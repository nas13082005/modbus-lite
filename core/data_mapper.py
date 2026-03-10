import yaml


class DataMapper:

    def __init__(self, config):

        with open(config) as f:
            self.data = yaml.safe_load(f)


    def mapping(self):

        return self.data["mapping"]
