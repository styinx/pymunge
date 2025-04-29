from os import getcwd
from pathlib import Path
from argparse import ArgumentParser, Namespace
from munger import Munger
from util.logging import LogLevel, get_logger


BASE_DIR = Path(__file__).parent
CONFIG = Namespace(kwargs={
    ''
})


def MungePath(arg: str) -> Path:
    path = Path(arg)
    if not path.exists():
        path.mkdir()  # TODO: should parents be created and existing folders overwritten?
    return path.resolve()


def main():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-b', '--binary-dir', type=MungePath, default=Path(getcwd()))
    parser.add_argument('-c', '--colormode', action='store_true', default=False)
    parser.add_argument('-i', '--interactive', action='store_true', default=False)
    parser.add_argument('-l', '--log-level', type=str, default=LogLevel.Info, choices=list(LogLevel))
    parser.add_argument('-m', '--munge-mode', type=str, default=Munger.Mode.Full, choices=list(Munger.Mode))
    parser.add_argument('-n', '--no-gui', action='store_true', default=False)
    parser.add_argument('-p', '--platform', type=str, default=Munger.Platform.PC, choices=list(Munger.Platform))
    parser.add_argument('-s', '--source', type=MungePath, default=Path(getcwd()))
    parser.add_argument('-t', '--target', type=MungePath)

    subparsers = parser.add_subparsers(dest='tool')

    odfmunge = subparsers.add_parser(Munger.Tool.OdfMunge)

    scriptmunge = subparsers.add_parser(Munger.Tool.ScriptMunge)

    args = parser.parse_args()
    logger = get_logger('pymunge', Path(getcwd()), color_mode=args.colormode)

    logger.debug(f'debug')
    logger.info(f'info')
    logger.warning(f'warning')
    logger.error(f'error')
    logger.critical(f'critical')

    logger.info(f'Munger config:')
    with logger:
        logger.info(f'Log level:        "{args.log_level}"')
        logger.info(f'Color mode:       "{args.colormode}"')
        logger.info(f'Interactive:      "{args.interactive}"')
        logger.info(f'No GUI:           "{args.no_gui}"')
        logger.info(f'Munge platform:   "{args.platform}"')
        logger.info(f'Munge mode:       "{args.munge_mode}"')
        logger.info(f'Binary directory: "{args.binary_dir}"')
        logger.info(f'Source:           "{args.source}"')
        logger.info(f'Target:           "{args.target}"')
        if args.tool:
            logger.info(f'Munge tool:       "{args.tool}"')

    munger = Munger(args, logger)
    #munger.run()
    munger.munge()


if __name__ == '__main__':
    main()
