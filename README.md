# oi-cli

A simple CLI for searching using the OSINT Industries API

## Installation

Using [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/brrttwrks/oi-cli.git
cd oi-cli/
uv pip install -e .
```

## Usage

Currently, the input argument must be a CSV file with a column name according to the type of API search you are executing. There are currently several types:

- email
- phone
- username
- name
- wallet

```
Usage: oi-cli search [OPTIONS] [FILE]

  Basic search

Options:
  -t, --type TEXT          Type of search: email, phone, username, name,
                           wallet  [required]
  -n, --name TEXT          Name of search query. If restarted, will check
                           cache to skip successful queries.  [required]
  -o, --output TEXT        Output path of report CSV file
  -p, --processes INTEGER
  --help                   Show this message and exit.
```
