import pickle
from pathlib import Path
from queue import Queue

from parxel.nodes import Document

from util.diagnostic import Diagnostic, ErrorMessage, WarningMessage
from util.logging import ScopedLogger, get_logger
from version import TUPLE as VERSION_TUPLE


class BuildDependency(Document):
    def __init__(self, filepath, parent = None, unmunged: bool = True):
        super().__init__(filepath, parent)
        self.ts = 0 if unmunged else filepath.stat().st_mtime


class FileRegistry:
    """
    The :class:`` stores the munge dependencies. Upon initialization
    it checks if the input files are up to date or need remunging.
    """

    class UnresolvedDependency(ErrorMessage):
        TOPIC = 'REG'

        def __init__(self, filepath: Path):
            super().__init__(f'Unresolved filepath {filepath}! Munge result may not work as expected.')

    class VersionMismatch(WarningMessage):
        TOPIC = 'REG'

        def __init__(self, version: tuple):
            super().__init__(f'Version of cached file "{version}" is incompatible with "{VERSION_TUPLE}"! Cached file is ignored.')

    def __init__(self, source: Path, target: Path, diagnostic: Diagnostic, logger: ScopedLogger = get_logger(__name__)):
        self.registered_files = {} # TODO: Maybe rename to source_files
        self.munged_files = {}
        self.munge_queue = Queue()

        self.diagnostic = diagnostic
        self.logger = logger

        self.source : Path = source
        self.target : Path = target

        self.munge_dir = self.target / '_munged'

        if not self.munge_dir.exists():
            self.munge_dir.mkdir(parents=True)

    def collect_munge_files(self, source_filters):
        """
        Adds files based on the configured filter list to the munge queue.
        """

        if self.source.is_dir():
            for source_filter in source_filters:
                for entry in self.source.rglob(f'*.{source_filter}'):
                    self.register_file(entry)

        else:
            self.register_file(self.source)

        for filepath, dependency in self.registered_files.items():
            if Path(filepath).stat().st_mtime != dependency.ts:
                self.munge_queue.put(filepath)
                self.logger.debug(f'{filepath} is not up to date')
            else:
                self.logger.debug(f'{filepath} is up to date')

    def register_file(self, filepath: Path, unmunged: bool = True):
        """
        Adds a file path to the registry. A registered file can be referenced as dependency.
        """

        # TODO: Must this be made thread-safe?

        if not filepath.exists():
            self.diagnostic.report(FileRegistry.UnresolvedDependency(filepath))

        else:
            dep = BuildDependency(filepath=filepath, unmunged=unmunged)
            if filepath not in self.registered_files:
                self.registered_files[filepath] = dep
                self.logger.debug(f'Register file: {dep.filepath}')
                # TODO: Add to munge queue if it matches the source_filters
            return dep

        return None

    def add_link(self, src: Path, dst: Path):
        """
        Links two file paths.
        """

        src_dep = self.register_file(src)
        dst_dep = self.register_file(dst)
        if src_dep and dst_dep:
            src_dep.add(dst_dep)

    def mark_munged(self, filepath: Path):
        # TODO: Should be made thread-safe since file can be referenced more than once.
        self.munged_files[filepath] = True
        self.registered_files[filepath].ts = Path(filepath).stat().st_mtime

    def store_dependencies(self):
        """
        Write build information for future runs.
        """

        if self.target.is_file():
            graph_file_path = (self.target.parent / '.pymunge.graph')
        else:
            graph_file_path = (self.target / '.pymunge.graph')

        with (graph_file_path).open('wb+') as graph_file:
            pickle.dump({
                'version': VERSION_TUPLE,
                'munged_files': self.munged_files,
                'registered_files': self.registered_files,
                'source': self.source,
                'target': self.target,
            }, graph_file)

            self.logger.info(f'Store dependency file: "{graph_file_path}"')

    def load_dependencies(self):
        """
        Load build information from previous run.
        """

        if self.target.is_file():
            graph_file_path = (self.target.parent / '.pymunge.graph')
        else:
            graph_file_path = (self.target / '.pymunge.graph')

        if graph_file_path.exists():
            self.logger.info(f'Load dependency file: "{graph_file_path}"')
            graph_file = pickle.load(graph_file_path.open('rb'))

            source = graph_file['source']
            target = graph_file['target']

            if source == self.source and target == self.target:

                version = graph_file['version']

                if version != VERSION_TUPLE:
                    self.diagnostic.report(FileRegistry.VersionMismatch(version))

                self.munged_files = graph_file['munged_files']
                self.registered_files = graph_file['registered_files']

                for filepath, registered_file in self.registered_files.items():
                    file = Path(filepath)

                    if file.exists():
                        # File needs remunging
                        if file.stat().st_mtime != registered_file.ts:
                            registered_file.ts = 0
                            if filepath in self.munged_files:
                                self.munged_files[filepath] = False

                    else:
                        del self.registered_files[file]
