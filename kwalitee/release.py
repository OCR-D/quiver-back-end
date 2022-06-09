import json, re
import requests
from ocrd_utils import getLogger

class Release():

    def __init__(self, json_data):
        self.tag = json_data['tag_name']
        self.projects = self.get_projects(json_data)

    def __str__(self):
        return f'<Release {self.tag}>'

    def get_projects(self, json_data):
        markdown_desc = json_data['body']
        pattern = r'### \[(.*?)\]'
        return re.findall(pattern, markdown_desc)

    def to_json(self):
        desc = {}
        desc['tag'] = self.tag
        desc['projects'] = self.projects
        return desc

def get_releases():
    api_url = "https://api.github.com/repos/OCR-D/ocrd_all/releases"
    header = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(api_url, headers=header)
    response_json = json.loads(response.text)
    
    releases = []
    for entry in response_json:
        releases.append(Release(entry))
    return releases