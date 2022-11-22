#!/usr/bin/env python

import json
from os import getcwd, listdir, remove
from pathlib import Path


def get_json_files():
    json_loc = getcwd() + '/workflows/results/'
    file_list = [ json_loc + x for x in listdir(json_loc) if x.endswith("json") ]
    return file_list

def summarize_to_one_file(json_files):
    result = []
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            result.append(data)
    output_path = getcwd() + '/data/workflows.json'
    json_str = json.dumps(result, indent=4)
    Path(output_path).write_text(json_str, encoding='utf-8')

def delete_old_jsons(json_files):
    for file in json_files:
        remove(file)


if __name__ == '__main__':
    json_files = get_json_files()
    summarize_to_one_file(json_files)
    delete_old_jsons(json_files)

    print("Successfully summarized JSON files!")
    