from jsonschema import validate
import json
import os
import sys


def load_json(filename):
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
        return data

def load_schema(filename):
    with open('schema/' + filename) as jsonfile:
        data = json.load(jsonfile)
        return data

file_to_validate = sys.argv[1]

if os.path.isfile(file_to_validate) == False:
    print(f"--- File not found: {file_to_validate}\n--- Usage: ./schema/validation.py FILENAME\n--- Example: ./schema/validation.py repos.json")
    raise Exception("File not found.")


schema = load_schema(file_to_validate)
instance = load_json(file_to_validate)

for object in instance:
    validate(instance=object, schema=schema)
