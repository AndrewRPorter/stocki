import sys
from setuptools import setup


try:
    with open('LICENSE.txt', 'r') as f:
        _license = f.read()
except Exception as e:
    _license = ''


try:
    with open('README.md', 'r') as f:
        _readme = f.read()
except Exception as e:
    _readme = ''


install_requires = ["requests", "urwid", "pycodestyle"]


setup(
    name="stocki",
    version="v0.1.2",
    description='The CLI for fetching stock market data.',
    long_description=_readme,
    license=_license,
    install_requires=install_requires,
    packages=["stocki"],
    entry_points={"console_scripts": ["stocki = stocki.stocki:main"]},
    include_package_data=True,
    python_requires=">=2.7",
    url="https://github.com/andrewrporter/stocki",
    author="AndrewRPorter",
    author_email="porter.r.andrew@gmail.com",
)
