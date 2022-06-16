import json, re
import requests

class Release():

    def __init__(self, json):
        self.tag = json['tag_name']
        self.projects = self.__get_projects(json)

    def __str__(self):
        return f'<Release {self.tag}>'

    def to_json(self):
        desc = {}
        desc['tag'] = self.tag
        desc['projects'] = self.projects
        return desc

    def __get_projects(self, json_data):
        markdown_desc = json_data['body']
        pattern = r'### \[(.*?)\]'
        return re.findall(pattern, markdown_desc)


def get_releases(test_mode=False):
    if test_mode:
        f = open('tests/assets/ocrd_all_releases.json')
        response_json = json.load(f)
    else:
        api_url = "https://api.github.com/repos/OCR-D/ocrd_all/releases"
        header = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(api_url, headers=header)
        response_json = json.loads(response.text)
    
    releases = []
    for entry in response_json:
        release = Release(entry)
        if release.projects:
            releases.append(release)
    return releases
