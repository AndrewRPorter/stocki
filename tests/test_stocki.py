import os
import requests
import subprocess
import pycodestyle

from unittest import main as test_main, TestCase


VERSION = "0.1.3"


class TestStocki(TestCase):
    @classmethod
    def setUp(cls):
        cls.url = 'https://api.iextrading.com/1.0/stock'

    def test_valid_tickers(self):
        valid_tickers = ["AAPL", "BAC", "F", "BRK.A"]

        for ticker in valid_tickers:
            r_quote = requests.get("{}/{}/quote".format(self.url, ticker))
            r_info = requests.get("{}/{}/company".format(self.url, ticker))

            data = r_quote.json()
            data.update(r_info.json())

            self.assertNotEqual(data, None)
            self.assertNotEqual(data, {})

    def test_invalid_tickers(self):
        invalid_tickers = ["ABCDEFGH", "/"]

        for ticker in invalid_tickers:
            r_quote = requests.get("{}/{}/quote".format(self.url, ticker))
            r_info = requests.get("{}/{}/company".format(self.url, ticker))

            with self.assertRaises(ValueError):
                data = r_quote.json()
                data.update(r_info.json())

    def test_version(self):
        call = subprocess.check_output("python stocki/__main__.py -v".split())
        call = call.decode("utf-8")
        self.assertEqual(str(call).strip(), "stocki {}".format(VERSION))

    def test_style(self):
        ignore = []
        file_list = []

        for root, dirs, files in os.walk("./"):
            for f in files:
                if f.endswith(".py"):
                    f = os.path.join(root, f)
                    if f in ignore:
                        continue
                    file_list.append(f)

        style = pycodestyle.StyleGuide({"ignore":"E501"})
        result = style.check_files(file_list)
        self.assertEqual(result.total_errors, 0,
            "Found code style errors (and warnings).")


if __name__ == "__main__":
    test_main()
