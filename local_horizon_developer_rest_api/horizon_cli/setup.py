import click
from setuptools import setup, find_packages

setup(
    name="horizon-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "horizon=horizon_cli.cli:cli",
        ]
    },


)
