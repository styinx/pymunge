import pickle
from pathlib import Path

from util.diagnostic import Diagnostic, ErrorMessage
from util.logging import ScopedLogger, get_logger

from parxel.nodes import Document


class BuildDependency(Document):
    def __init__(self, filepath, parent = None):
        super().__init__(filepath, parent)
        self.ts = filepath.stat().st_mtime


class FileRegistry:
    """
    The :class:`` stores the munge dependencies. Upon initialization
    it checks if the input files are up to date or need remunging.
    """

    class UnresolvedDependency(ErrorMessage):
        TOPIC = 'REG'

        def __init__(self, filepath: Path):
            super().__init__(f'Unresolved filepath {filepath}! Munge result may not work as expected.')

    def __init__(self, args, diagnostic: Diagnostic, logger: ScopedLogger = get_logger(__name__)):
        self.dependencies = {}

        self.diagnostic = diagnostic
        self.logger = logger

        self.source : Path = args.munge.source
        self.target : Path = args.munge.target

    def register_file(self, filepath: Path):
        if not filepath.exists():
            self.diagnostic.report(FileRegistry.UnresolvedDependency(filepath))

        else:
            dep = BuildDependency(filepath=filepath)
            if filepath not in self.dependencies:
                self.dependencies[filepath] = dep
                self.logger.debug(f'Register file: {dep.filepath}')
            return dep

        return None

    def add_dependency(self, src: Path, dst: Path):
        src_dep = self.register_file(src)
        dst_dep = self.register_file(dst)
        if src_dep and dst_dep:
            src_dep.add(dst_dep)

    def store_dependencies(self):
        if self.target.is_file():
            return

        with (self.target / '.pymunge.graph').open('wb+') as graph_file:
            pickle.dump(self.dependencies, graph_file)

    def load_dependencies(self):
        if self.target.is_file():
            return

        graph_file = (self.target / '.pymunge.graph')

        if graph_file.exists():
            self.dependencies = pickle.load(graph_file.open('rb'))

            for filepath, dependency in self.dependencies.items():
                if Path(filepath).stat().st_mtime != dependency.ts:
                    self.logger.debug(f'{filepath} is not up to date')

