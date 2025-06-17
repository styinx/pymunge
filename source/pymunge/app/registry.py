from pathlib import Path


class Dependency:

    def __init__(self, filepath: Path | None = None):
        self.filepath = filepath


class FileRegistry:

    def __init__(self):
        self.lookup = {
            'premunge': {},
            'postmunge': {},
            'ignored': {},
        }
