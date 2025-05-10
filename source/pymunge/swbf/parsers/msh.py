from pathlib import Path
from struct import unpack
import sys
from logging import Logger

from parxel.nodes import Node, BinaryNode
from parxel.parser import BinaryParser
from parxel.token import TK, Token

from app.registry import FileRegistry, Dependency
from swbf.parsers.format import BinaryFormat
from util.logging import get_logger
from util.enum import Enum


logger = get_logger(__name__)


class MshNode(BinaryNode):
    def __init__(self, buffer: bytes, parent: Node = None):
        super().__init__(buffer, parent)

        self.chunk_buffer = BinaryParser(buffer=buffer)

        self.chunk_name : str = self.chunk_buffer.string(4)
        self.chunk_length : int = self.chunk_buffer.int32()


class Header(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


# Level 1


class Animation(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


class BlendFactor(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


class ClosingChunk(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


class Mesh(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


class ShadowVolume(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


class Skeleton(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)


# Level 2


class Camera(MshNode):
    pass


class AnimationCycle(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.num_animations: int = self.chunk_buffer.int32()

        self.animations = []
        for _ in range(self.num_animations):
            animation_name: str = self.chunk_buffer.string(64)
            fps: float = self.chunk_buffer.float32()
            first_frame: float = self.chunk_buffer.float32()
            last_frame: float = self.chunk_buffer.float32()
            self.animations.append((animation_name, fps, first_frame, last_frame))


class Keyframes(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.num_bones: int = self.chunk_buffer.int32()

        self.keyframes = []
        for _ in range(self.num_bones):
            crc: int = self.chunk_buffer.int32()
            keyframe_type: int = self.chunk_buffer.int32()
            num_translation_frames: int = self.chunk_buffer.int32()
            num_rotation_frames: int = self.chunk_buffer.int32()
            translation_frame_index: int = self.chunk_buffer.int32()
            translation: list[float] = self.chunk_buffer.float32_array(3)
            rotation_frame_index: int = self.chunk_buffer.int32()
            rotation: list[float] = self.chunk_buffer.float32_array(4)
            self.keyframes.append((
                crc,
                keyframe_type,
                num_translation_frames,
                num_rotation_frames,
                translation_frame_index,
                translation,
                rotation_frame_index,
                rotation
            ))


class Material(MshNode):
    pass


class Model(MshNode):
    pass


class SceneInformation(MshNode):
    pass


# Level 3


class MaterialData(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.diffuse_color : list[float] = self.chunk_buffer.float32_array(4)
        self.specular_color : list[float] = self.chunk_buffer.float32_array(4)
        self.ambient_color : list[float] = self.chunk_buffer.float32_array(4)
        self.specular_sharpness : float = self.chunk_buffer.float32()


class Geometry(MshNode):
    pass


# Level 4


class Strip(MshNode):
    pass


# Leaves


class Attributes(MshNode):
    Emissive = 1
    Glow = 2
    SingleTransparency = 4
    DoubleTransparency = 8
    HardEdgeTransparency = 16
    PerPixelLightning = 32
    AdditiveTransparency = 64
    Specular = 128

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.sum: int = self.chunk_buffer.advance(1)[0]
        self.render_type: int = self.chunk_buffer.advance(1)[0]
        self.data0: int = self.chunk_buffer.advance(1)[0]
        self.data1: int = self.chunk_buffer.advance(1)[0]


class BoundingBox(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.rotation: list[float] = self.chunk_buffer.float32_array(4)
        self.center: list[float] = self.chunk_buffer.float32_array(3)
        self.extension: list[float] = self.chunk_buffer.float32_array(3)
        self.radius: float = self.chunk_buffer.float32()


class Data(MshNode):
    pass


class Flags(MshNode):
    pass


class Frame(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.frame_start: int = self.chunk_buffer.int32()
        self.frame_end: int = self.chunk_buffer.int32()
        self.fps: float = self.chunk_buffer.float32()


class Name(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.name: str = self.chunk_buffer.string(self.chunk_length)


class ModelIndex(MshNode):
    pass


class ModelType(MshNode):
    pass


class Parent(MshNode):
    pass


class Texture(MshNode):

    def __init__(self, buffer: bytes, parent: Node = None):
        MshNode.__init__(self, buffer, parent)

        self.name: str = self.chunk_buffer.string(self.chunk_length)


class Transform(MshNode):
    pass


class Msh(BinaryFormat):

    class Chunk:
        # Level 0
        HEDR = 'HEDR'

        # Level 1
        ANM2 = 'ANM2'
        BLN2 = 'BLN2'
        CL1L = 'CL1L'
        MSH2 = 'MSH2'
        SHV0 = 'SHV0'
        SKL2 = 'SKL2'

        # Level 2
        CAMR = 'CAMR'
        CYCL = 'CYCL'
        KFR3 = 'KFR3'
        MATL = 'MATL'
        MODL = 'MODL'
        SINF = 'SINF'

        # Level 3
        GEOM = 'GEOM'
        MATD = 'MATD'
        SWCI = 'SWCI'

        # Level 4
        CLTH = 'CLTH'
        SEGM = 'SEGM'

        # Level 5
        STRP = 'STRP'

        # Leaves
        ATRB = 'ATRB'
        BBOX = 'BBOX'
        BPRS = 'BPRS'
        CLRB = 'CLRB'
        CLRL = 'CLRL'
        CMSH = 'CMSH'
        COLL = 'COLL'
        CPOS = 'CPOS'
        CPRS = 'CPRS'
        CTEX = 'CTEX'
        CUV0 = 'CUV0'
        DATA = 'DATA'
        ENVL = 'ENVL'
        FIDX = 'FIDX'
        FLGS = 'FLGS'
        FRAM = 'FRAM'
        FWGT = 'FWGT'
        NAME = 'NAME'
        NDXL = 'NDXL'
        NDXT = 'NDXT'
        NRML = 'NRML'
        MATI = 'MATI'
        MNDX = 'MNDX'
        MTYP = 'MTYP'
        POSL = 'POSL'
        PRNT = 'PRNT'
        SHDW = 'SHDW'
        SPRS = 'SPRS'
        TRAN = 'TRAN'
        TX0D = 'TX0D'
        UV0L = 'UV0L'
        WGHT = 'WGHT'

    def __init__(self, registry: FileRegistry, filepath: Path, buffer: bytes = None, logger : Logger = logger):
        BinaryFormat.__init__(self, registry=registry, filepath=filepath, buffer=buffer, logger=logger)

    def _parse_chunk(self, children: dict) -> BinaryNode | Node | None:
        child_name = self.string(4)
        child_len = self.int32()

        parse_child, child_type = children.get(child_name, (None, None))
        if parse_child:
            # TODO
            if child_name == Msh.Chunk.MATL:
                materials : int = self.int32()
            elif child_name == Msh.Chunk.STRP:

                offset = 8
                num_indices: int = self.int32()
                offset += 4

                polygons = []
                for _ in range(num_indices):
                    polygons.append(int.from_bytes(self.advance(2), 'little'))
                    offset += 2

                if (num_indices * 2) % 4 > 0:
                    self.advance((num_indices * 2 % 4))

            node = child_type(self.collect_bytes())
            self.scope.add(node)
            self.scope = node
            parse_child()

            return self.scope

        else:
            self.pos -= 8
            if hasattr(self.scope, 'parent') and self.scope.parent:
                self.scope = self.scope.parent

            return None

    def _parse_chunk_leaf(self, children: dict) -> BinaryNode | Node | None:
        child_name = self.string(4)
        child_len = self.int32()
        print(child_name)

        leaf_type = children.get(child_name, None)
        if leaf_type:
            self.advance(child_len)
            leaf = leaf_type(self.collect_bytes())
            self.scope.add(leaf)
            return self.scope

        else:
            self.pos -= 8
            if hasattr(self.scope, 'parent') and self.scope.parent:
                self.scope = self.scope.parent

            return None

    def parse_format(self):
        self._parse_chunk({
            Msh.Chunk.HEDR: (self.parse_hedr, Header)
        })

        return self

    # Level 0

    def parse_hedr(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.BLN2: BlendFactor,
            Msh.Chunk.SKL2: Skeleton,
            Msh.Chunk.SHV0: ShadowVolume,
        }):
            pass

        while self._parse_chunk({
            Msh.Chunk.ANM2: (self.parse_anm2, Animation),
            Msh.Chunk.MSH2: (self.parse_msh2, Mesh),
        }):
            pass

        self._parse_chunk_leaf({
            Msh.Chunk.CL1L: ClosingChunk,
        })

    # Level 1

    def parse_anm2(self):
        while self._parse_chunk({
            Msh.Chunk.CYCL: (self.parse_camr, AnimationCycle),
            Msh.Chunk.KFR3: (self.parse_matl, Keyframes),
        }):
            pass

    def parse_msh2(self):
        while self._parse_chunk({
            Msh.Chunk.CAMR: (self.parse_camr, Camera),
            Msh.Chunk.MATL: (self.parse_matl, Material),
            Msh.Chunk.MODL: (self.parse_modl, Model),
            Msh.Chunk.SINF: (self.parse_sinf, SceneInformation),
        }):
            pass

    def parse_shv0(self):
        pass

    def parse_skl2(self):
        pass

    # Level 2

    def parse_camr(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.DATA: Data,
            Msh.Chunk.NAME: Name,
        }):
            pass

    def parse_matl(self):
        while self._parse_chunk({
            Msh.Chunk.MATD: (self.parse_matd, MaterialData),
        }):
            pass

    def parse_modl(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.FLGS: Flags,
            Msh.Chunk.NAME: Name,
            Msh.Chunk.MNDX: ModelIndex,
            Msh.Chunk.MTYP: ModelType,
            Msh.Chunk.PRNT: Parent,
            Msh.Chunk.SWCI: MshNode,
            Msh.Chunk.TRAN: Transform
        }):
            pass

        while self._parse_chunk({
            Msh.Chunk.GEOM: (self.parse_geom, Geometry)
        }):
            pass

    def parse_sinf(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.BBOX: BoundingBox,
            Msh.Chunk.FRAM: Frame,
            Msh.Chunk.NAME: Name
        }):
            pass

    # Level 3

    def parse_geom(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.BBOX: BoundingBox,
            Msh.Chunk.ENVL: MshNode
        }):
            pass

        while self._parse_chunk({
            Msh.Chunk.CLTH: (self.parse_clth, MshNode),
            Msh.Chunk.SEGM: (self.parse_segm, MshNode)
        }):
            pass


    def parse_matd(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.ATRB: Attributes,
            Msh.Chunk.NAME: Name,
            Msh.Chunk.DATA: MshNode,
            Msh.Chunk.TX0D: Texture
        }):
            pass

    # Level 4

    def parse_segm(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.CLRB: MshNode,
            Msh.Chunk.CLRL: MshNode,
            Msh.Chunk.MATI: MshNode,
            Msh.Chunk.NDXL: MshNode,
            Msh.Chunk.NDXT: MshNode,
            Msh.Chunk.NRML: MshNode,
            Msh.Chunk.POSL: MshNode,
            Msh.Chunk.SHDW: MshNode,
            Msh.Chunk.UV0L: MshNode,
            Msh.Chunk.WGHT: MshNode,
        }):
            pass

        while self._parse_chunk({
            Msh.Chunk.STRP: (self.parse_strp, Strip)
        }):
            pass

    def parse_clth(self):
        while self._parse_chunk_leaf({
        }):
            pass

    # Level 5

    def parse_strp(self):
        while self._parse_chunk_leaf({
            Msh.Chunk.BBOX: BoundingBox,
            Msh.Chunk.FRAM: Frame,
            Msh.Chunk.NAME: Name
        }):
            pass


if __name__ == '__main__':
    Msh.cmd_helper()

    # TODO: Global exit code
    sys.exit(0)
