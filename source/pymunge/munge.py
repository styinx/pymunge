from argparse import ArgumentParser, ArgumentTypeError, Namespace, _SubParsersAction
from os import getcwd
from pathlib import Path
from sys import exit

from app.environment import MungeEnvironment
from app.munger import Munger
from util.logging import LogLevel, get_logger
from util.status import ExitCode
from version import STRING as VERSION_STRING
from config import CONFIG, parse_config


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

    munge = run_parsers.add_parser('munge')
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

    cache = run_parsers.add_parser('cache')
    cache.add_argument('-f', '--file', type=File, default=CONFIG.cache.file)

    munge_parsers = munge.add_subparsers(dest='tool')

    modelmunge = munge_parsers.add_parser(Munger.Tool.ModelMunge)

    odfmunge = munge_parsers.add_parser(Munger.Tool.OdfMunge)

    scriptmunge = munge_parsers.add_parser(Munger.Tool.ScriptMunge)

    return parser


def build_args(parser, args):
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


def main():
    parser = create_parser()

    args = parser.parse_args()

    if args.config:
        args = parse_config(args.config)

        args = parser.parse_args(namespace=args)

    build_args(parser, args)

    if args.version:
        print(VERSION_STRING)
        return ExitCode.Success

    logger = get_logger('pymunge', path=Path(getcwd()), level=args.log_level, ansi_style=args.ansi_style)

    logger.debug(f'Munger config:')
    with logger:
        for key, arg in args.__dict__.items():
            logger.debug(f'{key:20s} {arg}')

    try:

        environment = MungeEnvironment(logger)

        if args.run == 'munge':
            munger = Munger(args, environment)
            #munger.run()
            munger.munge()

            if args.munge.cache:
                environment.store(args.munge.cache)

        elif args.run == 'cache':
            environment.load(args.cache.file)

        environment.details()
        environment.summary()

    except Exception as e:
        logger.error(str(e))

        return ExitCode.Failure

    return ExitCode.Success


if __name__ == '__main__':
    exit(main())
