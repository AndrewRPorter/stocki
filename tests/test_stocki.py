import os
import subprocess
from unittest import TestCase
from unittest import main as test_main

import pycodestyle

VERSION = "0.2.0"


class TestStocki(TestCase):
    @classmethod
    def setUp(cls):
        cls.ticker = "AAPL"

    def test_style(self):
        ignore = []
        file_list = []

        for root, _, files in os.walk("./"):
            for f in files:
                if f.endswith(".py"):
                    f = os.path.join(root, f)
                    if f in ignore:
                        continue
                    file_list.append(f)

        style = pycodestyle.StyleGuide({"ignore": "E501"})
        result = style.check_files(file_list)
        self.assertEqual(result.total_errors, 0, "Found code style errors (and warnings).")


if __name__ == "__main__":
    test_main()
