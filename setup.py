from setuptools import setup

try:
    with open('LICENSE.txt', 'r') as f:
        _license = f.read()
except:
    _license = ''

try:
    with open('README.md', 'r') as f:
        _readme = f.read()
except:
    _readme = ''

setup(
    name="stocki",
    description="CLI interface for fetching stock market data",
    version="v0.0.1",
    install_requires=["requests", "urwid"],
    packages=["stocki"],
    entry_points={"console_scripts": ["stocki = stocki.stocki:main"]},
    include_package_data=True,
    python_requires=">=3",
    url="https://github.com/andrewrporter/stocki",
    author="AndrewRPorter",
    author_email="porter.r.andrew@gmail.com",
    license="MIT"
)
