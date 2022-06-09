import pytest
from kwalitee import Release

def test_tag():
    release = Release()
    assert release.tag == "v2022-01-01"