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
    TOPIC = 'SKY'

class SkyParser(CfgParser):
    Extension = 'sky'

    class Call(Enum):
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
        DomeInfo = 'DomeInfo'
        DomeModel = 'DomeModel'
        Enable = 'Enable'
        FarSceneRange = 'FarSceneRange'
        Filter = 'Filter'
        FlatInfo = 'FlatInfo'
        FogColor = 'FogColor'
        FogFar = 'FogFar'
        FogNear = 'FogNear'
        FogRamp = 'FogRamp'
        FogRange = 'FogRange'
        Geometry = 'Geometry'
        Height = 'Height'
        Intensity = 'Intensity'
        LowResTerrain = 'LowResTerrain'
        MaxDistance = 'MaxDistance'
        Modulate = 'Modulate'
        MovementScale = 'MovementScale'
        NearSceneRange = 'NearSceneRange'
        ObjectVisibility = 'ObjectVisibility'
        Offset = 'Offset'
        PatchResolution = 'PatchResolution'
        ShadowColor = 'ShadowColor'
        SkyInfo = 'SkyInfo'
        SkyObject = 'SkyObject'
        Softness = 'Softness'
        SoftnessParam = 'SoftnessParam'
        SunInfo = 'SunInfo'
        TerrainColorDarkening = 'TerrainColorDarkening'
        TerrainEnable = 'TerrainEnable'
        Texture = 'Texture'
        TextureSpeed = 'TextureSpeed'
        Threshold = 'Threshold'
        TileSize = 'TileSize'
        TopDirectionalAmbientColor = 'TopDirectionalAmbientColor'
        VehicleAmbientColor = 'VehicleAmbientColor'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

        CfgParser.Call = SkyParser.Call


if __name__ == '__main__':
    SkyParser.cmd_helper()
