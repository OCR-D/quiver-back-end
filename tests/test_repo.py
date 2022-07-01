from kwalitee.repo import Repo
from yaml import safe_load

def get_repos_list():
    config_file = 'kwalitee/config.yml'
    with open(config_file, 'r') as f_config_file:
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


#def test_additional_info_desc():
#    repos = get_repos_list()
#    repo_1 = get_repo(repos, 'ocrd_kraken')
#
#    assert repo_1.additional_info['description'] == 'Wrapper for the kraken OCR engine'


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

def test_id():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken')
    assert repo_1.id == 'ocrd_kraken'

def test_latest_version():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_kraken')
    assert repo_1.latest_version == 'v0.1.2'

def test_dependencies():
    repos = get_repos_list()
    repo_1 = get_repo(repos, 'ocrd_typegroups_classifier')
    assert repo_1.dependencies == {"imageio": "2.19.3", "networkx": "2.6.3", "packaging": "21.3", "pandas": "1.3.5", "pyparsing": "3.0.9", "python-dateutil": "2.8.2", "pytz": "2022.1", "PyWavelets": "1.3.0", "scikit-image": "0.19.3", "scipy": "1.7.3", "six": "1.16.0", "tifffile": "2021.11.2", "torch": "1.12.0", "torchvision": "0.13.0"}

def test_dependency_conflict_true():
    repos = get_repos_list()
    repo = get_repo(repos, 'cor-asv-ann')
    assert repo.dependency_conflicts == {"h5py": { "2.10.0": "cor-asv-ann", "3.1.0": "ocrd_pc_segmentation", "3.7.0": "eynollah"}, "protobuf": {"3.19.4": "eynollah","4.21.2": "cor-asv-ann"}, "tensorboard": {"1.15.0": "cor-asv-ann","2.9.1": "eynollah"}, "tensorflow-estimator": {"1.15.1": "cor-asv-ann","2.5.0": "ocrd_pc_segmentation","2.9.0": "eynollah"}}


def test_dependency_conflict_false():
    repos = get_repos_list()
    repo = get_repo(repos, 'ocrd_typegroups_classifier')
    repo.dependency_conflicts = None