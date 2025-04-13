from argparse import Namespace
from pathlib import Path
from registry import FileRegistry
from swbf.formats.req import Req
from util.enum import Enum


class Munger:
    class Mode(Enum):
        Side = 'side'
        Sound = 'sound'
        World = 'world'
        Full = 'full'

    class Platform(Enum):
        PC = 'pc'
        PS2 = 'ps2'
        XBOX = 'xbox'

    def __init__(self, args: Namespace):
        self.source : Path = args.folder
        self.registry: FileRegistry = FileRegistry()
    
    def munge(self):
        for entry in self.source.rglob('*.req'):
            req = Req(registry=self.registry, filepath=entry)
            req.parse()
