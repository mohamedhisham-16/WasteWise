import json


class FacilityManager:
    def __init__(self, filepath="facilities.json"):
        self.filepath = filepath
        self.facilities = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.facilities = json.load(f)
        except FileNotFoundError:
            self.facilities = []

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.facilities, f, indent=2)

    def add_facility(self, facility_info):
        self.facilities.append(facility_info)
        self.save()

    def list_facilities(self):
        return self.facilities
