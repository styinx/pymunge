from argparse import Namespace
from multiprocessing import cpu_count as CPUS, Process, Queue
from pathlib import Path

from app.environment import MungeEnvironment as ENV
from app.ui import gui
from swbf.parsers.odf import OdfParser
from swbf.parsers.msh import MshParser
from swbf.parsers.req import ReqParser
from swbf.builders.odf import ClassBuilder
from swbf.builders.msh import ModelBuilder
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
        AnimationMunge = 'AnimationMunge'
        BinMunge = 'BinMunge'
        ConfigMunge = 'ConfigMunge'
        LevelPack = 'LevelPack'
        LocalizeMunge = 'LocalizeMunge'
        OdfMunge = 'OdfMunge'
        ModelMunge = 'ModelMunge'
        MovieMunge = 'MovieMunge'
        PathMunge = 'PathMunge'
        PathPlanningMunge = 'PathPlanningMunge'
        ScriptMunge = 'ScriptMunge'
        TerrainMunge = 'TerrainMunge'
        TextureMunge = 'TextureMunge'
        WorldMunge = 'WorldMunge'

    class Platform(Enum):
        PC = 'pc'
        PS2 = 'ps2'
        XBOX = 'xbox'

    def __init__(self, args: Namespace):
        self.source: Path = args.munge.source
        self.target: Path = args.munge.target / '_munged'
        self.source_filter: str = 'req'
        self.processes: list[Process] = []
        self.ui: Process = Process(target=gui)

        if not self.target.exists():
            self.target.mkdir(parents=True)

        if args.munge.tool:
            if args.munge.tool == Munger.Tool.ModelMunge:
                self.source_filter = 'msh'
            elif args.munge.tool == Munger.Tool.OdfMunge:
                self.source_filter = 'odf'
            elif args.munge.tool == Munger.Tool.ScriptMunge:
                self.source_filter = 'lua'

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
            'msh': MshParser,
            'odf': OdfParser,
            'req': ReqParser,
        }
        builders = {
            'msh': ModelBuilder,
            'odf': ClassBuilder,
            'req': Ucfb,
        }

        def build_file(file: Path):
            parser_type = parsers.get(self.source_filter, ReqParser)
            builder_type = builders.get(self.source_filter, Ucfb)

            parser = parser_type(filepath=file, logger=ENV.Log)
            tree = ENV.Stat.record('parse', str(parser.filepath), parser.parse)
            ENV.Reg.add_source_file(parser.filepath)

            builder = builder_type(tree)
            build_file_name = parser.filepath.name + f'.{builder.extension}'
            build_file = self.target / build_file_name
            ENV.Stat.record('build', str(build_file), builder.build)

            # Pack the built file into an ucfb
            ucfb = Ucfb(tree)
            ucfb.add(builder)
            ucfb.data()

            with build_file.open('wb+') as f:
                ENV.Log.debug(f'Writing "{build_file}"')
                f.write(ucfb.data())
                ENV.Reg.add_build_file(build_file)

        if self.source.is_file():
            build_file(self.source)

        else:
            ENV.Log.info(f'Processing "{self.source}"')
            for entry in self.source.rglob(f'*.{self.source_filter}'):
                build_file(entry)
            ENV.Log.info(f'Results written to "{self.target}"')

