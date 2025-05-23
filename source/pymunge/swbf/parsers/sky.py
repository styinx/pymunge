from pathlib import Path

from parxel.nodes import Node, LexicalNode
from parxel.token import TK, Token

from app.registry import FileRegistry
from swbf.parsers.format import TextFormat
from util.enum import Enum
from util.logging import get_logger

logger = get_logger(__name__)


class Comment(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.text: str = self.raw().strip()


class Block(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.header: str = self.raw().replace('(', '').replace(')', '').strip()

        if self.header not in Sky.Header:
            logger.warning(f'Block header "{self.header}" is not known.')


class Function(LexicalNode):

    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        function = self.raw().strip().replace(')', '').replace('(', ',').split(',')

        self.name: str = function[0]
        self.arguments: list[str] = function[1:]

        if self.name not in Sky.Function:
            logger.warning(f'Function name "{self.name}" is not known.')


class Sky(TextFormat):

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

    def __init__(self, registry: FileRegistry, filepath: Path, tokens: list[Token] = None, logger=logger):
        TextFormat.__init__(self, registry=registry, filepath=filepath, tokens=tokens, logger=logger)

    def parse_format(self):
        while self:
            if self.get().type in TK.Whitespaces:
                self.discard()  # Discard whitespaces

            # Comment
            elif self.get().type == TK.Minus:
                self.consume_strict(TK.Minus)

                self.consume_until(TK.LineFeed)

                comment = Comment(self.collect_tokens())
                self.add_to_scope(comment)

                self.discard()  # \n

            # Comment
            elif self.get().type == TK.Slash:
                self.consume_strict(TK.Slash)

                self.consume_until(TK.LineFeed)

                comment = Comment(self.collect_tokens())
                self.add_to_scope(comment)

                self.discard()  # \n

            # Begin Block
            elif self.get().type == TK.CurlyBracketOpen:
                self.discard()  # {

            # End Block
            elif self.get().type == TK.CurlyBracketClose:
                self.discard()  # }

                self.exit_scope()

            # Header or Function
            elif self.get().type == TK.Word:

                # We assume that the self format can't have nested blocks.

                if isinstance(self.scope, Sky):
                    self.consume_until(TK.ParanthesisClose)
                    self.next()

                    block = Block(self.collect_tokens())
                    self.enter_scope(block)

                else:
                    self.consume_until(TK.Semicolon)
                    self.next()

                    function = Function(self.collect_tokens())
                    self.add_to_scope(function)

            # Either skip or throw error
            else:
                logger.warning(f'Unrecognized token "{self.get()} ({self.tokens()})".')
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    Sky.cmd_helper()
