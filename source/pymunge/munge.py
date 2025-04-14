from os import getcwd
from pathlib import Path
from argparse import ArgumentParser
from munger import Munger
from registry import FileRegistry
from swbf.formats.req import Req
from util.logging import LogLevel, get_logger


def main():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-l', '--log-level', type=str, default=LogLevel.Info, choices=list(LogLevel))
    parser.add_argument('-f', '--folder', type=Path, default=getcwd(), required=True)
    parser.add_argument('-m', '--mode', type=str, default=Munger.Mode.Full, choices=list(Munger.Mode))
    parser.add_argument('-p', '--platform', type=str, default=Munger.Platform.PC, choices=list(Munger.Platform))

    args = parser.parse_args()
    logger = get_logger(__name__)

    munger = Munger(args)
    munger.run()
    #munger.munge()


if __name__ == '__main__':
    main()