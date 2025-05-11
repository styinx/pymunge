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


class Chunk:
    def __init__(self, msh_stream: BinaryParser):
        self.chunk_name : str = msh_stream.string(4)
        self.chunk_length : int = msh_stream.int32()


class Header(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 1


class Animation(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BlendFactor(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClosingChunk(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Mesh(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ShadowVolume(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Skeleton(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 2


class Camera(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class AnimationCycle(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_animations: int = msh_stream.int32()

        self.animations = []
        for _ in range(self.num_animations):
            animation_name: str = msh_stream.string(64)
            fps: float = msh_stream.float32()
            first_frame: float = msh_stream.float32()
            last_frame: float = msh_stream.float32()
            self.animations.append((animation_name, fps, first_frame, last_frame))

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Keyframes(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_bones: int = msh_stream.int32()

        self.keyframes = []
        for _ in range(self.num_bones):
            crc: int = msh_stream.int32()
            keyframe_type: int = msh_stream.int32()
            num_translation_frames: int = msh_stream.int32()
            num_rotation_frames: int = msh_stream.int32()
            translation_frame_index: int = msh_stream.int32()
            translation: list[float] = msh_stream.float32_array(3)
            rotation_frame_index: int = msh_stream.int32()
            rotation: list[float] = msh_stream.float32_array(4)
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

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Material(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.materials : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Model(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class SceneInformation(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 3


class MaterialData(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Geometry(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Level 4


class ClothHeader(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class SegmentHeader(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)
        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Strip(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_indices: int = msh_stream.int32()
        self.polygons: list[int] = [msh_stream.int16() for _ in range(self.num_indices)]

        # Skip potential padding (2 * 16 bits per entry for 32 bit alignment)
        msh_stream.advance((self.num_indices * 2) % 4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


# Leaves


class Attributes(Chunk, BinaryNode):
    Emissive = 1
    Glow = 2
    SingleTransparency = 4
    DoubleTransparency = 8
    HardEdgeTransparency = 16
    PerPixelLightning = 32
    AdditiveTransparency = 64
    Specular = 128

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.sum: int = msh_stream.advance(1)[0]
        self.render_type: int = msh_stream.advance(1)[0]
        self.data0: int = msh_stream.advance(1)[0]
        self.data1: int = msh_stream.advance(1)[0]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BendConstraints(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_constraints: int = msh_stream.int32()
        self.constraints: list[list[int]]= [msh_stream.int16_array(2) for _ in range(self.num_constraints)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class BoundingBox(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.rotation: list[float] = msh_stream.float32_array(4)
        self.center: list[float] = msh_stream.float32_array(3)
        self.extension: list[float] = msh_stream.float32_array(3)
        self.radius: float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothMesh(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        # TODO: is it 3 or 4 elements?
        self.num_points: int = msh_stream.int32()
        self.constraints: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_points)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothTextureName(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothUvCoordinates(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_coordinates: int = msh_stream.int32()
        self.coordinates: list[list[float]]= [msh_stream.float32_array(2) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ClothVertecies(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_vertecies: int = msh_stream.int32()
        self.constraints: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_vertecies)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Collision(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        #TODO: name lengths, 64 for now

        self.num_collisions: int = msh_stream.int32()
        self.collision_name: str = msh_stream.string(64)
        self.parent_name: str = msh_stream.string(64)
        self.primitive_type: int = msh_stream.int32()
        self.data0: float = msh_stream.float32()
        self.data1: float = msh_stream.float32()
        self.data2: float = msh_stream.float32()

        # Padding
        msh_stream.advance(msh_stream.pos % 4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ColorVertex(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.colors: bytes = msh_stream.bytes(4)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ColorVertecies(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_colors: int = msh_stream.int32()
        self.colors: list[bytes] = [msh_stream.bytes(4) for _ in range(self.num_colors)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class CrossConstraints(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_coordinates: int = msh_stream.int32()
        self.coordinates: list[list[float]]= [msh_stream.float32_array(3) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class DataCamera(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        # TODO
        self._todo : bytes = msh_stream.advance(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class DataMaterial(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.diffuse_color : list[float] = msh_stream.float32_array(4)
        self.specular_color : list[float] = msh_stream.float32_array(4)
        self.ambient_color : list[float] = msh_stream.float32_array(4)
        self.specular_sharpness : float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Envelope(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_indices : int = msh_stream.int32()
        self.indices : list[int] = msh_stream.int32_array(self.num_indices)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FixPoints(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_points : int = msh_stream.int32()
        self.indices : list[int] = msh_stream.int32_array(self.num_indices)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FixPointWeights(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        # TODO: string size

        self.num_points : int = msh_stream.int32()
        self.weights : list[str] = [msh_stream.string(64) for _ in range(self.num_points)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class FlagsModel(Chunk, BinaryNode):
    Hidden = 1
    DynamicallyLit = 2
    RetainNormals = 4
    RenderAfterShadows = 8
    DontFlattenGeometry = 16
    PS2Optimize = 32

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.flags : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Frame(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.frame_start: int = msh_stream.int32()
        self.frame_end: int = msh_stream.int32()
        self.fps: float = msh_stream.float32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Name(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Normals(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_normals: int = msh_stream.int32()
        self.normals: list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_normals)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class MaterialIndex(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.material_index : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ModelIndex(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.model_index : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ModelType(Chunk, BinaryNode):
    Null = 0
    Dynamic = 1
    Cloth = 2
    Bone = 3
    Static = 4
    ShadowVolume = 6
    Destructable = 7

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.model_type : int = msh_stream.int32()

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ParentModel(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.name : str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Polygons(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        # TODO
        self.todo = msh_stream.bytes(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class PositionVertices(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_positions : int = msh_stream.int32()
        self.positions : list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_positions)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class ShadowMesh(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_vertices: int = msh_stream.int32()
        self.vertices: list[list[float]] = [msh_stream.float32_array(3) for _ in range(self.num_vertices)]
        self.num_edges: int = msh_stream.int32()
        self.edges: list[list[int]] = [msh_stream.int16_array(4) for _ in range(self.num_vertices)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class StretchConstraints(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_constraints: int = msh_stream.int32()
        self.constraints: list[list[int]] = [msh_stream.int16_array(2) for _ in range(self.num_constraints)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Texture(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.name: str = msh_stream.string(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class TransformModel(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.scale : list[float] = msh_stream.float32_array(3)
        self.rotation : list[float] = msh_stream.float32_array(4)
        self.translation : list[float] = msh_stream.float32_array(3)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class Triangles(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        # TODO
        self.todo = msh_stream.bytes(self.chunk_length)

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class UvCoordinates(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_coordinates : int = msh_stream.int32()
        self.coordinates : list[list[float]] = [msh_stream.float32_array(2) for _ in range(self.num_coordinates)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


class WeightBones(Chunk, BinaryNode):

    def __init__(self, msh_stream: BinaryParser, parent: Node = None):
        Chunk.__init__(self, msh_stream)

        self.num_weights : int = msh_stream.int32()
        self.weights : list[tuple[int, float]] = [(msh_stream.int32(), msh_stream.float32()) for _ in range(self.num_weights)]

        BinaryNode.__init__(self, msh_stream.collect_bytes(), parent)


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
        self.pos -= 8

        parse_children, child_type = children.get(child_name, (None, None))

        # The chunk is a valid child
        if child_type:
            node = child_type(self)
            self.scope.add(node)
        else:
            if hasattr(self.scope, 'parent') and self.scope.parent:
                self.scope = self.scope.parent
            return None

        # The chunk has children
        if parse_children:
            self.scope = node
            parse_children()
            return self.scope
        # The chunk is a leaf
        else:
            return self.scope

    def parse_format(self):
        self._parse_chunk({
            Msh.Chunk.HEDR: (self.parse_hedr, Header)
        })

        return self

    # Level 0

    def parse_hedr(self):
        while self._parse_chunk({
            Msh.Chunk.ANM2: (self.parse_anm2, Animation),
            Msh.Chunk.BLN2: (None, BlendFactor),
            Msh.Chunk.MSH2: (self.parse_msh2, Mesh),
            Msh.Chunk.SKL2: (None, Skeleton),
            Msh.Chunk.SHV0: (None, ShadowVolume),
            Msh.Chunk.CL1L: (None, ClosingChunk),
        }):
            pass

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
        while self._parse_chunk({
            Msh.Chunk.DATA: (None, DataCamera),
            Msh.Chunk.NAME: (None, Name),
        }):
            pass

    def parse_matl(self):
        while self._parse_chunk({
            Msh.Chunk.MATD: (self.parse_matd, MaterialData),
        }):
            pass

    def parse_modl(self):
        while self._parse_chunk({
            Msh.Chunk.FLGS: (None, FlagsModel),
            Msh.Chunk.GEOM: (self.parse_geom, Geometry),
            Msh.Chunk.NAME: (None, Name),
            Msh.Chunk.MNDX: (None, ModelIndex),
            Msh.Chunk.MTYP: (None, ModelType),
            Msh.Chunk.PRNT: (None, ParentModel),
            Msh.Chunk.SWCI: (None, BinaryNode),
            Msh.Chunk.TRAN: (None, TransformModel)
        }):
            pass

    def parse_sinf(self):
        while self._parse_chunk({
            Msh.Chunk.BBOX: (None, BoundingBox),
            Msh.Chunk.FRAM: (None, Frame),
            Msh.Chunk.NAME: (None, Name)
        }):
            pass

    # Level 3

    def parse_geom(self):
        while self._parse_chunk({
            Msh.Chunk.BBOX: (None, BoundingBox),
            Msh.Chunk.CLTH: (self.parse_clth, ClothHeader),
            Msh.Chunk.ENVL: (None, Envelope),
            Msh.Chunk.SEGM: (self.parse_segm, SegmentHeader)
        }):
            pass

    def parse_matd(self):
        while self._parse_chunk({
            Msh.Chunk.ATRB: (None, Attributes),
            Msh.Chunk.NAME: (None, Name),
            Msh.Chunk.DATA: (None, DataMaterial),
            Msh.Chunk.TX0D: (None, Texture)
        }):
            pass

    # Level 4

    def parse_segm(self):
        while self._parse_chunk({
            Msh.Chunk.CLRB: (None, ColorVertex),
            Msh.Chunk.CLRL: (None, ColorVertecies),
            Msh.Chunk.MATI: (None, MaterialIndex),
            Msh.Chunk.NDXL: (None, Polygons),
            Msh.Chunk.NDXT: (None, Triangles),
            Msh.Chunk.NRML: (None, Normals),
            Msh.Chunk.POSL: (None, PositionVertices),
            Msh.Chunk.SHDW: (None, ShadowMesh),
            Msh.Chunk.STRP: (self.parse_strp, Strip),
            Msh.Chunk.UV0L: (None, UvCoordinates),
            Msh.Chunk.WGHT: (None, WeightBones)
        }):
            pass

    def parse_clth(self):
        while self._parse_chunk({
            # TODO
            Msh.Chunk.BPRS: (None, BendConstraints),
            Msh.Chunk.CMSH: (None, ClothMesh),
            Msh.Chunk.COLL: (None, Collision),
            Msh.Chunk.CPOS: (None, ClothVertecies),
            Msh.Chunk.CPRS: (None, CrossConstraints),
            Msh.Chunk.CTEX: (None, ClothTextureName),
            Msh.Chunk.CUV0: (None, ClothUvCoordinates),
            Msh.Chunk.FIDX: (None, FixPoints),
            Msh.Chunk.FWGT: (None, FixPointWeights),
            Msh.Chunk.SPRS: (None, StretchConstraints)
        }):
            pass

    # Level 5

    def parse_strp(self):
        while self._parse_chunk({
            Msh.Chunk.BBOX: (None, BoundingBox),
            Msh.Chunk.FRAM: (None, Frame),
            Msh.Chunk.NAME: (None, Name)
        }):
            pass


if __name__ == '__main__':
    Msh.cmd_helper()

    # TODO: Global exit code
    sys.exit(0)
