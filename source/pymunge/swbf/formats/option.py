import re
import sys
from pathlib import Path
from io import FileIO, StringIO
from parxel.lexer import Lexer
from parxel.parser import Parser
from parxel.nodes import Node, Document, LexicalNode
from parxel.token import TK, Token
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class Switch(LexicalNode):
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Option.Switch:
            logger.warning(f'Switch "{self.value}" is not known.')


class Value(LexicalNode):
    RE_NUMBER = re.compile(r'\d+(\.\d+)?')
    def __init__(self, tokens: list[Token], parent: Node = None):
        LexicalNode.__init__(self, tokens, parent)

        self.value: str = self.raw().strip()

        if self.value not in Option.Value and not re.match(Value.RE_NUMBER, self.value):
            logger.warning(f'Value "{self.value}" is not known.')
        
        if isinstance(self.parent, Switch):
            valid_values = Option.SwitchValue[self.parent.value]

            if isinstance(valid_values, list):
                if self.value not in valid_values:
                    logger.warning(f'Value "{self.value}" is not a valid value for {self.parent.value}.')
            else:
                if not re.match(Option.SwitchValue[self.parent.value], self.value):
                    logger.warning(f'Value "{self.value}" is not a valid value for {self.parent.value}.')


class Option(Document, Parser):
    class Switch(Enum):
        AdditiveEmissive = 'additiveemissive'
        Bump = 'bump'
        BumpMap = 'bumpmap'
        BumpScale = 'bumpscale'
        BorderColor = 'bordercolor'
        Compress = 'compress'
        Cubemap = 'cubemap'
        Depth = 'depth'
        DetailBias = 'detailbias'
        DoNotMergeCollision = 'donotmergecollision'
        ForceFormat = 'forceformat'
        ForceMip = 'forcemip'
        Format = 'format'
        HiResShadow = 'hiresshadow'
        Keep= 'keep'
        KeepMaterial = 'keepmaterial'
        Maps = 'maps'
        MipDistance = 'mipdistance'
        NoCollision = 'nocollision'
        NoGameModel = 'nogamemodel'
        RightHanded = 'righthanded'
        SoftSkin = 'softskin'
        SoftSkinShadow = 'softskinshadow'
        VertexLighting = 'vertexlighting'
        Volume = 'volume'
        _4Bit = '4bit'
        _8Bit = '8bit'
        _32Bit = '32bit'

    class Value(Enum):
        A4R4G4B4 = 'a4r4g4b4'
        A8R8G8B8 = 'a8r8g8b8'
        OverrideTexture = 'override_texture'
        R5G6B5 = 'r5g6b5'
        V8U8 = 'v8u8'
        _0x80808080 = '0x80808080'
    
    SwitchValue = {
        Switch.AdditiveEmissive : [],
        Switch.Bump : [],
        Switch.BumpMap : [],
        Switch.BumpScale : re.compile(r'\d+.\d+'),
        Switch.BorderColor : ['0'],
        Switch.Compress : [],
        Switch.Cubemap : [],
        Switch.Depth : re.compile(r'\d+'),
        Switch.DetailBias : ['7'], # TODO
        Switch.DoNotMergeCollision : [],
        Switch.ForceFormat : [Value.A8R8G8B8, Value.V8U8],
        Switch.ForceMip : [Value._0x80808080],
        Switch.Format : [Value.A4R4G4B4, Value.A8R8G8B8, Value.R5G6B5],
        Switch.HiResShadow : [],
        Switch.Keep : [],
        Switch.KeepMaterial : [],
        Switch.Maps : ['1'], # TODO
        Switch.MipDistance : ['1'], # TODO
        Switch.NoCollision : [],
        Switch.NoGameModel : [],
        Switch.RightHanded : [],
        Switch.SoftSkin : [],
        Switch.SoftSkinShadow : [],
        Switch.VertexLighting : [],
        Switch.Volume : [],
        Switch._4Bit : [],
        Switch._8Bit : [],
        Switch._32Bit : [],
    }

    def __init__(self, filepath: Path, tokens: list[Token]):
        Document.__init__(self, filepath=filepath)
        Parser.__init__(self, filepath=filepath, tokens=tokens)

    def parse_format(self):
        while self:
            if self.get().type in TK.Whitespaces:
                self.discard()  # Discard whitespaces

            elif self.get().type == TK.Minus:
                self.discard() # '-'

                self.consume_until_any(TK.Whitespaces)

                switch = Switch(self.collect_tokens())
                self.enter_scope(switch)

                self.discard() # Discard whitespaces

                while self and self.get().type != TK.Minus:
                    self.consume_until_any(TK.Whitespaces)

                    tokens = self.collect_tokens()

                    if tokens:
                        value = Value(tokens, self.scope)
                        self.add_to_scope(value)

                    self.discard() # Discard whitespaces

                self.exit_scope()

            # Either skip or thow error
            else:
                logger.warning(f'Unrecognized token "{self.get()} ({self.tokens()})".')
                self.discard()
                # self.error(TK.Null)

        return self


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if path.is_file():
            opt = Option.read(filepath=path)
            opt.print()
        else:
            for file in path.rglob('*.option'):
                opt = Option.read(filepath=file)

    elif len(sys.argv) > 2:
        opt = Option.read(stream=sys.stdin)
    else:
        sys.exit(1)

    # TODO: Global exit code
    sys.exit(0)
