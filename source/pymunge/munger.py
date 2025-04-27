from argparse import Namespace
from pathlib import Path
from registry import FileRegistry
from swbf.formats.req import Req
from util.enum import Enum
from multiprocessing import cpu_count as CPUS, Process, Queue
from ui.ui import gui


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
        self.processes : list[Process] = []
        self.ui: Process = Process(target=gui)

    def setup(self):
        self.processes = [Process(target=self.worker)] * (CPUS() - 1)

    def worker(self):
        pass

    def run(self):
        self.ui.start()

        for process in self.processes:
            process.start()

        for process in self.processes:
            process.join()

        self.ui.join()

    def munge(self):
        for entry in self.source.rglob('*.req'):
            req = Req(registry=self.registry, filepath=entry)
            req.parse()
