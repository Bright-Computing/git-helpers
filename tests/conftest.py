import subprocess
import pytest
from pathlib import Path

BIN_DIR = Path(__file__).parent.parent / 'bin'


def pytest_addoption(parser):
    parser.addoption('--work-dir', default=None, help='Root temp directory for fixtures and test repos')


@pytest.fixture(scope='session')
def work_dir(request):
    d = request.config.getoption('--work-dir')
    if d is None:
        pytest.exit(
            'Missing --work-dir. Run the suite via tests/run_tests.sh, '
            'which prepares fixtures and passes --work-dir automatically.',
            returncode=1,
        )
    return Path(d)



def cmd_info(result):
    """Format a CompletedProcess into a readable diagnostic block for assertion messages."""
    cmd = ' '.join(str(a) for a in result.args)
    return '\n'.join([
        f'$ {cmd}',
        f'exit: {result.returncode}',
        f'stdout:\n{result.stdout.rstrip()}',
        f'stderr:\n{result.stderr.rstrip()}',
    ])


def git(repo_dir, *args, check=True):
    return subprocess.run(
        ['git', *args],
        cwd=repo_dir,
        check=check,
        capture_output=True,
        text=True,
    )


def resolve_ref(repo_dir, ref):
    return git(repo_dir, 'rev-parse', ref).stdout.strip()


# Multiple tests may use the same fixture name; a counter ensures each gets
# its own subdirectory under work_dir/tests/ without collisions.
_repo_counter = 0


@pytest.fixture
def make_repo(work_dir):
    """Return a factory that creates a git repo from a .fi fixture file."""
    global _repo_counter
    _repo_counter += 1
    idx = _repo_counter

    def _make(fixture_name):
        repo_dir = work_dir / 'tests' / f'{idx}_{fixture_name}'
        repo_dir.mkdir(parents=True)
        git(repo_dir, 'init')
        git(repo_dir, 'config', 'user.email', 'test@test')
        git(repo_dir, 'config', 'user.name', 'Test')
        fi_path = work_dir / 'fixtures' / f'{fixture_name}.fi'
        with fi_path.open('rb') as f:
            subprocess.run(
                ['git', 'fast-import', '--quiet'],
                cwd=repo_dir, stdin=f, check=True, capture_output=True,
            )
        git(repo_dir, 'checkout', 'master')
        return repo_dir
    return _make


def git_cherry_pick(repo_dir, ref, branch):
    """Cherry-pick ref onto branch with -x annotation."""
    commit_hash = resolve_ref(repo_dir, ref)
    git(repo_dir, 'checkout', branch)
    git(repo_dir, 'cherry-pick', '-x', '--allow-empty', commit_hash)
    git(repo_dir, 'checkout', 'master')


def git_cherry_pick_merge(repo_dir, ref, mainline, branch):
    """Cherry-pick a merge commit onto branch, specifying the mainline parent index (1-based)."""
    commit_hash = resolve_ref(repo_dir, ref)
    git(repo_dir, 'checkout', branch)
    git(repo_dir, 'cherry-pick', '-m', str(mainline), '-x', '--allow-empty', commit_hash)
    git(repo_dir, 'checkout', 'master')


def bc_cherry_pick(repo_dir, commit_ref, *args):
    """Run git-bc-cherry-pick on commit_ref from the repo's current branch."""
    commit_hash = resolve_ref(repo_dir, commit_ref)
    result = subprocess.run(
        [BIN_DIR / 'git-bc-cherry-pick', *args, commit_hash],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    )
    print(cmd_info(result))
    return result


def set_origin_head(repo_dir, branch='master'):
    """Create refs/remotes/origin/{branch} and set refs/remotes/origin/HEAD to point to it."""
    commit = resolve_ref(repo_dir, branch)
    git(repo_dir, 'update-ref', f'refs/remotes/origin/{branch}', commit)
    git(repo_dir, 'symbolic-ref', 'refs/remotes/origin/HEAD', f'refs/remotes/origin/{branch}')


def bc_show_eligible(repo_dir, *args):
    result = subprocess.run(
        [BIN_DIR / 'git-bc-show-eligible', *args],
        cwd=repo_dir,
        capture_output=True,
        text=True,
    )
    print(cmd_info(result))
    return result
