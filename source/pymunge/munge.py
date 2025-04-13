from os import getcwd
from pathlib import Path
from argparse import ArgumentParser
from munger import Munger
from registry import FileRegistry
from swbf.formats.req import Req


def main():
    parser = ArgumentParser('pymunge')
    parser.add_argument('-f', '--folder', type=Path, default=getcwd(), required=True)
    parser.add_argument('-m', '--mode', choices=list(Munger.Mode), default=Munger.Mode.Full)
    parser.add_argument('-p', '--platform', choices=list(Munger.Platform), default=Munger.Platform.PC)

    args = parser.parse_args()

    munger = Munger(args)
    munger.munge()


if __name__ == '__main__':
    main()