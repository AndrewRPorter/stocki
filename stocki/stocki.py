# coding: utf-8
import sys
import urwid
import requests
import argparse
from urwid.widget import BOX, FLOW, FIXED


VERSION = "0.1.3"


SCROLL_LINE_UP = "line up"
SCROLL_LINE_DOWN = "line down"
SCROLL_PAGE_UP = "page up"
SCROLL_PAGE_DOWN = "page down"
SCROLL_TO_TOP = "to top"
SCROLL_TO_END = "to end"


YELLOW = '\033[33m'
RED = "\033[31m"
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = "\033[0m"


class Scrollable(urwid.WidgetDecoration):
    def sizing(self):
        return frozenset([BOX])

    def selectable(self):
        return True

    def __init__(self, widget):
        """Box widget that makes a fixed or flow widget vertically scrollable.

        Note:
            This code is based off of code from:
                https://github.com/rndusr/stig/blob/master/stig/tui/scroll.py
        """

        self._trim_top = 0
        self._scroll_action = None
        self._forward_keypress = None
        self._old_cursor_coords = None
        self._rows_max_cached = 0
        self.__super.__init__(widget)

    def render(self, size, focus=False):
        maxcol, maxrow = size
        # Render complete original widget
        ow = self._original_widget
        ow_size = self._get_original_widget_size(size)
        canv = urwid.CompositeCanvas(ow.render(ow_size, focus))
        canv_cols, canv_rows = canv.cols(), canv.rows()

        if canv_cols <= maxcol:
            pad_width = maxcol - canv_cols
            if pad_width > 0:
                canv.pad_trim_left_right(0, pad_width)

        if canv_rows <= maxrow:
            fill_height = maxrow - canv_rows
            if fill_height > 0:
                canv.pad_trim_top_bottom(0, fill_height)

        if canv_cols <= maxcol and canv_rows <= maxrow:
            return canv

        self._adjust_trim_top(canv, size)

        # Trim canvas if necessary
        trim_top = self._trim_top
        trim_end = canv_rows - maxrow - trim_top
        trim_right = canv_cols - maxcol
        if trim_top > 0:
            canv.trim(trim_top)
        if trim_end > 0:
            canv.trim_end(trim_end)
        if trim_right > 0:
            canv.pad_trim_left_right(0, -trim_right)

        # Disable cursor display if cursor is outside of visible canvas parts
        if canv.cursor is not None:
            curscol, cursrow = canv.cursor
            if cursrow >= maxrow or cursrow < 0:
                canv.cursor = None

        # Let keypress() know if original_widget should get keys
        self._forward_keypress = bool(canv.cursor)

        return canv

    def keypress(self, size, key):
        if self._forward_keypress:
            ow = self._original_widget
            ow_size = self._get_original_widget_size(size)

            # Remember previous cursor position if possible
            if hasattr(ow, "get_cursor_coords"):
                self._old_cursor_coords = ow.get_cursor_coords(ow_size)

            key = ow.keypress(ow_size, key)
            if key is None:
                return None

        # Handle up/down, page up/down, etc
        command_map = self._command_map
        if command_map[key] == urwid.CURSOR_UP:
            self._scroll_action = SCROLL_LINE_UP
        elif command_map[key] == urwid.CURSOR_DOWN:
            self._scroll_action = SCROLL_LINE_DOWN
        elif command_map[key] == urwid.CURSOR_PAGE_UP:
            self._scroll_action = SCROLL_PAGE_UP
        elif command_map[key] == urwid.CURSOR_PAGE_DOWN:
            self._scroll_action = SCROLL_PAGE_DOWN
        elif command_map[key] == urwid.CURSOR_MAX_LEFT:
            self._scroll_action = SCROLL_TO_TOP
        elif command_map[key] == urwid.CURSOR_MAX_RIGHT:
            self._scroll_action = SCROLL_TO_END
        else:
            return key

        self._invalidate()

    def mouse_event(self, size, event, button, col, row, focus):
        if button == 5:
            self._scroll_action = SCROLL_LINE_DOWN
        elif button == 4:
            self._scroll_action = SCROLL_LINE_UP

        self._invalidate()
        ow = self._original_widget
        if hasattr(ow, "mouse_event"):
            ow_size = self._get_original_widget_size(size)
            row += self._trim_top
            return ow.mouse_event(ow_size, event, button, col, row, focus)
        else:
            return False

    def _adjust_trim_top(self, canv, size):
        action = self._scroll_action
        self._scroll_action = None

        maxcol, maxrow = size
        trim_top = self._trim_top
        canv_rows = canv.rows()

        if trim_top < 0:
            # Negative trim_top values use bottom of canvas as reference
            trim_top = canv_rows - maxrow + trim_top + 1

        if canv_rows <= maxrow:
            self._trim_top = 0  # Reset scroll position
            return

        def ensure_bounds(new_trim_top):
            return max(0, min(canv_rows - maxrow, new_trim_top))

        if action == SCROLL_LINE_UP:
            self._trim_top = ensure_bounds(trim_top - 1)
        elif action == SCROLL_LINE_DOWN:
            self._trim_top = ensure_bounds(trim_top + 1)
        elif action == SCROLL_PAGE_UP:
            self._trim_top = ensure_bounds(trim_top - maxrow+1)
        elif action == SCROLL_PAGE_DOWN:
            self._trim_top = ensure_bounds(trim_top + maxrow-1)
        elif action == SCROLL_TO_TOP:
            self._trim_top = 0
        elif action == SCROLL_TO_END:
            self._trim_top = canv_rows - maxrow
        else:
            self._trim_top = ensure_bounds(trim_top)

        if self._old_cursor_coords is not None and self._old_cursor_coords != canv.cursor:
            self._old_cursor_coords = None
            curscol, cursrow = canv.cursor
            if cursrow < self._trim_top:
                self._trim_top = cursrow
            elif cursrow >= self._trim_top + maxrow:
                self._trim_top = max(0, cursrow - maxrow + 1)

    def _get_original_widget_size(self, size):
        ow = self._original_widget
        sizing = ow.sizing()
        if FIXED in sizing:
            return ()
        elif FLOW in sizing:
            return (size[0],)

    def get_scrollpos(self, size=None, focus=False):
        return self._trim_top

    def set_scrollpos(self, position):
        self._trim_top = int(position)
        self._invalidate()

    def rows_max(self, size=None, focus=False):
        if size is not None:
            ow = self._original_widget
            ow_size = self._get_original_widget_size(size)
            sizing = ow.sizing()
            if FIXED in sizing:
                self._rows_max_cached = ow.pack(ow_size, focus)[1]
            elif FLOW in sizing:
                self._rows_max_cached = ow.rows(ow_size, focus)
            else:
                raise RuntimeError("Not a flow/box widget: %r" %
                                   self._original_widget)
        return self._rows_max_cached


class App():
    def __init__(self, content):
        self._palette = [
            ("menu", "black", "light gray", "standout"),
            ("title", "default,bold", "default", "bold")
        ]

        menu = urwid.Text([u'\n', ("menu", u" Q "), ("light gray", u" Quit")])
        layout = urwid.Frame(body=content, footer=menu)

        main_loop = urwid.MainLoop(layout, self._palette,
                                   unhandled_input=self._handle_input)
        main_loop.run()

    def _handle_input(self, input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()


def load(ticker):
    base_url = 'https://api.iextrading.com/1.0/stock'
    ticker = ticker.upper()

    try:
        r_quote = requests.get("{}/{}/quote".format(base_url, ticker))
        r_info = requests.get("{}/{}/company".format(base_url, ticker))

        data = r_quote.json()
        data.update(r_info.json())

        pile = urwid.Pile([
            urwid.Text("STOCKI: The CLI Interface for fetching stock market data\n", align="center"),
            urwid.Text(("title", "{} OVERVIEW".format(ticker))),
            urwid.Padding(urwid.Text("Price: {}".format(data["latestPrice"])), left=5),
            urwid.Padding(urwid.Text("Change: {} ({:.2f}%)".format(data["change"], (data["changePercent"]))), left=5),
            urwid.Padding(urwid.Text("Volume: {}".format(data["latestVolume"])), left=5),
            urwid.Padding(urwid.Text("Market Cap: {}".format(data["marketCap"])), left=5),
            urwid.Padding(urwid.Text("52 Week Range: {} - {}".format(data["week52Low"], data["week52High"])), left=5),
            urwid.Padding(urwid.Text("YTD Change: {:.2f}%\n".format(float(data["ytdChange"]))), left=5),
            urwid.Text(("title", "COMPANY INFO")),
            urwid.Padding(urwid.Text("Name: {}".format(data["companyName"])), left=5),
            urwid.Padding(urwid.Text("Industry: {}".format(data["industry"])), left=5),
            urwid.Padding(urwid.Text("Sector: {}".format(data["sector"])), left=5),
            urwid.Padding(urwid.Text("Website: {}".format(data["website"])), left=5),
            urwid.Padding(urwid.Text("CEO: {}\n".format(data["CEO"])), left=5),
            urwid.Text(("title", "DESCRIPTION")),
            urwid.Padding(urwid.Text(data["description"]), left=5),
        ])

        padding = urwid.Padding(Scrollable(pile), left=1, right=1)

        return padding
    except Exception as e:
        return None


def help():
    print(''.join([BOLD, "stocki {} – Made by @andrewrporter".format(VERSION), END, "\n"]))
    print("The CLI for fetching stock market data.\n")
    print(''.join([UNDERLINE, "Usage", END, ":", " $ stocki ", YELLOW, "[ticker]", YELLOW, " [-v/--version]", YELLOW, " [-h/--help]", END]))


def version():
    print("stocki {}".format(VERSION))


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("ticker", type=str, nargs='?')
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.ticker:
        content = load(args.ticker)

        if content:
            App(content)
        else:
            print(''.join([RED, "stocki doesn't recognize: '{}'".format(args.ticker), END]))
    elif args.version:
        version()
    elif args.help:
        help()
    else:
        help()
