from argparse import Namespace
from multiprocessing import cpu_count as CPUS, Process, Queue
from pathlib import Path

from app.environment import MungeEnvironment
from app.ui import gui
from swbf.parsers.odf import OdfParser
from swbf.parsers.msh import MshParser
from swbf.parsers.req import ReqParser
from swbf.builders.odf import Class
from swbf.builders.msh import Model
from swbf.builders.builder import Ucfb
from util.enum import Enum
from util.logging import get_logger, ScopedLogger
from util.time import duration, measure


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

    def __init__(self, args: Namespace, logger: ScopedLogger = get_logger(__name__)):
        self.logger: ScopedLogger = logger
        self.source: Path = args.source
        self.filter: str = 'req'
        self.environment: MungeEnvironment = MungeEnvironment(logger=self.logger)
        self.processes: list[Process] = []
        self.ui: Process = Process(target=gui)

        if args.tool:
            if args.tool == Munger.Tool.ModelMunge:
                self.filter = 'msh'
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
        parsers = {'req': ReqParser, 'msh': MshParser, 'odf': OdfParser}
        builders = {
            'req': Ucfb,
            'odf': Class,
            'msh': Model,
        }

        parser_type = parsers.get(self.filter, ReqParser)
        builder_type = builders.get(self.filter, Ucfb)

        if self.source.is_file():
            parser = parser_type(filepath=self.source, logger=self.logger)
            tree = self.environment.statistic.record('parse', parser.filepath, parser.parse)

            builder = builder_type(tree)
            self.environment.statistic.record('build', parser.filepath, builder.build)

            print(builder.dump(24))

            #ucfb = Ucfb(tree)
            #ucfb.add(builder)
            #ucfb.data()
            #print(ucfb.dump(24))

        else:
            for entry in self.source.rglob(f'*.{self.filter}'):
                parser = parser_type(filepath=entry, logger=self.logger)
                tree = self.environment.statistic.record('parse', parser.filepath, parser.parse)

                builder = builder_type(tree)
                self.environment.statistic.record('build', parser.filepath, builder.build)

                print(builder.dump(24))

        self.environment.diagnostic.summary()
        self.environment.statistic.summary()
