from multiprocessing import cpu_count as CPUS, Process
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

from app.environment import MungeEnvironment as ENV
from app.ui import gui
from swbf.parsers.cfg import CfgParser
from swbf.parsers.fx import FxParser
from swbf.parsers.msh import MshParser
from swbf.parsers.odf import OdfParser
from swbf.parsers.parser import Ext
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

    class Platform(Enum):
        PC = 'pc'
        PS2 = 'ps2'
        XBOX = 'xbox'

    PARSER = {
        Ext.Cfg: CfgParser,
        Ext.Fx: FxParser,
        Ext.Msh: MshParser,
        Ext.Odf: OdfParser,
        Ext.Req: ReqParser,
        Ext.Sky: SkyParser,
    }

    BUILDER = {
        Ext.Msh: ModelBuilder,
        Ext.Odf: ClassBuilder,
        Ext.Req: Ucfb,
    }

    def __init__(self):
        pass
        #self.ui: Process = Process(target=gui)

    def worker(queue, target):
        for file in iter(queue.get, None):  # stop when None is sent
            Munger.munge(file, target)

    def run(self):
        #self.ui.start()

        queue = mp.Queue()

        # Fill the queue
        while not ENV.Reg.munge_queue.empty():
            queue.put(ENV.Reg.munge_queue.get())

        with ProcessPoolExecutor(max_workers=CPUS() - 1) as executor:
            for _ in range(CPUS() - 1):
                executor.submit(Munger.worker, queue, ENV.Reg.munge_dir)

            # Signal workers to exit
            for _ in range(CPUS() - 1):
                queue.put(None)

        #self.ui.join()

    @staticmethod
    def munge(file: Path, target: Path):
        ext = file.suffix[1:]

        if ext not in Munger.PARSER:
            ENV.Diag.report(ErrorMessage(f'File type "{ext}" not yet supported for parsing'))
            return

        parser_type = Munger.PARSER[ext]
        parser = parser_type(filepath=file, logger=ENV.Log)
        tree = ENV.Stat.record('parse', str(parser.filepath), parser.parse)
        ENV.Reg.register_file(parser.filepath)

        if ext not in Munger.BUILDER:
            ENV.Diag.report(ErrorMessage(f'File type "{ext}" not yet supported for building'))
            return

        builder_type = Munger.BUILDER[ext]
        builder = builder_type(tree)
        build_file_name = parser.filepath.name + f'.{builder.Extension}'
        build_file = target / build_file_name
        ENV.Stat.record('build', str(build_file), builder.build)

        # Pack the built file into an ucfb
        ucfb = Ucfb(tree)
        ucfb.add(builder)
        ucfb.data()

        with build_file.open('wb+') as f:
            ENV.Log.debug(f'Writing "{build_file}"')
            f.write(ucfb.data())
            ENV.Reg.register_file(build_file)
