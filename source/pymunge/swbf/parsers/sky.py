from logging import Logger
from pathlib import Path

from parxel.nodes import Node, LexicalNode
from parxel.token import TK, Token

from app.environment import MungeEnvironment as ENV
from swbf.parsers.parser import SwbfTextParser
from swbf.parsers.cfg import CfgParser
from util.diagnostic import WarningMessage
from util.enum import Enum
from util.logging import get_logger


class SkyWarning(WarningMessage):
    scope = 'SKY'

class SkyParser(CfgParser):
    extension = 'sky'

    class Header(Enum):
        FlatInfo = 'FlatInfo'
        DomeInfo = 'DomeInfo'
        DomeModel = 'DomeModel'
        LowResTerrain = 'LowResTerrain'
        SkyInfo = 'SkyInfo'
        SkyObject = 'SkyObject'
        SunInfo = 'SunInfo'

    class Function(Enum):
        Ambient = 'Ambient'
        AmbientColor = 'AmbientColor'
        Angle = 'Angle'
        BackAngle = 'BackAngle'
        BackColor = 'BackColor'
        BackDegree = 'BackDegree'
        BottomDirectionalAmbientColor = 'BottomDirectionalAmbientColor'
        CharacterAmbientColor = 'CharacterAmbientColor'
        Color = 'Color'
        Degree = 'Degree'
        DetailTexture = 'DetailTexture'
        DetailTextureScale = 'DetailTextureScale'
        Enable = 'Enable'
        FarSceneRange = 'FarSceneRange'
        Filter = 'Filter'
        FogColor = 'FogColor'
        FogFar = 'FogFar'
        FogNear = 'FogNear'
        FogRamp = 'FogRamp'
        FogRange = 'FogRange'
        Geometry = 'Geometry'
        Height = 'Height'
        Intensity = 'Intensity'
        MaxDistance = 'MaxDistance'
        Modulate = 'Modulate'
        MovementScale = 'MovementScale'
        NearSceneRange = 'NearSceneRange'
        ObjectVisibility = 'ObjectVisibility'
        Offset = 'Offset'
        PatchResolution = 'PatchResolution'
        ShadowColor = 'ShadowColor'
        Softness = 'Softness'
        SoftnessParam = 'SoftnessParam'
        TerrainColorDarkening = 'TerrainColorDarkening'
        Texture = 'Texture'
        TextureSpeed = 'TextureSpeed'
        Threshold = 'Threshold'
        TileSize = 'TileSize'
        TopDirectionalAmbientColor = 'TopDirectionalAmbientColor'
        VehicleAmbientColor = 'VehicleAmbientColor'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)


if __name__ == '__main__':
    SkyParser.cmd_helper()
