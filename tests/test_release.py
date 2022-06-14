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
    assert release.tag == 'v2022-06-03'

def test_released_projects():
    first_release = get_json_data(0)
    release = Release(first_release)
    assert release.projects == ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']

def test_json_output():
    first_release = get_json_data(0)
    release = Release(first_release)
    test_representation = {}
    test_representation['tag'] = 'v2022-06-03'
    test_representation['projects'] = ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']
    json_representation = release.to_json()
    assert json_representation == test_representation

def test_string_representation():
    first_release = get_json_data(0)
    release = Release(first_release)
    assert str(release) == '<Release v2022-06-03>'

def test_filter_projects():
    first_release = get_json_data(0)
    current_release_entry = Release(first_release)
    second_release = get_json_data(1)
    older_release_entry = Release(second_release)

    older_release_entry.filter_projects()
    assert older_release_entry.projects == ['eynollah', 'ocrd_cis', 'ocrd_doxa', 'ocrd_fileformat', 'sbb_binarization']
