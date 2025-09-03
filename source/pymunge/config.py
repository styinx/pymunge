from argparse import ArgumentTypeError, Namespace
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


def parse_config(file: Path) -> Namespace:
    config = {}
    exec(file.open('r').read(), {'__file__': str(file)}, config)

    if 'CONFIG' not in config:
        raise ArgumentTypeError(f'Missing variable "CONFIG" in config file "{file}"')

    return config['CONFIG']

