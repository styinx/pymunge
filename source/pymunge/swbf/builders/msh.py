from pathlib import Path

from pyglm import glm

from parxel.nodes import Node

from app.environment import MungeEnvironment as ENV
from swbf.builders.builder import Ext
from swbf.builders.builder import UcfbNode, int32_data, string_data, float32_array_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.parsers.msh import MshParser, MshChunk
from swbf.parsers.msh import Header, Mesh, SceneInformation, Name
from swbf.parsers.msh import Model, ModelType, ModelIndex, FlagsModel, ParentModel, TransformModel, Geometry, Envelope, SegmentHeader, WeightBones
from util.diagnostic import ErrorMessage


class ModelBuilderError(ErrorMessage):
    TOPIC = 'MSH'


class MissingMshChunk(ModelBuilderError):
    def __init__(self, node: type[MshChunk], filepath: Path):
        super().__init__(f'Missing MSH Chunk "{node.TYPE}" in file {filepath}')


class ModelChunk:
    INFO = 'INFO'
    NAME = 'NAME'
    NODE = 'NODE'
    PRNT = 'PRNT'
    XFRM = 'XFRM'


class ModelInfoProperty(UcfbNode):
    def __init__(self, magic: str, name: str, models: int, pad: bool = True):
        UcfbNode.__init__(self)

        self.magic: str = magic
        self.name: str = name
        self.models: int = models
        self.pad: str = ''

        self.name += '\0'

        if pad:
            alignment = len(self.name) % 4
            if alignment != 0:
                self.pad += '\0' * (4 - alignment)

        self.length: int = len(name) + 1 + 4 + len(self.pad)

    def __len__(self) -> int:
        # MAGIC , SIZE , (name , number)
        return 4 + 4 + self.length

    def data(self) -> bytes:
        return string_data(self.magic) + int32_data(self.length + 4) + string_data(self.name) + int32_data(self.models) + string_data(self.pad)


class ModelNode(Node):
    def __init__(self, model: Model):
        super().__init__()
        parent = model.find(ParentModel)
        self.name = model.find(Name).raw_name()
        self.type = model.find(ModelType).model_type
        self.parent = parent.raw_name() if parent else None
        self.index = model.find(ModelIndex).model_index
        self.model_transform = model.find(TransformModel)
        self.geometry = model.find(Geometry)
        self.is_enveloped = True if self.geometry != None and self.geometry.find(Envelope) != None else False
        self.is_deformer = False

        model_transform = model.find(TransformModel)
        if model_transform:
            q = glm.quat(*[0.0 if x == -0.0 else x for x in model_transform.rotation])

            rotation_matrix = glm.mat3_cast(q)
            #model_transforms += rotation_matrix.to_bytes()
            #model_transforms += float32_array_data(model_transform.translation)


class ModelBuilder(SwbfUcfbBuilder):
    Extension = Ext.Model

    def __init__(self, tree: MshParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Skeleton)

    def build(self):
        mesh = self.tree.find_nested(Mesh)

        if not mesh:
            ENV.Diag.report(MissingMshChunk(Mesh, self.tree.filepath))
            return self

        for scene_information in mesh.find_all(SceneInformation):
            pass

        model_root = None
        enveloped_names = []
        model_parents = []
        model_transforms = bytearray()

        model_tree = {}
        model_indices = {}

        # Build model tree
        for model in mesh.find_all(Model):
            model_node = ModelNode(model)
            model_tree[model_node.name] = model_node
            model_indices[model_node.index] = model_node

            if not model_node.parent:
                model_root = model

            else:
                model_tree[model_node.parent].add(model_tree[model_node.name])

        # Find enveloped models
        for index, node in model_indices.items():

            if not node.is_enveloped:
                continue

            envelope = node.geometry.find(Envelope)
            segments = node.geometry.find(SegmentHeader)
            weights = segments.find(WeightBones).weights

            weighted_bone_indices = [vertex[0] for weight in weights for vertex in weight if vertex[0] > 0 and vertex[1] > 0.0]

            for envl_index in weighted_bone_indices:
                modl_index = envelope.indices[envl_index]
                if model_indices[modl_index].name not in enveloped_names:
                    enveloped_names.append(model_indices[modl_index].name)

        def p(n, i=0):
            print(' ' * i, i, n.name, f'[{n.index}]' f'({n.type})')
            for c in n.children:
                p(c, i + 1)

        p(model_tree[model_root.find(Name).raw_name()])
        print(enveloped_names)

        info_property = ModelInfoProperty(ModelChunk.INFO, self.tree.filepath.stem, len(enveloped_names))
        self.add(info_property)

        enveloped_names = '\0'.join(enveloped_names)
        name_property = StringProperty(ModelChunk.NAME, enveloped_names)
        self.add(name_property)

        model_parents = '\0'.join(model_parents)
        parent_property = StringProperty(ModelChunk.PRNT, model_parents)
        self.add(parent_property)

        model_transforms = model_transforms
        transform_property = BinaryProperty(ModelChunk.XFRM, model_transforms)
        self.add(transform_property)

        modl = SwbfUcfbBuilder(self.tree, Magic.Model)

        modl_name_property = StringProperty(ModelChunk.NAME, self.tree.filepath.stem)
        modl.add(modl_name_property)

        modl_node = model_root.find(Name)
        modl_node_property = StringProperty(ModelChunk.NODE, modl_node.name)
        modl.add(modl_node_property)

        self.add(modl)

        return self
