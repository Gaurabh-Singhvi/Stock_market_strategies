from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stock_market_strategies",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for analyzing stock market data and implementing trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock_market_strategies",
    packages=find_packages(include=['src', 'src.*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.0.0",
        "pyyaml>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "stock_market_strategies=src.main:main",
        ],
    },
)
