from logging import Logger
from pathlib import Path

from parxel.token import Token

from swbf.parsers.parser import Ext, SwbfTextParser
from swbf.parsers.cfg import CfgParser
from util.diagnostic import WarningMessage
from util.enumeration import Enum
from util.logging import get_logger


class FxWarning(WarningMessage):
    TOPIC = 'FX'

class FxParser(CfgParser):
    Extension = Ext.Fx

    class Call(Enum):
        Alpha = 'Alpha'
        Accelerate = 'Accelerate'
        Angle = 'Angle'
        BlendMode = 'BlendMode'
        Blue = 'Blue'
        BorderDiffuseColor = 'BorderDiffuseColor'
        BoundingRadius = 'BoundingRadius'
        BurstCount = 'BurstCount'
        BurstDelay = 'BurstDelay'
        BumpMapTextures = 'BumpMapTextures'
        Circle = 'Circle'
        Color = 'Color'
        ConstantBlend = 'ConstantBlend'
        DisableLowRes = 'DisableLowRes'
        DownSizeFactor = 'DownSizeFactor'
        DustVelocity = 'DustVelocity'
        Effect = 'Effect'
        Enable = 'Enable'
        FadeInTime = 'FadeInTime'
        FlareOutSize = 'FlareOutSize'
        FresnelMinMax = 'FresnelMinMax'
        GammaBrightness = 'GammaBrightness'
        GammaContrast = 'GammaContrast'
        Green = 'Green'
        Geometry = 'Geometry'
        Height = 'Height'
        Hue = 'Hue'
        HaloInnerRing = 'HaloInnerRing'
        HaloMiddleRing = 'HaloMiddleRing'
        HaloOutterRing = 'HaloOutterRing'
        InheritVelocityFactor = 'InheritVelocityFactor'
        InitialFlareOutAlpha = 'InitialFlareOutAlpha'
        LifeTime = 'LifeTime'
        LightAzimAndElev = 'LightAzimAndElev'
        LODDecimation = 'LODDecimation'
        MainTexture = 'MainTexture'
        MaxDiffuseColor = 'MaxDiffuseColor'
        MaxGodraysInWorld = 'MaxGodraysInWorld'
        MaxGodraysOnScreen = 'MaxGodraysOnScreen'
        MaxLodDist = 'MaxLodDist'
        MaxParticles = 'MaxParticles'
        MaxViewDistance = 'MaxViewDistance'
        MinLodDist = 'MinLodDist'
        MinDiffuseColor = 'MinDiffuseColor'
        Mode = 'Mode'
        Model = 'Model'
        Next = 'Next'
        NormalMapTextures = 'NormalMapTextures'
        NumFlareOuts = 'NumFlareOuts'
        Offset = 'Offset'
        OffsetAngle = 'OffsetAngle'
        OceanEnable = 'OceanEnable'
        OscillationEnable = 'OscillationEnable'
        ParticleDensity = 'ParticleDensity'
        ParticleEmitter = 'ParticleEmitter'
        ParticleSize = 'ParticleSize'
        PatchDivisions = 'PatchDivisions'
        PC = 'PC'
        Position = 'Position'
        PositionScale = 'PositionScale'
        PositionValue = 'PositionValue'
        PositionX = 'PositionX'
        PositionY = 'PositionY'
        PositionZ = 'PositionZ'
        PS2 = 'PS2'
        Range = 'Range'
        Reach = 'Reach'
        Red = 'Red'
        RefractionColor = 'RefractionColor'
        ReflectionColor = 'ReflectionColor'
        RotationVelocity = 'RotationVelocity'
        Rotation = 'Rotation'
        Saturation = 'Saturation'
        Scale = 'Scale'
        Size = 'Size'
        SoundName = 'SoundName'
        SparkLength = 'SparkLength'
        Spawner = 'Spawner'
        SpeckleAmbientColor = 'SpeckleAmbientColor'
        SpeckleCoordShift = 'SpeckleCoordShift'
        SpeckleScrollSpeed = 'SpeckleScrollSpeed'
        SpeckleSpecularColor = 'SpeckleSpecularColor'
        SpeckleTextures = 'SpeckleTextures'
        SpeckleTile = 'SpeckleTile'
        SpecularColor = 'SpecularColor'
        SpecularMaskTextures = 'SpecularMaskTextures'
        SpecularMaskScrollSpeed = 'SpecularMaskScrollSpeed'
        SpecularMaskTile = 'SpecularMaskTile'
        SpikeColor = 'SpikeColor'
        SpikeSize = 'SpikeSize'
        Spread = 'Spread'
        StartDelay = 'StartDelay'
        StartRotation = 'StartRotation'
        SunFlare = 'SunFlare'
        Transformer = 'Transformer'
        Texture = 'Texture'
        Tile = 'Tile'
        Type = 'Type'
        UnderwaterColor = 'UnderwaterColor'
        Value = 'Value'
        Velocity = 'Velocity'
        VelocityScale = 'VelocityScale'
        WaterRingColor = 'WaterRingColor'
        WaterSplashColor = 'WaterSplashColor'
        WaterWakeColor = 'WaterWakeColor'
        XBOX = 'XBOX'
        Yellow = 'Yellow'

    def __init__(self, filepath: Path, tokens: list[Token] = None, logger: Logger = get_logger(__name__)):
        SwbfTextParser.__init__(self, filepath=filepath, tokens=tokens, logger=logger)

        CfgParser.Call = FxParser.Call


if __name__ == '__main__':
    FxParser.cmd_helper()
