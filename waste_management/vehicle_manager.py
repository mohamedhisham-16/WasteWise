import json


class VehicleManager:
    def __init__(self, filepath="vehicles.json"):
        self.filepath = filepath
        self.vehicles = []
        self.load()

    def load(self):
        try:
            with open(self.filepath, "r") as f:
                self.vehicles = json.load(f)
        except FileNotFoundError:
            self.vehicles = []

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.vehicles, f, indent=2)

    def add_vehicle(self, vehicle_info):
        self.vehicles.append(vehicle_info)
        self.save()

    def list_vehicles(self):
        return self.vehicles
