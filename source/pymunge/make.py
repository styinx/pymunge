from argparse import ArgumentParser
from build import ProjectBuilder
from datetime import datetime
from os import getcwd
from pathlib import Path
from subprocess import run, PIPE

from version import MAJOR, MINOR, PATCH, BRANCH, HASH


SOURCE_DIR = Path(__file__).parent
ROOT_DIR = SOURCE_DIR.parent.parent


VERSION_TEMPLATE = str(
    'MAJOR: int = {MAJOR:d}\n'          # Number of releases
    'MINOR: int = {MINOR:d}\n'          # Number of features (MRs or PRs)
    'PATCH: int = {PATCH:d}\n'          # Number of commits since HASH
    'HASH: str = \'{HASH:s}\'\n'
    'DATE: str = \'{DATE:s}\'\n'
    'BRANCH: str = \'{BRANCH:s}\'\n'
    'NUMBER: tuple[int, int, int] = ({MAJOR}, {MINOR:d}, {PATCH:d})\n'
    'STRING: str = \'{MAJOR:02d}.{MINOR:02d}.{PATCH:06d}_{HASH:s}_{BRANCH:s}_{DATE:s}\'\n'
)


class Git:
    def __init__(self, path: Path = Path()):
        self.args = []
        self.cwd = path

        if not self.cwd.name:
            self.cwd = Path(getcwd())

    def _run(self, *args):
        result = run(
            ['git'] + list(args),
            cwd=self.cwd,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def add(self, *files: str) -> str:
        return self._run('add', ' '.join(files))

    def branch(self) -> str:
        return self._run('rev-parse', '--abbrev-ref', 'HEAD')

    def commits(self, source: str, target: str) -> int:
        return int(self._run('rev-list', '--count', f'{source}..{target}'))

    def commit(self, msg: str) -> str:
        return self._run('commit', '-m', msg)

    def hash(self, short: bool = True) -> str:
        return self._run('rev-parse', '--short' if short else '', 'HEAD')

    def push(self, remote: str) -> str:
        return self._run('push', remote)

    def tag(self, tag: str, remote: str) -> str:
        tag_msg = self._run('tag', tag)
        push_msg = self._run('push', remote, tag)
        return tag_msg, push_msg


if __name__ == '__main__':
    parser = ArgumentParser()

    actions = parser.add_subparsers(dest='action')

    build_action = actions.add_parser('build')
    build_action.add_argument('-d', '--deploy', action='store_true', default=False)

    git_action = actions.add_parser('git')
    git_action.add_argument('-a', '--add', type=str, nargs='+')
    git_action.add_argument('-c', '--commit', type=str)
    git_action.add_argument('-p', '--push', action='store_true', default=False)
    git_action.add_argument('-t', '--tag', action='store_true', default=False)

    version_action = actions.add_parser('version')
    version_action.add_argument('-i', '--increment', type=str, choices=['major', 'minor'])
    version_action.add_argument('-s', '--sync-version', action='store_true', default=False)

    args = parser.parse_args()

    git = Git()

    if args.action == 'version':
        if args.increment:
            if args.increment == 'major':
                MAJOR += 1
            elif args.increment == 'minor':
                MINOR += 1

        if args.sync_version:
            PATCH += git.commits(HASH, git.hash())
            BRANCH = git.branch()
            HASH = git.hash(short=True)
            DATE = datetime.now().strftime('%Y-%m-%d-%H-%M%z')

            with open(SOURCE_DIR / 'version.py', 'w+') as version_file:
                version_file.write(VERSION_TEMPLATE.format(
                    MAJOR=MAJOR,
                    MINOR=MINOR,
                    PATCH=PATCH,
                    HASH=HASH,
                    DATE=DATE,
                    BRANCH=BRANCH,
                ))
                print(f'{MAJOR:02d}.{MINOR:02d}.{PATCH:06d}_{HASH:s}_{BRANCH:s}_{DATE:s}')

    if args.action == 'git':
        if args.add:
            git.add(args.add)
        if args.commit:
            git.commit(args.commit)
        if args.push:
            git.push('origin')
        if args.tag:
            git.tag(f'v{MAJOR}.{MINOR}', 'origin')

    if args.action == 'build':
        ProjectBuilder(ROOT_DIR).build('wheel', output_directory='build')

        if args.deploy:
            run(
                args=['python', '-m', 'twine', 'upload', '--repository', 'pypi', 'dist/*'],
                check=True,
                cwd=ROOT_DIR
            )

