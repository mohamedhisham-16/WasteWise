class User:

    def __init__(self, user_id, name, password, role, zone, violation_score=0):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.role = role
        self.zone = zone
        self.violation_score = float(violation_score)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'password': self.password,
            'role': self.role,
            'zone': self.zone,
            'violation_score': 0.0
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a User object from a dictionary."""
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            password=data.get('password', '123'),
            role=data['role'],
            zone=data.get('zone', ''),
            violation_score=float(data.get('violation_score', 0.0))
        )

