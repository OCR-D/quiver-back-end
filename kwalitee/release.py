import json, re
from ocrd_utils import getLogger

class Release():

    def __init__(self, json_data):
        self.tag = json_data['tag_name']
        self.projects = self.get_projects(json_data)

    def __str__(self):
        pass

    def get_projects(self, json_data):
        markdown_desc = json_data['body']
        pattern = r'### \[(.*?)\]'
        return re.findall(pattern, markdown_desc)

    def to_json(self):
        pass