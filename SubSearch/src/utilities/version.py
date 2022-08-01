import json

from src.utilities import local_paths


def read_data(config_file: str):
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        version = data["version"]
        return version


def current():
    c_version = read_data(local_paths.root_directory("data", "version.json"))
    return c_version
