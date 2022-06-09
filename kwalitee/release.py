import json
from ocrd_utils import getLogger

class Release():

    def __init__(self, json_data):
        self.tag = json_data['tag_name']

    def __str__(self):
        pass

    def get_projects(self):
        pass

    def to_json(self):
        pass