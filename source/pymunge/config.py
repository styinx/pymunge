from argparse import ArgumentParser, ArgumentTypeError, Namespace, ArgumentTypeError, Namespace, _SubParsersAction
from os import getcwd
from pathlib import Path
from sys import path as PATH


CWD = Path(getcwd())
BASE_DIR = Path(__file__).parent
PYMUNGE_DIR = BASE_DIR.parent

PATH.append(str(PYMUNGE_DIR))


from swbf.parsers.parser import Ext # TODO: remove
from util.logging import LogLevel
from util.enum import Enum


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


class MungeFlags(Enum):
    Test1 = 'Test1'
    Test2 = 'Test2'


class MungeMode(Enum):
    Side = 'side'
    Sound = 'sound'
    World = 'world'
    Full = 'full'


class MungePlatform(Enum):
    PC = 'pc'
    PS2 = 'ps2'
    XBOX = 'xbox'


class MungeTool(Enum):
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


class GameVersion(Enum):
    _1 = '1'
    _2 = '2'


class Default:
    CACHE_FILE = '.pymunge.cache'
    GRAPH_FILE = '.pymunge.graph'
    LOG_FILE = '.pymunge.log'


# Default config
CONFIG = Namespace(**{
    'ansi_style': False,
    'log_file': Default.LOG_FILE,
    'log_level': LogLevel.Debug,
    'headless': False,
    'version': False,
    'run': 'munge',

    'munge': Namespace(**{
        'binary_dir': CWD,
        'cache_file': CWD / Default.CACHE_FILE,
        'clean': False,
        'dry_run': False,
        'interactive': False,
        'mode': MungeMode.Full,
        'platform': MungePlatform.PC,
        'resolve_dependencies': True,
        'source': CWD,
        'target': CWD,
        'tool': None,
        'game_version': GameVersion._1
    }),

    'cache': Namespace(**{
        'file': CWD / Default.CACHE_FILE
    })
})


def build_args(parser: ArgumentParser, args: Namespace):
    """
    Build nested Namespace objects recursively from subparsers.
    """
    for action in parser._actions:
        if not isinstance(action, _SubParsersAction):
            continue

        for name, subparser in action.choices.items():
            # Collect arguments that belong to this subparser.
            sub_ns = Namespace()
            for sub_action in subparser._actions:
                if hasattr(args, sub_action.dest):
                    setattr(sub_ns, sub_action.dest, getattr(args, sub_action.dest))
                    delattr(args, sub_action.dest)

            # Attach sub-namespace.
            setattr(args, name, sub_ns)

            # Recurse subparser with its own namespace.
            build_args(subparser, sub_ns)


def parse_config(file: Path) -> Namespace:
    config = {}
    exec(file.open('r').read(), {'__file__': str(file)}, config)

    if 'CONFIG' not in config:
        raise ArgumentTypeError(f'Missing variable "CONFIG" in config file "{file}"')

    return config['CONFIG']


def merge_namespace(default: Namespace, file: Namespace, cli: Namespace) -> Namespace:
    """
    Fills args in this order: DEFAULT CONFIG -> CONFIG FILE -> COMMAND LINE
    """
    args = Namespace()
    keys = set(vars(default)) | set(vars(file)) | set(vars(cli))

    for key in keys:
        default_val = getattr(default, key, None)
        file_val = getattr(file, key, None)
        cli_val = getattr(cli, key, None)

        if isinstance(default_val, Namespace) or isinstance(file_val, Namespace) or isinstance(cli_val, Namespace):
            default_val = default_val if isinstance(default_val, Namespace) else Namespace()
            file_val = file_val if isinstance(file_val, Namespace) else Namespace()
            cli_val = cli_val if isinstance(cli_val, Namespace) else Namespace()
            setattr(args, key, merge_namespace(default_val, file_val, cli_val))

        else:
            if cli_val not in (None, False):
                setattr(args, key, cli_val)
            elif file_val not in (None, False):
                setattr(args, key, file_val)
            else:
                setattr(args, key, default_val)

    return args


def populate_config(parser: ArgumentParser):
    cli_args = parser.parse_args()
    build_args(parser, cli_args)

    cfg_args = Namespace()
    if cli_args.config:
        cfg_args = parse_config(cli_args.config)

    return merge_namespace(CONFIG, cfg_args, cli_args)
