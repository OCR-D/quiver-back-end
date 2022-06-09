import pytest
from kwalitee import Release
import json

def get_json_data(array_pos):
    f = open('tests/assets/ocrd_all_releases.json')
    data = json.load(f)
    return data[array_pos]
    

def test_tag():
    first_release = get_json_data(0)
    release = Release(first_release)
    assert release.tag == "v2022-06-03"
