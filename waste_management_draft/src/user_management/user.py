class User:

    def __init__(self, user_id, name, role, zone):
        self.user_id = user_id
        self.name = name
        self.role = role
        self.zone = zone

    def to_dict(self):

        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role,
            'zone': self.zone
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a User object from a dictionary."""
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            role=data['role'],
            zone=data.get('zone', '')
        )
