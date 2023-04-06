# setup.py

from setuptools import setup, find_packages

setup(
    name='horizon_ai',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: TBD",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
