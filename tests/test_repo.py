from quiver.repo import Repo
from yaml import safe_load

def get_repos_list():
    config_file = 'quiver/config.yml'
    with open(config_file, 'r', encoding='utf-8') as f_config_file:
        config = safe_load(f_config_file.read())
        repos = []
        for repo_desc in config['repolist']:
            url = repo_desc['url']
            official = repo_desc.get('official', False)
            compliant_cli = repo_desc.get('compliant_cli', False)
            repos.append(Repo(config, url, official, compliant_cli))
    return repos


def get_repo(repos_list, repo_name):
    result = None
    for repo in repos_list:
        if repo.id == repo_name:
            result = repo
    return result


def test_additional_info_links():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken')
    repo_2 = get_repo(repos, 'ocrd_keraslm')

    # assertions as conditions
    # see https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest
    errors = []
    if not repo_1.additional_info['links']['Dockerfile'] == 'https://github.com/OCR-D/ocrd_kraken/blob/master/Dockerfile':
        errors.append('repo_1\'s Dockerfile URL is wrong.')
    if not repo_1.additional_info['links']['ocrd-tool.json'] == 'https://github.com/OCR-D/ocrd_kraken/blob/master/ocrd-tool.json':
        errors.append('repo_1\'s ocrd-tool.json URL is wrong.')
    if not repo_1.additional_info['links']['README.md'] == 'https://github.com/OCR-D/ocrd_kraken/blob/master/README.md':
        errors.append('repo_1\'s README URL is wrong.')
    if not repo_1.additional_info['links']['setup.py'] == 'https://github.com/OCR-D/ocrd_kraken/blob/master/setup.py':
        errors.append('repo_1\'s setup.py URL is wrong.')
    if not repo_2.additional_info['links']['Dockerfile'] == None:
        errors.append('repo_2\'s Dockerfile URL is not empty.')

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_ocrd_tool_validation():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken') # invalid ocrd-tool.json
    repo_2 = get_repo(repos, 'ocrd_keraslm') # valid ocrd-tool.json

    errors = []
    if not repo_1.ocrd_tool_json_valid == False:
        errors.append('repo_1\'s ocrd-tool.json must be invalid.')
    if not repo_2.ocrd_tool_json_valid == True:
        errors.append('repo_2\'s ocrd-tool.json must be valid.')

    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_python_or_bashlib():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken') # python
    repo_2 = get_repo(repos, 'ocrd_im6convert') # bashlib
    repo_3 = get_repo(repos, 'core') # python, but no setup.py

    errors = []
    if not repo_1.project_type == "python":
        errors.append(f'repo_1 is a python based project. current project type: {repo_1.project_type}.')
    if not repo_2.project_type == "bashlib":
        errors.append(f'repo_2 is a bashlib based project. current project type: {repo_2.project_type}.')
    if not repo_3.project_type == "python":
        errors.append(f'repo_3 is a python based project. current project type: {repo_3.project_type}.')

    assert not errors, "errors occured:\n{}".format("\n".join(errors))    

def test_unreleased_changes():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_segment') # this repo has no releases and 11 commits on master
    repo_2 = get_repo(repos, 'ocrd_typegroups_classifier') # this repo is up to date
    repo_3 = get_repo(repos, 'ocrd_ocropy') # this repo has 3 unreleased changes. it is archived, therefore save to test with.

    errors = []
    if not repo_1.unreleased_changes == 94:
        errors.append(f'repo_1 has 94 unreleased changes. current number: {repo_1.unreleased_changes}')
    if not repo_2.unreleased_changes == 0:
        errors.append(f'repo_2 has 0 unreleased changes. current number: {repo_2.unreleased_changes}')
    if not repo_3.unreleased_changes == 3:
        errors.append(f'repo_3 has 3 unreleased changes. current number: {repo_3.unreleased_changes}')

    assert not errors, "errors occured:\n{}".format("\n".join(errors))
    
def test_id():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken')
    assert repo_1.id == 'ocrd_kraken'

def test_latest_version():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken')
    assert repo_1.latest_version == 'v0.3.0'

def test_dependencies():
    repos = get_repos_list()
    repo = get_repo(repos, 'dinglehopper')
    assert list(repo.dependencies.keys()) == ['colorama', 'multimethod', 'rapidfuzz', 'uniseg']

def test_dependency_conflict_true():
    repos = get_repos_list()
    repo = get_repo(repos, 'ocrd_anybaseocr')
    assert list(repo.dependency_conflicts.keys()) == ['protobuf', 'torch']


def test_dependency_conflict_false():
    repos = get_repos_list()
    repo = get_repo(repos, 'ocrd_typegroups_classifier')
    repo.dependency_conflicts = None

def test_ocrd_tool():
    repos = get_repos_list()
    repo = get_repo(repos, 'ocrd_olahd_client')
    assert repo.ocrd_tool['git_url'] == 'https://github.com/OCR-D/ocrd_olahd_client'
    