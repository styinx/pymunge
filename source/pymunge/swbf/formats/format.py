from munger import Munger
from registry import Dependency


class Format:
    def __init__(self, munger: Munger):
        self.munger: Munger = munger
    
    def register_dependency(self, dependency: Dependency):
        if dependency.filepath:
            self.munger.registry.lookup['premunge'][dependency.filepath.name] = dependency
            print(dependency.filepath)
