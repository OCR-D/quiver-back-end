import json
from pathlib import Path
from subprocess import run, PIPE
from shlex import split as X
from ocrd_utils import pushd_popd, getLogger
import requests

class Repo():

    def __init__(self, config, url, official=False, compliant_cli=False):
        self.log = getLogger('kwalitee.repo')
        self.url = url
        self.config = config
        self.id = str(Path(url).name)
        self.official = official
        self.compliant_cli = compliant_cli
        self.path = Path(self.config['repodir'], Path(url).name)
        self.additional_info = self.make_additional_info()
        self.file_urls = self.get_file_urls()
        self.ocrd_tool_json_valid = self.validate_ocrd_tool_json()
        self.project_type = self.get_project_type()
        self.latest_version = self.get_latest_version()

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
        with pushd_popd(self.path):
            if Path('ocrd-tool.json').is_file():
                result = self._run('ocrd ocrd-tool ocrd-tool.json validate').stdout
                if 'valid="true"' in result:
                    valid = True
        return valid

    def get_project_type(self):
        type = 'bashlib'
        with pushd_popd(self.path):
            for path in [Path(x) for x in ['setup.py', 'requirements.txt', 'requirements_test.txt']]:
                if path.is_file():
                    type = 'python'
        return type

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
