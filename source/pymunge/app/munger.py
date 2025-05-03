from argparse import Namespace
from multiprocessing import cpu_count as CPUS, Process, Queue
from pathlib import Path

from app.registry import FileRegistry
from app.ui import gui
from swbf.parsers.odf import Odf
from swbf.parsers.req import Req
from swbf.builders.odf import Class
from swbf.builders.ucfb import Ucfb
from util.enum import Enum
from util.logging import get_logger


logger = get_logger(__name__)


class Diagnostic:
    def __init__(self):
        pass


class Munger:
    """
    Entry point of the munging process.
    """

    class Mode(Enum):
        Side = 'side'
        Sound = 'sound'
        World = 'world'
        Full = 'full'

    class Tool(Enum):
        """
        If specified the munge tool filters the input of the munging process.
        """
        OdfMunge = 'OdfMunge'
        ModelMunge = 'ModelMunge'
        ScriptMunge = 'ScriptMunge'

    class Platform(Enum):
        PC = 'pc'
        PS2 = 'ps2'
        XBOX = 'xbox'

    def __init__(self, args: Namespace, logger = logger):
        self.logger = logger
        self.source: Path = args.source
        self.filter: str = 'req'
        self.registry: FileRegistry = FileRegistry()
        self.diagnostic: Diagnostic = Diagnostic()
        self.processes : list[Process] = []
        self.ui: Process = Process(target=gui)

        if args.tool:
            if args.tool == Munger.Tool.ModelMunge:
                pass
            elif args.tool == Munger.Tool.OdfMunge:
                self.filter = 'odf'
            elif args.tool == Munger.Tool.ScriptMunge:
                pass

    def setup(self):
        self.processes = [Process(target=self.worker)] * (CPUS() - 1)

    def worker(self):
        pass

    def run(self):
        #self.ui.start()

        for process in self.processes:
            process.start()

        for process in self.processes:
            process.join()

        #self.ui.join()

    def munge(self):
        parsers = {
            'req': Req,
            'odf': Odf
        }
        builders = {
            'req': Ucfb,
            'odf': Class
        }
        parser_type = parsers.get(self.filter, Req)
        builder_type = builders.get(self.filter, Ucfb)

        if self.source.is_file():
            parser = parser_type(registry=self.registry, filepath=self.source, logger=self.logger)
            tree = parser.parse()
            builder = builder_type(tree)
            builder.build()

            ucfb = Ucfb()
            ucfb.add(builder)
            ucfb.data()
            print(ucfb.dump())

        else:
            for entry in self.source.rglob(f'*.{self.filter}'):
                parser = parser_type(registry=self.registry, filepath=entry, logger=self.logger)
                tree = parser.parse()
                builder = builder_type(tree)
                builder.build()
                print(builder.dump())

