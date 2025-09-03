from multiprocessing import cpu_count as CPUS
from pathlib import Path
from queue import Empty
from signal import Signals
from sys import exit
from threading import Thread, Event

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

    StopEvent = Event()

    def __init__(self):
        pass
        #self.ui: Process = Process(target=gui)

    def run(self):
        #self.ui.start()

        threads = []

        for _ in range(CPUS() - 1):
            t = Thread(target=Munger.worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        #self.ui.join()
    
    @staticmethod
    def handle_signal(signum, frame):
        ENV.Log.critical(f'Received signal {signum} ({Signals(signum).name})')
        Munger.StopEvent.set()
        exit(1)

    @staticmethod
    def worker():
        while not Munger.StopEvent.is_set():

            try:
                file = ENV.Reg.munge_queue.get(timeout=0.5)
                if file:
                    Munger.munge(file, ENV.Reg.munge_dir)

            except Empty:
                # TODO: Breaking the loop should only occur after munging is done 
                break

            except Exception as e:
                ENV.Log.error(str(e))
                Munger.StopEvent.set()
                break

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
