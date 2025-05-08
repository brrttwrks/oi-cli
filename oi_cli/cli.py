import click
from click import ClickException
import sys
import csv
from pathlib import Path
from .api import (
    clean_name,
    search_query,
    cache_query,
    get_cache,
    store_results,
    export_csv,
    get_credits,
)
from .log import log
import threading
from queue import Queue

worker_count = 1

def result_queue_writer(result_queue):
    log.info(f"Starting {threading.current_thread().name}")
    sentinel_count = 0
    while True:
        result = result_queue.get()

        if result == "EOL":
            sentinel_count += 1

        if sentinel_count == worker_count:
            log.info(f"Stopping {threading.current_thread().name}")
            break

        name, search_key, results = result
        store_results(name, search_key, results)

def cache_queue_writer(cache_queue):
    log.info(f"Starting {threading.current_thread().name}")
    sentinel_count = 0
    while True:
        cache = cache_queue.get()

        if cache == "EOL":
            sentinel_count += 1

        if sentinel_count == worker_count:
            log.info(f"Stopping {threading.current_thread().name}")
            break

        search_key, name = cache
        cache_query(search_key, name)

def worker(search_queue, result_queue, cache_queue):
    log.info(f"Starting {threading.current_thread().name}")
    while True:
        search = search_queue.get()

        if search == "EOL":
            log.info(f"Stopping {threading.current_thread().name}")
            result_queue.put("EOL")
            cache_queue.put("EOL")
            break
        
        name, type_, value, output_path = search
        search_key = f"{type_}|{value}"

        log.info(f"Searching type {type_}: {value}")

        results = search_query(type_, value)
        if results is None:
            log.info(f"No results: {search_key}")
            continue

        result_queue.put((name, search_key, results))
        cache_queue.put((search_key, name))


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
    "type_",
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
@click.option(
    "-p",
    "--processes",
    "process",
    required=False,
    type=int,
    default=1,
)
@click.argument("file", type=click.File("r"), default=sys.stdin)
def search_command(type_, name, output, process, file):
    "A basic search"

    name = clean_name(name)
    if output is None:
        output_path = Path(f"{name}.csv")
    else:
        output_path = Path(output)
        if output_path.is_dir():
            raise click.BadOptionUsage("output", "Output must be a file, not a directory.")

    global worker_count
    worker_count = process

    cached = get_cache(name)
    search_queue = Queue()

    for row in csv.DictReader(file):
        val = row.get(type_)
        search_key = f"{type_}|{val}"
        if val is not None or len(val.strip()) > 0:
            if search_key not in cached:
                search_queue.put((name, type_, val, output_path))
    [search_queue.put("EOL") for w in range(worker_count)] # sentinels

    result_queue = Queue()
    cache_queue = Queue()

    result_thread = threading.Thread(
        name = f"result_writer",
        target = result_queue_writer,
        args = (result_queue,),
    )
    result_thread.start()

    cache_thread = threading.Thread(
        name = f"cache_writer",
        target = cache_queue_writer,
        args = (cache_queue,),
    )
    cache_thread.start()

    workers = []
    for w in range(worker_count):
        t = threading.Thread(
            name = f"worker_{w+1}",
            target = worker,
            args = (search_queue, result_queue, cache_queue,),
        )
        workers.append(t)

    [w.start() for w in workers]
    [w.join() for w in workers]

    result_thread.join()
    cache_thread.join()

    export_csv(name, output_path)
