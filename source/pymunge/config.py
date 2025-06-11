from argparse import ArgumentTypeError, Namespace
from os import getcwd
from pathlib import Path
from sys import path as PATH


BASE_DIR = Path(__file__).parent
PYMUNGE_DIR = BASE_DIR.parent

PATH.append(str(PYMUNGE_DIR))


from pymunge.app.munger import Munger
from pymunge.util.logging import LogLevel


CONFIG = Namespace(**{
    'ansi_style': False,
    'log_level': LogLevel.Debug,
    'headless': False,
    'version': False,
    'run': 'munge',

    'munge': Namespace(**{
        'binary_dir': Path(getcwd()),
        'cache': False,
        'clean': False,
        'dry_run': False,
        'interactive': False,
        'munge_mode': Munger.Mode.Full,
        'platform': Munger.Platform.PC,
        'resolve_dependencies': True,
        'source': Path(getcwd()),
        'target': Path(getcwd()) / 'munged',
        'tool': None,
    }),

    'cache': Namespace(**{
        'file': Path(getcwd()) / 'pymunge.bin'
    })
})

def parse_config(file: Path) -> Namespace:
    config = {}
    exec(file.open('r').read(), {'__file__': str(file)}, config)

    if 'CONFIG' not in config:
        raise ArgumentTypeError(f'Missing variable "CONFIG" in config file "{file}"')

    return config['CONFIG']

