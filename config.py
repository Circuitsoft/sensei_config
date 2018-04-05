import yaml
import os

class Config(object):
    def __init__(self, path=None):
        self.config = {}

        self.reload(path or '~/.sensei.yaml')

    def reload(self, path=None):
        if path:
            path = os.path.expanduser(path)
            if os.path.isfile(path):
                self.path = path

        with open(self.path, 'r') as strm:
            self.config = yaml.load(strm)

    def __getitem__(self, n):
        return self.config[n]

    def __contains__(self, k):
        return k in self.config

    def get(self, k, d=None):
        return self.config.get(k, d)
