import requests
from .settings import *
import json
import csv
from datetime import datetime
from .log import log

def get_credits():
    url = "https://api.osint.industries/misc/credits"
    headers = {
        "api-key": OI_CLI_API_KEY,
        "accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    return response.json()

def clean_name(name: str) -> str:
    n = name.lower()
    n = n.replace(" ", "_")
    return n

def search_query(search_type: str, search_value: str):
    url = f"https://api.osint.industries/v2/request"
    headers = {
        "api-key": OI_CLI_API_KEY,
        "accept": "application/json",
    }
    params = {
        "type": search_type,
        "query": search_value,
        "timeout": 60
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def cache_query(search_key: str, name: str):
    cache_path = OI_CLI_DIR / name
    with open(cache_path, "a") as f:
        f.write(f"{search_key}\n")

def get_cache(name: str) -> set:
    cache = set()
    cache_path = OI_CLI_DIR / name
    cache_path.touch()
    with open(cache_path, "r") as f:
        for line in f:
            cache.add(line.strip())
    return cache

def store_results(name: str, search_key: str, results: list) -> Path:
    file_path = OI_CLI_DIR / f"{name}.json"
    with open(file_path, "a") as f:
        for result in results:
            if isinstance(result, str):
                continue
            result["search_key"] = search_key
            result["search_date"] = datetime.now().strftime("%Y-%m-%d")
            f.write(f"{json.dumps(result)}\n")

def get_headers(response_list: list) -> list:
    headers = set()
    for response in response_list:
        for key in response.keys():
            headers.add(key)
    headers = list(headers)
    for idx, col in enumerate(["search_key", "search_date", "module"]):
        el_idx = headers.index(col)
        el = headers.pop(el_idx)
        headers.insert(idx, el)
    return headers

def export_csv(name, output_path):
    results_path = OI_CLI_DIR / f"{name}.json"
    with (
        open(results_path, "r") as ifile,
        open(output_path, "a") as ofile,
    ):

        responses = []
        for line in ifile:
            parsed_response = {}
            data = json.loads(line)
            module_name = data.get("module")
            spec_format = data.get("spec_format")

            parsed_response["search_key"] = data.get("search_key")
            parsed_response["search_date"] = data.get("search_date")
            parsed_response["module"] = module_name

            if spec_format is not None:
                for sf_item  in spec_format:
                    for k, v in sf_item.items():
                        if k == "platform_variables":
                            for pv_item in v:
                                if pv_item["type"] in ["str", "int", "float"]:
                                    parsed_response[pv_item["proper_key"]] = pv_item["value"]
                        else:
                            parsed_response[v["proper_key"]] = v["value"]

            responses.append(parsed_response)

        writer = csv.DictWriter(ofile, fieldnames=get_headers(responses))
        writer.writeheader()
        writer.writerows(responses)
