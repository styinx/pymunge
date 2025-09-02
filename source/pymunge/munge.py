from argparse import ArgumentParser, ArgumentTypeError, Namespace, _SubParsersAction
from os import getcwd
from pathlib import Path
from signal import signal, SIGINT, SIGTERM
from sys import exit
import traceback

from app.environment import MungeEnvironment
from app.munger import Munger
from swbf.parsers.parser import Ext
from util.enum import Enum
from util.logging import LogLevel, get_logger
from util.status import ExitCode
from version import INFO as VERSION_INFO
from config import CONFIG, parse_config


def handle_signal(signum, frame):
    print("Received SIGTERM, shutting down pool...")
    executor.shutdown(wait=False, cancel_futures=True)
    exit(0)

signal(SIGTERM, handle_signal)
signal(SIGINT, handle_signal)


class Run(Enum):
    Cache = 'cache'
    Munge = 'munge'


def MungePath(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        path.mkdir(parents=True)  # TODO: should parents be created and existing folders overwritten?
    return path.resolve()


def File(arg: str) -> Path:
    path = Path(arg)

    if not path.is_file():
        raise ArgumentTypeError('Given path is no file!')
    if not path.exists():
        raise ArgumentTypeError('Non existing file was given!')

    return path.resolve()


def create_parser():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-a', '--ansi-style', action='store_true', default=CONFIG.ansi_style)
    parser.add_argument('-c', '--config', type=File)
    parser.add_argument('-l', '--log-level', type=str, default=CONFIG.log_level, choices=list(LogLevel))
    parser.add_argument('-H', '--headless', action='store_true', default=CONFIG.headless)
    parser.add_argument('-v', '--version', action='store_true', default=CONFIG.version)

    run_parsers = parser.add_subparsers(dest='run', required=True)

    munge = run_parsers.add_parser(Run.Munge)
    munge.add_argument('-b', '--binary-dir', type=MungePath, default=CONFIG.munge.binary_dir)
    munge.add_argument('-c', '--cache', type=Path)
    munge.add_argument('-C', '--clean', action='store_true', default=CONFIG.munge.clean)
    munge.add_argument('-d', '--dry-run', action='store_true', default=CONFIG.munge.dry_run)
    munge.add_argument('-f', '--flags', type=str, action='append', choices=list(Munger.Flags))
    munge.add_argument('-i', '--interactive', action='store_true', default=CONFIG.munge.interactive)
    munge.add_argument('-m', '--munge-mode', type=str, default=CONFIG.munge.munge_mode, choices=list(Munger.Mode))
    munge.add_argument('-p', '--platform', type=str, default=CONFIG.munge.platform, choices=list(Munger.Platform))
    munge.add_argument('-r', '--resolve-dependencies', action='store_true', default=CONFIG.munge.resolve_dependencies)
    munge.add_argument('-s', '--source', type=MungePath, default=CONFIG.munge.source)
    munge.add_argument('-t', '--target', type=MungePath, default=CONFIG.munge.target)

    cache = run_parsers.add_parser(Run.Cache)
    cache.add_argument('-f', '--file', type=File, default=CONFIG.cache.file)

    munge_parsers = munge.add_subparsers(dest='tool')

    configmunge = munge_parsers.add_parser(Tool.ConfigMunge)
    modelmunge = munge_parsers.add_parser(Tool.ModelMunge)
    odfmunge = munge_parsers.add_parser(Tool.OdfMunge)
    scriptmunge = munge_parsers.add_parser(Tool.ScriptMunge)

    return parser


def build_args(parser, args):
    """
    Build nested args namespace from subparsers.
    """
    for action in parser._actions:
        if not isinstance(action, _SubParsersAction):
            continue

        for name, subparser in action.choices.items():
            subparser_args = Namespace()
            for subparser_action in subparser._actions:
                if hasattr(args, subparser_action.dest):
                    setattr(subparser_args, subparser_action.dest, getattr(args, subparser_action.dest))
                    delattr(args, subparser_action.dest)
            setattr(args, name, subparser_args)
            build_args(subparser, args)


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

    _FILTER = {
        BinMunge: [Ext.Zaa, Ext.Zaf],
        ConfigMunge: [Ext.Cfg, Ext.Ffx, Ext.Fx, Ext.Mcfg, Ext.Mus, Ext.Sky, Ext.Snd, Ext.Tsr],
        LevelPack: [Ext.Req],
        LocalizeMunge: [Ext.Cfg],
        ModelMunge: [Ext.Msh],
        MovieMunge: [Ext.Mlst],
        OdfMunge: [Ext.Odf],
        PathMunge: [Ext.Pth],
        PathPlanningMunge: [Ext.Pln],
        ScriptMunge: [Ext.Lua],
        SoundFLMunge: [Ext.Asfx, Ext.Sfx, Ext.St4, Ext.Stm],
        TerrainMunge: [Ext.Ter],
        TextureMunge: [Ext.Tga, Ext.Pic],
        WorldMunge: [Ext.Wld],
    }


def main():
    parser = create_parser()

    args = parser.parse_args()

    if args.config:
        args = parse_config(args.config)

        args = parser.parse_args(namespace=args)

    build_args(parser, args)

    if args.version:
        print(VERSION_INFO)
        return ExitCode.Success

    logger = get_logger('pymunge', path=Path(getcwd()), level=args.log_level, ansi_style=args.ansi_style)

    logger.debug(f'Munger config:')
    with logger:
        for key, arg in args.__dict__.items():
            logger.debug(f'{key:20s} {arg}')

    try:
        if args.munge.tool:
            source_filters = Tool._FILTER[args.munge.tool]
        else:
            source_filters = [Ext.Req]

        environment = MungeEnvironment(args, logger)
        environment.registry.load_dependencies()
        environment.registry.collect_munge_files(source_filters)

        if args.run == 'munge':
            munger = Munger()
            munger.run()

            if args.munge.cache:
                environment.store_cache()

        elif args.run == 'cache':
            environment.load_cache()

        if args.log_level == LogLevel.Debug:
            environment.details()

        environment.registry.store_dependencies()
        environment.summary()

    except Exception as e:
        logger.error(str(e))
        print(traceback.format_exc())

        return ExitCode.Failure

    return ExitCode.Success


if __name__ == '__main__':
    exit(main())
