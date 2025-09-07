from pathlib import Path

from app.environment import MungeEnvironment as ENV
from swbf.builders.builder import Ext
from swbf.builders.builder import int32_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.builders.fnv1a import fnv1a_32
from swbf.parsers.odf import OdfParser, OdfNode, Section, Key, Reference, Value
from util.diagnostic import ErrorMessage, WarningMessage


class ClassBuilderError(ErrorMessage):
    TOPIC = 'ODF'


class ClassBuilderWarning(WarningMessage):
    TOPIC = 'ODF'


class InconsistentSections(ClassBuilderError):
    def __init__(self, section_count: int, filepath: Path):
        if section_count > 2:
            text = 'More than 2'
        else:
            text = 'Less than 2'
        super().__init__(f'{text} sections found in file: "{filepath}"')


class MissingSection(ClassBuilderError):
    def __init__(self, name: str, filepath: Path):
        super().__init__(f'No "{name}" section found in file: "{filepath}"')


class MissingNode(ClassBuilderError):
    def __init__(self, node: type[OdfNode], filepath: Path):
        super().__init__(f'Missing Node "{node.__class__.__name__}" in file {filepath}')


class ClassChunk:
    BASE = 'BASE'
    PROP = 'PROP'
    TYPE = 'TYPE'


class ClassBuilder(SwbfUcfbBuilder):
    Extension = Ext.Class

    def __init__(self, tree: OdfParser):
        class_section: Section = tree.find(Section)

        if not class_section:
            ENV.Diag.report(MissingNode(Section, self.tree.filepath))

        if class_section.name == OdfParser.Section.ExplosionClass:
            magic = Magic.ExplosionClass
        elif class_section.name == OdfParser.Section.OrdnanceClass:
            magic = Magic.OrdnanceClass
        elif class_section.name == OdfParser.Section.WeaponClass:
            magic = Magic.WeaponClass
        else:
            magic = Magic.EntityClass

        SwbfUcfbBuilder.__init__(self, tree, magic)

    def build(self):
        sections = self.tree.find_all(Section)

        len_sections = len(sections)
        if len_sections > 2:
            ENV.Diag.report(InconsistentSections(len_sections, self.tree.filepath))
        elif len_sections < 2:
            ENV.Diag.report(InconsistentSections(len_sections, self.tree.filepath))

        class_section = [x for x in sections if x.name.find('Class') > -1]
        properties_section = [x for x in sections if x.name.find('Properties') > -1]

        # Write ...Class section
        if not class_section:
            ENV.Diag.report(MissingSection('...Class', self.tree.filepath))

        else:
            for key in class_section[0].find_all(Key):
                if key.name == OdfParser.Key.ClassLabel:

                    class_label = key.find(Value)

                    if not class_label:
                        ENV.Diag.report(ClassBuilderError(f'Missing class label in file: "{self.tree.filepath}"'))

                    else:

                        base_property = StringProperty(ClassChunk.BASE, class_label.raw_value())
                        self.add(base_property)

                        name_property = StringProperty(ClassChunk.TYPE, self.tree.filepath.stem)  # ODF name without Extension
                        self.add(name_property)

        # Write Properties section
        if not properties_section:
            ENV.Diag.report(MissingSection('Properties', self.tree.filepath))

        else:
            for key in properties_section[0].find_all(Key):
                # TODO: filter out duplicates and invalid props

                val = key.children[0]
                if isinstance(val, Reference):
                    magic = int32_data(fnv1a_32(key.name))
                    data = (val.filepath.stem + chr(0)).encode('utf-8')

                    prop = BinaryProperty(ClassChunk.PROP, magic + data)
                    self.add(prop)

                elif isinstance(val, Value):
                    if val.value != '""':
                        magic = int32_data(fnv1a_32(key.name))
                        data = (val.raw_value() + chr(0)).encode('utf-8')

                        prop = BinaryProperty(ClassChunk.PROP, magic + data)
                        self.add(prop)

                else:
                    ENV.Diag.report(ClassBuilderError(f'Unexpected Node "{key.__class__.__name__}".'))

        return self
