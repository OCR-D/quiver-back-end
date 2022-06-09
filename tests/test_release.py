import pytest
from kwalitee import Release
import json

def test_tag():
    f = open('tests/assets/ocrd_all_releases.json')
    data = json.load(f)
    first_release = data[0]
    release = Release(first_release)
    assert release.tag == "v2022-06-03"
