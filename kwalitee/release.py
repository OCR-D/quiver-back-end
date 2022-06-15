import json, re
import requests

class Release():

    def __init__(self, json, released_projects_list):
        self.tag = json['tag_name']
        self.projects = self.__filter_projects(json, released_projects_list)

    def __str__(self):
        return f'<Release {self.tag}>'

    def to_json(self):
        desc = {}
        desc['tag'] = self.tag
        desc['projects'] = self.projects
        return desc

    def __filter_projects(self, json, released_projects_list):
        projects = self.__get_projects(json)
        filtered_projects = []
        for project in projects:
            if (project in released_projects_list):
                pass
            else:
                filtered_projects.append(project)
                released_projects_list.append(project)
        return filtered_projects

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
    released_projects = []
    for entry in response_json:
        release = Release(entry, released_projects)
        if release.projects:
            releases.append(release)
    return releases
