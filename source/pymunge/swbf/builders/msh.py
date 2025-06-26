from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.builders.builder import UcfbNode, int32_data, string_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.parsers.msh import MshParser, MshChunk
from swbf.parsers.msh import Header, Mesh, SceneInformation, Model, ModelType, Name, FlagsModel, ParentModel
from util.diagnostic import ErrorMessage


class ModelBuilderError(ErrorMessage):
    scope = 'MSH'


class MissingMshChunk(ModelBuilderError):
    def __init__(self, node: type[MshChunk], filepath: Path):
        super().__init__(f'Missing MSH Chunk "{node.type}" in file {filepath}')


class ModelChunk:
    INFO = 'INFO'
    NAME = 'NAME'


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


class ModelBuilder(SwbfUcfbBuilder):
    extension = 'model'

    def __init__(self, tree: MshParser):
        SwbfUcfbBuilder.__init__(self, tree, Magic.Skeleton)

    def build(self):
        mesh = self.tree.find_nested(Mesh)

        if not mesh:
            ENV.Diag.report(MissingMshChunk(Mesh, self.tree.filepath))

        for scene_information in mesh.find_all(SceneInformation):
            pass

        exporting_models = []
        for model in mesh.find_all(Model):
            model_name = model.find(Name)
            model_type = model.find(ModelType)

            if not model_name:
                ENV.Diag.report(MissingMshChunk(Name, self.tree.filepath))
            if not model_type:
                ENV.Diag.report(MissingMshChunk(ModelType, self.tree.filepath))

            if model_name and model_type:
                if not model_name.name.startswith('p_') \
                    and model_name.name.find('_lowrez') == -1 \
                    and model_type.model_type != ModelType.ShadowVolume:

                    exporting_models.append(model_name.name.replace('\0', ''))

        info_property = ModelInfoProperty(ModelChunk.INFO, self.tree.filepath.stem, len(exporting_models))
        self.add(info_property)

        model_names = '\0'.join(exporting_models)
        print(model_names)
        name_property = StringProperty(ModelChunk.NAME, model_names)
        self.add(name_property)

        return self
