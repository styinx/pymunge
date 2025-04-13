from argparse import Namespace
from pathlib import Path
from registry import FileRegistry
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
        self.registry = FileRegistry()


class MungerStub(Munger):
    def __init__(self, folder: Path):
        args = Namespace({'folder': folder})
        Munger.__init__(args)
