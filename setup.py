from setuptools import setup

try:
    with open("LICENSE.txt", "r") as f:
        _license = f.read()
except Exception:
    _license = ""


try:
    with open("README.md", "r") as f:
        _readme = f.read()
except Exception:
    _readme = ""


install_requires = ["requests", "urwid", "pycodestyle"]


setup(
    name="stocki",
    version="0.2.0",
    description="The CLI for fetching stock market data.",
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
