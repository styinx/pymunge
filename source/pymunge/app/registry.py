import pickle
from pathlib import Path
from queue import Queue

from parxel.nodes import Document

from util.diagnostic import Diagnostic, ErrorMessage
from util.logging import ScopedLogger, get_logger


class BuildDependency(Document):
    def __init__(self, filepath, parent = None):
        super().__init__(filepath, parent)
        self.ts = filepath.stat().st_mtime


class FileRegistry:
    """
    The :class:`` stores the munge dependencies. Upon initialization
    it checks if the input files are up to date or need remunging.
    """

    TOOL_FILTER = {
    }

    class UnresolvedDependency(ErrorMessage):
        TOPIC = 'REG'

        def __init__(self, filepath: Path):
            super().__init__(f'Unresolved filepath {filepath}! Munge result may not work as expected.')

    def __init__(self, args, diagnostic: Diagnostic, logger: ScopedLogger = get_logger(__name__)):
        self.dependencies = {}
        self.munge_queue = Queue()

        self.diagnostic = diagnostic
        self.logger = logger

        self.source : Path = args.munge.source
        self.target : Path = args.munge.target

        self.munge_dir = self.target / '_munged'

        if not self.munge_dir.exists():
            self.munge_dir.mkdir(parents=True)

    def collect_munge_files(self, source_filters):
        """
        Adds files based on the configured filter list to the munge queue.
        """

        self.logger.info(f'Processing "{self.source}"')
        for source_filter in source_filters:
            for entry in self.source.rglob(f'*.{source_filter}'):
                self.munge_queue.put(entry)
        self.logger.info(f'Results written to "{self.target}"')

    def register_file(self, filepath: Path):
        """
        Adds a file path to the registry. A registered file can be referenced as dependency.
        """

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
        """
        Links two file paths as dependencies.
        """

        src_dep = self.register_file(src)
        dst_dep = self.register_file(dst)
        if src_dep and dst_dep:
            src_dep.add(dst_dep)

    def store_dependencies(self):
        """
        Write the current dependency tree for incremental builds.
        Up-to-date dependencies are not remunged.
        """

        # No history if single file is munged.
        if self.target.is_file():
            return

        with (self.target / '.pymunge.graph').open('wb+') as graph_file:
            pickle.dump(self.dependencies, graph_file)

            self.logger.info(f'Store dependency file: "{graph_file.name}"')

    def load_dependencies(self):
        """
        Load build dependencies if a previous run was made in the target folder.
        """

        # No history if single file was munged.
        if self.target.is_file():
            return

        graph_file = (self.target / '.pymunge.graph')

        if graph_file.exists():
            self.logger.info(f'Load dependency file: "{graph_file}"')

            self.dependencies = pickle.load(graph_file.open('rb'))

            for filepath, dependency in self.dependencies.items():
                if Path(filepath).stat().st_mtime != dependency.ts:
                    self.logger.debug(f'{filepath} is not up to date')

