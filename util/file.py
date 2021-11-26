import os
import json


def load_json_file(path):
    """读取json文件"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"field {path} not find!")

    with open(path, "r") as f:
        config = json.load(f)
    return config
