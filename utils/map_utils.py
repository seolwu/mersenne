import os
from yaml import load, dump
from .config import MAP_FILE_PATH

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def open_map():
    with open(MAP_FILE_PATH, "r") as file:
        map_raw = file.read()
    return load(map_raw, Loader=Loader) or {}

def save_map(map_data):
    map_dump = dump(map_data, Dumper=Dumper)
    with open(MAP_FILE_PATH, "w") as file:
        file.write(map_dump)

def initialize_map_file():
    if not os.path.exists(MAP_FILE_PATH):
        initial_data = {}
        save_map(initial_data)
