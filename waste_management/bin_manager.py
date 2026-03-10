import json


class BinManager:
    def __init__(self, filepath="bins.json"):
        self.filepath = filepath
        self.bins = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.bins = json.load(f)
        except FileNotFoundError:
            self.bins = []

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.bins, f, indent=2)

    def add_bin(self, bin_info):
        self.bins.append(bin_info)
        self.save()

    def list_bins(self):
        return self.bins
