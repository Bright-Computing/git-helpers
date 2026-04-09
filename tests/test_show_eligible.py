from conftest import bc_show_eligible, git_cherry_pick, git_cherry_pick_merge, resolve_ref, set_origin_head


def test_merge_groups_by_parentage(make_repo):
    """Merge commits are grouped with their children regardless of message similarity."""
    repo = make_repo('merge_differing_messages')
    result = bc_show_eligible(repo, 'master', 'stable')
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    lines = result.stdout.splitlines()

    # M1 and its two children must appear as a group (messages match)
    m1_idx = next((i for i, l in enumerate(lines) if 'XXX-10: Add widget B' in l and not l.startswith(' ')), None)
    assert m1_idx is not None, "M1 (XXX-10: Add widget B) not found as top-level entry"
    children = lines[m1_idx + 1:m1_idx + 3]
    assert all(l.startswith(' ') for l in children), \
        f"M1 children must be indented, got: {children}"
    assert any('XXX-10: Add widget A' in l for l in children), \
        f"XXX-10: Add widget A not grouped under M1, got: {children}"
    assert any('XXX-10: Add widget B' in l for l in children), \
        f"expected child also containing 'Add widget B', got: {children}"

    # M2 and its children must be grouped even though messages differ
    m2_idx = next((i for i, l in enumerate(lines) if 'XXX-20: Refactor completed' in l), None)
    assert m2_idx is not None, "M2 (XXX-20: Refactor completed) not found in output"
    children = lines[m2_idx + 1:m2_idx + 3]
    assert all(l.startswith(' ') for l in children), \
        f"M2 children must be indented, got: {children}"
    assert any('XXX-20: Refactor part 1' in l for l in children), \
        f"XXX-20: Refactor part 1 not grouped under M2, got: {children}"
    assert any('XXX-20: Refactor part 2' in l for l in children), \
        f"XXX-20: Refactor part 2 not grouped under M2, got: {children}"

    # M3 and its three children must be grouped
    m3_idx = next((i for i, l in enumerate(lines) if 'XXX-40: New API v3' in l and not l.startswith(' ')), None)
    assert m3_idx is not None, "M3 (XXX-40: New API v3) not found as top-level entry"
    children = lines[m3_idx + 1:m3_idx + 4]
    assert all(l.startswith(' ') for l in children), \
        f"M3 children must be indented, got: {children}"
    assert len(children) == 3 and all('XXX-40' in l for l in children), \
        f"expected 3 indented children all containing XXX-40, got: {children}"


def test_cherry_picked_commit_excluded(make_repo):
    """A commit already cherry-picked to the target branch does not appear as eligible."""
    repo = make_repo('merge_differing_messages')
    git_cherry_pick(repo, 'master~1', 'stable')  # cherry-pick P onto stable
    result = bc_show_eligible(repo, 'master', 'stable')
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    assert 'XXX-30: Fix nasty bug' not in result.stdout, \
        "cherry-picked commit still appears as eligible"


def test_mainline_not_first_parent(make_repo):
    """When mainline is parents[1] of a sync merge, --select=HASH prefix is shown."""
    repo = make_repo('mainline_not_first_parent')
    # M_outer (master tip) was already handled; cherry-pick it to stable to exclude it
    git_cherry_pick_merge(repo, 'master', 1, 'stable')

    x_hash = resolve_ref(repo, 'master^1')  # M_outer's first parent is X (the mainline commit)
    result = bc_show_eligible(repo, 'master', 'stable')
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"

    lines = result.stdout.splitlines()
    sync_line = next((l for l in lines if 'Sync with master' in l), None)
    assert sync_line is not None, "'Sync with master' not found in output"
    assert sync_line.startswith(f'--select={x_hash[:12]}'), \
        f"expected line to start with '--select={x_hash[:12]}', got: {sync_line!r}"
    sync_idx = lines.index(sync_line)
    child_lines = lines[sync_idx + 1:sync_idx + 3]
    assert any('Feature part 1' in l for l in child_lines), \
        f"'Feature part 1' not grouped under sync commit, next lines: {child_lines}"


def test_standalone_commit_visible(make_repo):
    """A standalone commit not yet picked appears as a top-level entry."""
    repo = make_repo('merge_differing_messages')
    result = bc_show_eligible(repo, 'master', 'stable')
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    top_level = [l for l in result.stdout.splitlines() if not l.startswith(' ')]
    assert any('XXX-30: Fix nasty bug' in l for l in top_level), \
        "'XXX-30: Fix nasty bug' not found as a top-level entry"


def test_autodetect_uses_origin_head(make_repo):
    """When no BRANCH is given and origin/HEAD is set, it is auto-detected and used."""
    repo = make_repo('merge_differing_messages')
    set_origin_head(repo, 'master')
    result = bc_show_eligible(repo)
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"
    assert 'Auto-detected main branch: origin/master' in result.stdout


def test_autodetect_fails_without_origin_head(make_repo):
    """When no BRANCH is given and origin/HEAD is absent, exit 1 with an actionable error."""
    repo = make_repo('merge_differing_messages')
    result = bc_show_eligible(repo)
    assert result.returncode == 1
    assert 'No branch provided and could not auto-detect one' in result.stdout
    assert 'git remote set-head origin --auto' in result.stdout


def test_octopus_merge_children_grouped(make_repo):
    """All branch children of an octopus merge are grouped under it as indented entries."""
    repo = make_repo('octopus_merge')
    result = bc_show_eligible(repo, 'master', 'stable')
    assert result.returncode == 0, f"expected exit 0, got {result.returncode}"

    lines = result.stdout.splitlines()
    m_idx = next((i for i, l in enumerate(lines) if 'Merge feature1 and feature2' in l), None)
    assert m_idx is not None, "octopus merge commit not found in output"

    children = [l for l in lines[m_idx + 1:] if l.startswith(' ')]
    assert children, "no indented children found under octopus merge"
    assert any('Feature1 part 1' in l for l in children), \
        f"Feature1 part 1 not grouped under octopus merge: {children}"
    assert any('Feature1 part 2' in l for l in children), \
        f"Feature1 part 2 not grouped under octopus merge: {children}"
    assert any('Feature2 commit' in l for l in children), \
        f"Feature2 commit not grouped under octopus merge: {children}"
