import click
from click import ClickException
import sys
import csv
from pathlib import Path
from .api import (
    search_query,
    cache_query,
    get_cache,
    store_results,
    export_csv,
    get_credits,
)
from .log import log
import multiprocessing as mp

def clean_name(name: str) -> str:
    """Clean report name"""
    n = name.lower()
    n = n.replace(" ", "_")
    return n

@click.group()
@click.version_option()
def cli():
    "A simple CLI for searching using the OSINT Industries API"

@cli.command(name="credits")
def credits_command():
    credits = get_credits()
    click.echo(credits)

@cli.command(name="search")
@click.option(
    "-t",
    "--type",
    required=True,
    type=str,
    help="Type of search: email, phone, username, name, wallet",
)
@click.option(
    "-n",
    "--name",
    required=True,
    type=str,
    help="Name of search query. If restarted, will check cache to skip successful queries."
)
@click.option(
    "-o",
    "--output",
    required=False,
    type=str,
    help="Output path of report CSV file",
)
@click.argument("file", type=click.File("r"), default=sys.stdin)
def search_command(type, name, output, file):
    "A basic search"

    name = clean_name(name)
    if output is None:
        output_path = Path(f"{name}.json")
    else:
        output_path = Path(output)
        if output_path.is_dir():
            raise click.BadOptionUsage("output", "Output must be a file, not a directory.")

    cache = get_cache(name)
    for row in csv.DictReader(file):
        val = row.get(type)
        search_key = f"{type}|{val}"
        if val is not None or len(val.strip()) > 0:
            if search_key not in cache:
                log.info(f"Searching type {type}: {val} ...")
                results = search_query(type, val)
                if results is None:
                    log.info(f"No results: {search_key}")
                    continue

                store_results(name, search_key, results)
                cache_query(search_key, name)
            else:
                log.info(f"Already queried: {search_key}. Skipping.")
    export_csv(name, output_path)
