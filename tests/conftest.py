import subprocess
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / 'fixtures'
BIN_DIR = Path(__file__).parent.parent / 'bin'


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


@pytest.fixture
def make_repo(tmp_path):
    """Return a factory that creates a git repo from a .fi fixture file."""
    def _make(fixture_name):
        repo_dir = tmp_path / fixture_name
        repo_dir.mkdir()
        git(repo_dir, 'init')
        git(repo_dir, 'config', 'user.email', 'test@test')
        git(repo_dir, 'config', 'user.name', 'Test')
        fi_path = FIXTURES_DIR / f'{fixture_name}.fi'
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
