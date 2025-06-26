from pathlib import Path


class Dependency:

    def __init__(self, filepath: Path | None = None):
        self.filepath = filepath


class FileRegistry:

    def __init__(self):
        self.source_files = {}
        self.build_files = {}

    def add_source_file(self, path: Path):
        self.source_files[path] = {
            'dependencies': []
        }

    def add_build_file(self, path: Path):
        self.build_files[path] = {
            'dependencies': []
        }

