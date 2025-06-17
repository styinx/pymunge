from app.environment import MungeEnvironment
from swbf.builders.builder import int32_data
from swbf.builders.builder import StringProperty, BinaryProperty
from swbf.builders.builder import Magic, SwbfUcfbBuilder
from swbf.builders.fnv1a import fnv1a_32
from swbf.parsers.odf import OdfParser, Section, Key, Reference, Value
from util.diagnostic import ErrorMessage


class OdfBuilderError(ErrorMessage):
    scope = 'ODF'


class Class(SwbfUcfbBuilder):

    def __init__(self, tree: OdfParser):
        magic: str = Magic.EntityClass
        section: Section = tree.children[0]
        odf_type: str = section.name

        if odf_type == OdfParser.Section.ExplosionClass:
            magic = Magic.ExplosionClass
        elif odf_type == OdfParser.Section.OrdnanceClass:
            magic = Magic.OrdnanceClass
        elif odf_type == OdfParser.Section.WeaponClass:
            magic = Magic.WeaponClass

        SwbfUcfbBuilder.__init__(self, tree, magic)

    def build(self):
        geom_name_skipped = False

        try:

            it = self.tree.walk()

            while it:

                node = next(it)

                if isinstance(node, Key):

                    if node.name == OdfParser.Key.ClassLabel:
                        class_label = next(it)

                        if not isinstance(class_label, Value):
                            raise Exception('TODO')

                        base_property = StringProperty('BASE', class_label.value.replace('"', ''))
                        self.add(base_property)

                        name_property = StringProperty('TYPE', self.tree.filepath.stem)  # odf name
                        self.add(name_property)

                    else:

                        # TODO: filter out duplicates and invalid props

                        # Filter out duplicated GeometryName
                        if not geom_name_skipped and node.name == OdfParser.Key.GeometryName:
                            next(it)
                            geom_name_skipped = True
                            continue

                        val = next(it)
                        if isinstance(val, Reference):
                            prop = BinaryProperty(
                                'PROP',
                                int32_data(fnv1a_32(node.name)) +
                                (val.filepath.stem.replace('"', '') + chr(0)).encode('utf-8')
                            )
                            self.add(prop)

                        elif isinstance(val, Value):
                            if val.value != '""':
                                prop = BinaryProperty(
                                    'PROP',
                                    int32_data(fnv1a_32(node.name)) + (val.value.replace('"', '') + chr(0)).encode('utf-8')
                                )
                                print(prop.buffer)
                                self.add(prop)

                        else:
                            error = f'Unexpected Node "{node.__class__.__name__}".'
                            MungeEnvironment.Diagnostic.report(OdfBuilderError(error))
                            raise Exception(error)

        except StopIteration:
            pass

        return self
