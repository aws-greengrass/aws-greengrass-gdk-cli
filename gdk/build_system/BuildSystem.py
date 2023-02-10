
class BuildSystem:
    """
    Delegates build tasks to the appropriate build system
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BuildSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.systems = {}

    def register(self, system):
        self.systems[system.__str__()] = system

    def build(self, system_type):
        system = self.systems.get(system_type)

        if not system:
            raise TypeError(f"system type {system_type} is not currently supported")

        return system.build()
