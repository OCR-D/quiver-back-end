from kwalitee.release import get_releases
from kwalitee import Release
import json


def get_json_data(array_pos):
    f = open('tests/assets/ocrd_all_releases.json')
    data = json.load(f)
    return data[array_pos]


def test_tag():
    json = get_json_data(0)
    release = Release(json)
    assert release.tag == 'v2022-06-03'


def test_released_projects():
    json = get_json_data(0)
    release = Release(json)
    assert release.projects == ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']


def test_json_output():
    json = get_json_data(0)
    release = Release(json)
    test_representation = {}
    test_representation['tag'] = 'v2022-06-03'
    test_representation['projects'] = ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']
    json_representation = release.to_json()
    assert json_representation == test_representation


def test_string_representation():
    json = get_json_data(0)
    release = Release(json)
    assert str(release) == '<Release v2022-06-03>'
