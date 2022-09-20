import json
import re
from pathlib import Path
from shlex import split as X
from subprocess import PIPE, run

import requests
from ocrd_utils import getLogger, pushd_popd
from ocrd_validators import OcrdToolValidator


class Repo():

    def __init__(self, config, url, official=False, compliant_cli=False):
        self.log = getLogger('quiver.repo')
        self.config = config
        self.path = Path(self.config['repodir'], Path(url).name)
        
        self.url = url
        self.id = str(Path(url).name)
        self.official = official
        self.compliant_cli = compliant_cli
        self.additional_info = self.make_additional_info()
        self.ocrd_tool_json_valid = self.validate_ocrd_tool_json()
        self.project_type = self.get_project_type()
        self.latest_version = self.get_latest_version()
        self.dependencies = self.get_dependencies()
        self.dependency_conflicts = self.get_dependency_conflicts()
        self.unreleased_changes = self.get_unreleased_changes()
        self.org_plus_name = '/'.join(self.url.split('/')[-2:])
        self.ocrd_tool = self.get_ocrd_tool()

    def __str__(self):
        return '<Repo %s @ %s>' % (self.url, self.path)

    def is_cloned(self):
        return self.path.is_dir()

    def pull(self):
        with pushd_popd(self.path):
            self._run('git pull origin master')

    def clone(self):
        if self.is_cloned():
            self.log.debug("Already cloned: %s" % self.path)
            return
        with pushd_popd(self.config['repodir']):
            self.log.debug("Cloning %s" % self.url)
            result = self._run('git clone --depth 1 "%s"' % self.url)
            self.log.debug("Result: %s" % result)

    def get_latest_version(self):
        with pushd_popd(self.path):
            return self._run('git describe --abbrev=0 --tags').stdout

    def make_additional_info(self):
        result = {}
        result['links'] = self.get_file_urls()
        #result['description'] = self.get_description()

        return result


    def get_file_urls(self):
        ret = {}
        self.log.info("%s  Getting file URLs" % self.url)
        with pushd_popd(self.path):
            for path in [Path(x) for x in ['ocrd-tool.json', 'Dockerfile', 'README.md', 'setup.py']]:
                if path.is_file():
                    ret[path.name] = self.url + '/blob/master/' + str(path)
                else:
                    ret[path.name] = None
        return ret

    def get_description(self):
        api_url = "https://api.github.com/repos/" + self.org_plus_name
        header = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(api_url, headers=header)
        response_json = json.loads(response.text)

        return response_json['description']

    def validate_ocrd_tool_json(self):
        valid = False
        tool = self.get_ocrd_tool()
        if tool:
            result = OcrdToolValidator.validate(tool)
            if 'OK' in str(result):
                valid = True
        return valid

    def get_project_type(self):
        with pushd_popd(self.path):
            type = 'python' if any(Path(x).is_file() for x in ['setup.py', 'requirements.txt', 'requirements_test.txt']) else 'bashlib'
        return type

    def get_dependencies(self):
        with open('data/deps.json', 'r', encoding='utf-8') as f:
            deps_file = json.load(f)

            return deps_file[self.id]


    def get_dependency_conflicts(self):
        with open('data/dep_conflicts.json', 'r', encoding='utf-8') as f:
            json_file = json.load(f)

            result = {}
            for pkg in json_file:
                if self.id in json_file[pkg]:
                    versions = json_file[pkg].values()
                    major_version_numbers = []
                    for v in versions:
                        major_version = re.findall(r'^(\d+)\.', v)[0]
                        major_version_numbers.append(int(major_version))
                    # eliminate duplicates
                    filtered = list(set(major_version_numbers))
                    if len(filtered) > 1:
                        result[pkg] = json_file[pkg]
            if result:
                return result

    def get_unreleased_changes(self):
        with pushd_popd(self.path):
            latest_tag = self._get_latest_tag()
            if latest_tag:
                latest_commit = self._get_latest_commit()
                cmd = 'git rev-list ' + latest_tag + '..' + latest_commit + ' --count'
                dist = self._run(cmd).stdout.strip()
                return int(dist)
            else:
                total_no_of_commits = self._run('git rev-list --count HEAD').stdout.strip()
                return int(total_no_of_commits)

    def get_ocrd_tool(self):
        result = None
        with pushd_popd(self.path):
            if Path('ocrd-tool.json').is_file():
                with open('ocrd-tool.json', 'r', encoding='utf-8') as f:
                    result = json.load(f)
        return result

    def _get_latest_tag(self):
        complete_refs = self._run('git show-ref --tag')
        formatted = complete_refs.stdout.strip()
        item_list = formatted.splitlines()
        if item_list:
            latest_release = item_list[-1]
            pattern = 'v?[0-9]+\.[0-9]+.*?$'
            match = re.findall(pattern, latest_release)
            return match[0]
        else:
            return None

    def _get_latest_commit(self):
        hash = self._run('git log -n 1 --pretty=format:"%H" HEAD')
        formatted = hash.stdout.strip()
        return formatted

    def to_json(self):
        desc = {}
        unwanted_attrs = ['log', 'path', 'config']
        for attr in vars(self):
            if attr not in unwanted_attrs:
                desc[attr] = getattr(self, attr)
        return desc

    def _run(self, cmd, **kwargs):
        result = run(X(cmd), stdout=PIPE, encoding='utf-8', **kwargs)
        if result.stdout:
            result.stdout = result.stdout.strip()
        return result
