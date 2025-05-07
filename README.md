# oi-cli

[![PyPI](https://img.shields.io/pypi/v/oi-cli.svg)](https://pypi.org/project/oi-cli/)
[![Changelog](https://img.shields.io/github/v/release/brrttwrks/oi-cli?include_prereleases&label=changelog)](https://github.com/brrttwrks/oi-cli/releases)
[![Tests](https://github.com/brrttwrks/oi-cli/actions/workflows/test.yml/badge.svg)](https://github.com/brrttwrks/oi-cli/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/brrttwrks/oi-cli/blob/master/LICENSE)

A simple CLI for searching using the OSINT Industries API

## Installation

Install this tool using `pip`:
```bash
pip install oi-cli
```
## Usage

For help, run:
```bash
oi-cli --help
```
You can also use:
```bash
python -m oi_cli --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd oi-cli
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
