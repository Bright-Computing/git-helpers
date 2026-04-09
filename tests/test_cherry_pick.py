from conftest import bc_cherry_pick, resolve_ref, git


def last_commit_message(repo_dir, branch='stable'):
    return git(repo_dir, 'log', '-n', '1', '--format=%B', branch).stdout.strip()


def test_regular_commit_cherry_pick(make_repo):
    """A plain commit is cherry-picked as-is with no children annotation."""
    repo = make_repo('bc_cherry_pick_scenarios')
    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master', 'master')  # P is master tip
    git(repo, 'checkout', 'master')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    msg = last_commit_message(repo)
    assert 'XXX-3: Patch' in msg, f"commit message:\n{msg}"
    assert '(with child' not in msg, f"unexpected children annotation in:\n{msg}"


def test_merge_commit_appends_children(make_repo):
    """Cherry-picking a merge commit appends (with child HASH) lines for each branch child."""
    repo = make_repo('bc_cherry_pick_scenarios')
    # M = master~1; parents[0]=X, parents[1]=F2; F1 is F2's first parent
    f2_hash = resolve_ref(repo, 'master~1^2')    # F2: M's branch parent (parents[1])
    f1_hash = resolve_ref(repo, 'master~1^2^1')  # F1: F2's first parent

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master~1', 'master~1')
    git(repo, 'checkout', 'master')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    msg = last_commit_message(repo)
    assert f'(with child {f2_hash})' in msg, \
        f"expected '(with child {f2_hash[:8]}...)' in commit message:\n{msg}"
    assert f'(with child {f1_hash})' in msg, \
        f"expected '(with child {f1_hash[:8]}...)' in commit message:\n{msg}"


def test_select_overrides_mainline(make_repo):
    """--select makes the specified parent the mainline, changing which side is applied."""
    repo = make_repo('bc_cherry_pick_scenarios')
    # M = master~1, parents[0]=X (mainline by default), parents[1]=F2 (feature)
    # With --select=F2, mainline becomes F2 and we apply the X side (master.txt)
    f2_hash = resolve_ref(repo, 'master~1^2')
    x_hash = resolve_ref(repo, 'master~1^1')

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master~1', 'master~1', f'--select={f2_hash}')
    git(repo, 'checkout', 'master')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    msg = last_commit_message(repo)
    assert f'(with child {x_hash})' in msg, \
        f"expected '(with child {x_hash[:8]}...)' in commit message:\n{msg}"
    stable_files = git(repo, 'ls-tree', '-r', '--name-only', 'stable').stdout.split()
    assert 'master.txt' in stable_files, f"master.txt missing from stable tree: {stable_files}"
    assert 'feat1.txt' not in stable_files, f"feat1.txt should not be in stable tree: {stable_files}"
    assert 'feat2.txt' not in stable_files, f"feat2.txt should not be in stable tree: {stable_files}"


def test_no_commit_writes_to_merge_msg(make_repo):
    """--no-commit stages changes and writes the children list to MERGE_MSG without committing."""
    repo = make_repo('bc_cherry_pick_scenarios')
    head_before = resolve_ref(repo, 'stable')

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master~1', 'master~1', '--no-commit')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    head_after = resolve_ref(repo, 'stable')
    assert head_after == head_before, \
        f"stable moved unexpectedly: {head_before[:8]} -> {head_after[:8]}"
    merge_msg = (repo / '.git' / 'MERGE_MSG').read_text()
    assert '(with child' in merge_msg, f"MERGE_MSG missing children annotation:\n{merge_msg}"

    git(repo, 'reset', '--hard')
    git(repo, 'checkout', 'master')


def test_dry_run_prints_commands(make_repo):
    """--dry-run prints the cherry-pick and amend commands without executing them."""
    repo = make_repo('bc_cherry_pick_scenarios')
    head_before = resolve_ref(repo, 'stable')

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master~1', 'master~1', '--dry-run')
    git(repo, 'checkout', 'master')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    assert 'git cherry-pick' in result.stdout
    assert 'git commit --amend' in result.stdout
    head_after = resolve_ref(repo, 'stable')
    assert head_after == head_before, \
        f"stable moved despite --dry-run: {head_before[:8]} -> {head_after[:8]}"


def test_select_unknown_hash_fails(make_repo):
    """--select with a hash that doesn't match any parent exits with an error."""
    repo = make_repo('bc_cherry_pick_scenarios')

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master~1', 'master~1', '--select=deadbeef')
    git(repo, 'checkout', 'master')

    assert result.returncode != 0, "expected non-zero exit for unknown --select"
    assert 'Error' in result.stdout or 'Error' in result.stderr


def test_octopus_merge_cherry_pick(make_repo):
    """Cherry-picking an octopus merge succeeds; children from the first branch parent are annotated."""
    repo = make_repo('octopus_merge')
    # M_oct = master tip; parents[0]=X (mainline), parents[1]=F2, parents[2]=G1
    f2_hash = resolve_ref(repo, 'master^2')   # F2: first branch parent
    f1_hash = resolve_ref(repo, 'master^2^1') # F1: F2's parent

    git(repo, 'checkout', 'stable')
    result = bc_cherry_pick(repo, 'master', 'master')
    git(repo, 'checkout', 'master')

    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    msg = last_commit_message(repo)
    # Children from parents[1] (feature1) must be annotated
    assert f'(with child {f2_hash})' in msg, \
        f"expected '(with child {f2_hash[:8]}...)' in commit message:\n{msg}"
    assert f'(with child {f1_hash})' in msg, \
        f"expected '(with child {f1_hash[:8]}...)' in commit message:\n{msg}"
