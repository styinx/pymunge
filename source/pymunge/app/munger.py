from argparse import Namespace
from multiprocessing import cpu_count as CPUS, Process, Queue
from pathlib import Path

from app.environment import MungeEnvironment as ENV
from app.ui import gui
from swbf.parsers.cfg import CfgParser
from swbf.parsers.fx import FxParser
from swbf.parsers.msh import MshParser
from swbf.parsers.odf import OdfParser
from swbf.parsers.req import ReqParser
from swbf.parsers.sky import SkyParser
from swbf.builders.odf import ClassBuilder
from swbf.builders.msh import ModelBuilder
from swbf.builders.builder import Ucfb
from util.enum import Enum
from util.diagnostic import ErrorMessage


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
        ModelMunge = 'ModelMunge'
        MovieMunge = 'MovieMunge'
        OdfMunge = 'OdfMunge'
        PathMunge = 'PathMunge'
        PathPlanningMunge = 'PathPlanningMunge'
        ScriptMunge = 'ScriptMunge'
        SoundFLMunge = 'SoundFLMunge'
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
        self.source_filters: list[str] = ['req']
        self.processes: list[Process] = []
        self.ui: Process = Process(target=gui)

        if not self.target.exists():
            self.target.mkdir(parents=True)

        if args.munge.tool:
            tool_filters = {
                Munger.Tool.BinMunge: ['zaa', 'zaf'],
                Munger.Tool.ConfigMunge: ['cfg', 'ffx', 'fx', 'mcfg', 'mus', 'sky', 'snd', 'tsr'],
                Munger.Tool.LevelPack: ['req'],
                Munger.Tool.LocalizeMunge: ['cfg'],
                Munger.Tool.ModelMunge: ['msh'],
                Munger.Tool.MovieMunge: ['mlst'],
                Munger.Tool.OdfMunge: ['odf'],
                Munger.Tool.PathMunge: ['pth'],
                Munger.Tool.PathPlanningMunge: ['pln'],
                Munger.Tool.ScriptMunge: ['lua'],
                Munger.Tool.SoundFLMunge: ['asfx', 'sfx', 'st4', 'stm'],
                Munger.Tool.TerrainMunge: ['ter'],
                Munger.Tool.TextureMunge: ['tga', 'pic'],
                Munger.Tool.WorldMunge: ['wld'],
            }
            self.source_filters = tool_filters.get(args.munge.tool, ['req'])

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
            'cfg': CfgParser,
            'fx': FxParser,
            'msh': MshParser,
            'odf': OdfParser,
            'req': ReqParser,
            'sky': SkyParser,
        }
        builders = {
            'msh': ModelBuilder,
            'odf': ClassBuilder,
            'req': Ucfb,
        }

        def build_file(file: Path):
            ext = file.suffix[1:]

            if ext not in parsers:
                ENV.Diag.report(ErrorMessage(f'File type "{ext}" not yet supported for parsing'))
                return

            parser_type = parsers[ext]
            parser = parser_type(filepath=file, logger=ENV.Log)
            tree = ENV.Stat.record('parse', str(parser.filepath), parser.parse)
            ENV.Reg.register_file(parser.filepath)

            if ext not in builders:
                ENV.Diag.report(ErrorMessage(f'File type "{ext}" not yet supported for building'))
                return

            builder_type = builders[ext]
            builder = builder_type(tree)
            build_file_name = parser.filepath.name + f'.{builder.Extension}'
            build_file = self.target / build_file_name
            ENV.Stat.record('build', str(build_file), builder.build)

            # Pack the built file into an ucfb
            ucfb = Ucfb(tree)
            ucfb.add(builder)
            ucfb.data()

            with build_file.open('wb+') as f:
                ENV.Log.debug(f'Writing "{build_file}"')
                f.write(ucfb.data())
                ENV.Reg.register_file(build_file)

        if self.source.is_file():
            build_file(self.source)

        else:
            ENV.Log.info(f'Processing "{self.source}"')
            for source_filter in self.source_filters:
                for entry in self.source.rglob(f'*.{source_filter}'):
                    build_file(entry)
            ENV.Log.info(f'Results written to "{self.target}"')

