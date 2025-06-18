from argparse import Namespace
from multiprocessing import cpu_count as CPUS, Process, Queue
from pathlib import Path

from app.environment import MungeEnvironment
from app.statistic import Statistic
from app.ui import gui
from swbf.parsers.odf import OdfParser
from swbf.parsers.msh import MshParser
from swbf.parsers.req import ReqParser
from swbf.builders.odf import Class
from swbf.builders.msh import Model
from swbf.builders.builder import Ucfb
from util.enum import Enum


class Munger:
    """
    Entry point of the munging process.
    """

    class Flags(Enum):
        Test1 = 'Test1'
        Test2 = 'Test2'

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

    def __init__(self, args: Namespace, environment: MungeEnvironment):
        self.environment: MungeEnvironment = environment
        self.source: Path = args.munge.source
        self.target: Path = args.munge.target / '_munged'
        self.filter: str = 'req'
        self.processes: list[Process] = []
        self.ui: Process = Process(target=gui)

        if not self.target.exists():
            self.target.mkdir(parents=True)

        if args.munge.tool:
            if args.munge.tool == Munger.Tool.ModelMunge:
                self.filter = 'msh'
            elif args.munge.tool == Munger.Tool.OdfMunge:
                self.filter = 'odf'
            elif args.munge.tool == Munger.Tool.ScriptMunge:
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

        def build_file(file: Path):
            parser = parser_type(filepath=file, logger=self.environment.logger)
            tree = self.environment.statistic.record('parse', str(parser.filepath), parser.parse)

            builder = builder_type(tree)
            self.environment.statistic.record('build', str(parser.filepath), builder.build)

            ucfb = Ucfb(tree)
            ucfb.add(builder)
            ucfb.data()

            #print(ucfb.dump(24))
            #print(builder.dump(24))

            path = self.target / (parser.filepath.name + '.class')
            with path.open('wb+') as f:
                self.environment.logger.info(f'Write to "{path}"')
                f.write(ucfb.data())

        if self.source.is_file():
            build_file(self.source)

        else:
            for entry in self.source.rglob(f'*.{self.filter}'):
                build_file(entry)

