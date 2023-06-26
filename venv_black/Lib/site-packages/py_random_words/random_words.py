import json
from os import path
from random import choice


class RandomWords:
    def __init__(self):
        directory_path = path.dirname(__file__)
        with open(path.join(directory_path, 'animals.json'), 'r') as f:
            self.data_store = json.load(f)

    def get_word(self):
        return choice(self.data_store)
