from argparse import ArgumentParser
from os import getcwd
from pathlib import Path
from signal import signal, SIGINT, SIGTERM
from sys import exit
import traceback

from app.environment import MungeEnvironment
from app.munger import Munger
from config import CONFIG, CWD, build_args, parse_config, populate_config, File, MungePath
from config import GameVersion, MungeFlags, MungeMode, MungePlatform, MungeTool, Run
from swbf.parsers.parser import Ext
from util.enumeration import Enum
from util.logging import LogLevel, get_logger
from util.status import ExitCode
from version import INFO as VERSION_INFO


signal(SIGTERM, Munger.handle_signal)
signal(SIGINT, Munger.handle_signal)


def create_parser():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-a', '--ansi-style', action='store_true', default=CONFIG.ansi_style)
    parser.add_argument('-c', '--config', type=File)
    parser.add_argument('-f', '--log-file', type=str, default=CONFIG.log_file)
    parser.add_argument('-l', '--log-level', type=str, default=CONFIG.log_level, choices=LogLevel.vals())
    parser.add_argument('-n', '--no-log-file', action='store_true')
    parser.add_argument('-H', '--headless', action='store_true', default=CONFIG.headless)
    parser.add_argument('-v', '--version', action='store_true', default=CONFIG.version)

    run_parsers = parser.add_subparsers(dest='run', required=True)

    cache = run_parsers.add_parser(Run.Cache)
    cache.add_argument('-f', '--file', type=File, default=CONFIG.cache.file)

    format = run_parsers.add_parser(Run.Format)
    format.add_argument('-c', '--check', action='store_true')
    format.add_argument('-d', '--directory', type=Path, default=CWD)
    format.add_argument('-f', '--format-file', type=File)
    format.add_argument('-F', '--filters', type=str, choices=[Ext.Odf, Ext.Asfx], nargs='+')
    format.add_argument('-s', '--style', type=File, required=True)

    munge = run_parsers.add_parser(Run.Munge)
    munge.add_argument('-b', '--binary-dir', type=MungePath, default=CONFIG.munge.binary_dir)
    munge.add_argument('-c', '--cache-file', type=Path, default=CONFIG.munge.cache_file)
    munge.add_argument('-C', '--clean', action='store_true', default=CONFIG.munge.clean)
    munge.add_argument('-d', '--dry-run', action='store_true', default=CONFIG.munge.dry_run)
    munge.add_argument('-f', '--flags', type=str, action='append', choices=MungeFlags.vals())
    munge.add_argument('-i', '--interactive', action='store_true', default=CONFIG.munge.interactive)
    munge.add_argument('-m', '--mode', type=str, default=CONFIG.munge.mode, choices=MungeMode.vals())
    munge.add_argument('-p', '--platform', type=str, default=CONFIG.munge.platform, choices=MungePlatform.vals())
    munge.add_argument('-r', '--resolve-dependencies', action='store_true', default=CONFIG.munge.resolve_dependencies)
    munge.add_argument('-s', '--source', type=MungePath, default=CONFIG.munge.source)
    munge.add_argument('-t', '--target', type=MungePath, default=CONFIG.munge.target)
    munge.add_argument('-v', '--game-version', type=str, default=CONFIG.munge.game_version, choices=GameVersion.vals())

    munge_parsers = munge.add_subparsers(dest='tool')

    configmunge = munge_parsers.add_parser(MungeTool.ConfigMunge)
    modelmunge = munge_parsers.add_parser(MungeTool.ModelMunge)
    odfmunge = munge_parsers.add_parser(MungeTool.OdfMunge)
    scriptmunge = munge_parsers.add_parser(MungeTool.ScriptMunge)

    return parser


def main():
    parser = create_parser()

    args = populate_config(parser)

    if args.version:
        print(VERSION_INFO)
        return ExitCode.Success

    log_path = None if args.no_log_file else CWD
    log_file = None if args.no_log_file else args.log_file
    logger = get_logger('pymunge', filepath=log_path, filename=log_file, level=args.log_level, ansi_style=args.ansi_style)

    logger.debug(f'Munger config:')
    with logger:
        for key, arg in args.__dict__.items():
            logger.debug(f'{key:20s} {arg}')

    try:
        if args.munge.tool:
            source_filters = MungeTool._FILTER[args.munge.tool]
        else:
            source_filters = [Ext.Req]

        environment = MungeEnvironment(args, logger)

        if args.run == Run.Cache:
            environment.load_cache()

        elif args.run == Run.Format:
            munger = Munger()
            munger.format(args.format.format_file or args.format.directory, args.format.filters, args.format.style)

        elif args.run == Run.Munge:
            environment.registry.load_dependencies()
            environment.registry.collect_munge_files(source_filters)

            munger = Munger()
            munger.run()

            environment.store_cache()
            environment.registry.store_dependencies()

        if args.log_level == LogLevel.Debug:
            environment.details()

        environment.summary()

    except Exception as e:
        logger.error(str(e))
        print(traceback.format_exc())

        return ExitCode.Failure

    return ExitCode.Success


if __name__ == '__main__':
    exit(main())
