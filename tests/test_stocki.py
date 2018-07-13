import sys
import requests

if sys.version_info < (2.7):
    from unittest2 import main as test_main, TestCase
else:
    from unittest import main as test_main, TestCase

class TestStocki(TestCase):
    def setUp(self):
        self.base_url = 'https://api.iextrading.com/1.0/stock'

    def test_valid_tickers(self):
        valid_tickers = ["AAPL", "BAC", "F", "BRK.A"]

        for ticker in valid_tickers:
            r_quote = requests.get("{}/{}/quote".format(self.base_url, ticker))
            r_info = requests.get("{}/{}/company".format(self.base_url, ticker))

            data = r_quote.json()
            data.update(r_info.json())

            self.assertNotEqual(data, None)
            self.assertNotEqual(data, {})

    def test_invalid_tickers(self):
        invalid_tickers = ["", "ABCDEFGH", "/"]

        for ticker in invalid_tickers:
            r_quote = requests.get("{}/{}/quote".format(self.base_url, ticker))
            r_info = requests.get("{}/{}/company".format(self.base_url, ticker))

            with self.assertRaises(ValueError):
                data = r_quote.json()
                data.update(r_info.json())

if __name__ == "__main__":
    test_main()
