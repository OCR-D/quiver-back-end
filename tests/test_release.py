from kwalitee.release import get_releases
from kwalitee import Release
import json


def get_json_data(array_pos):
    f = open('tests/assets/ocrd_all_releases.json')
    data = json.load(f)
    return data[array_pos]


def test_tag():
    json = get_json_data(0)
    released_projects = []
    release = Release(json, released_projects)
    assert release.tag == 'v2022-06-03'


def test_released_projects():
    json = get_json_data(0)
    released_projects = []
    release = Release(json, released_projects)
    assert release.projects == ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']


def test_json_output():
    json = get_json_data(0)
    released_projects = []
    release = Release(json, released_projects)
    test_representation = {}
    test_representation['tag'] = 'v2022-06-03'
    test_representation['projects'] = ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']
    json_representation = release.to_json()
    assert json_representation == test_representation


def test_string_representation():
    json = get_json_data(0)
    released_projects = []
    release = Release(json, released_projects)
    assert str(release) == '<Release v2022-06-03>'


def test_filter_projects():
    json = get_json_data(0)
    released_projects = ['core', 'ocrd_detectron2', 'ocrd_keraslm', 'eynollah', 'ocrd_cis', 'ocrd_doxa']
    release = Release(json, released_projects)
    assert release.projects == ['ocrd_olena', 'ocrd_segment', 'opencv-python', 'workflow-configuration']


def test_ignore_releases_without_project_after_filtering():
    releases = get_releases(test_mode=True)
    ret = []
    for release in releases:
        ret.append(release.to_json())
    is_tag_in_list = False
    for entry in ret:
        # an example of an empty release (i.e. one without projects) after filtering is v2022-02-03
        if entry['tag'] == 'v2022-02-03':
            is_tag_in_list = True
    assert not is_tag_in_list
