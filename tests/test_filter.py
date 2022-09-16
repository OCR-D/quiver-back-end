from quiver.release import get_releases
from quiver.filter import filter_release_projects

def test_filter():
    releases = get_releases(test_mode=True)
    filtered = filter_release_projects(releases)
    release = filtered[1]
    assert release['projects'] == ['eynollah', 'ocrd_cis', 'ocrd_doxa', 'ocrd_fileformat', 'sbb_binarization']

def test_ignore_releases_without_project_after_filtering():
    releases = get_releases(test_mode=True)
    filtered = filter_release_projects(releases)
    is_tag_in_list = False
    for entry in filtered:
        # an example of an empty release (i.e. one without projects) after filtering is v2022-02-03
        if entry['tag'] == 'v2022-02-03':
            is_tag_in_list = True
    assert not is_tag_in_list
