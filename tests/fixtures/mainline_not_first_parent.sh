#!/bin/bash
# Builds the mainline_not_first_parent fixture repo and exports it as a
# fast-import stream to mainline_not_first_parent.fi.
#
# Re-run this script whenever you need to update the fixture topology.
#
# master:   A --- X ----------- M_outer
#                  \           /
# feature: (A): F1--M_inner---F2
#
# stable:   A
#
# M_inner: parents[0]=F1, parents[1]=X (mainline)
# Feature did `git merge master` at X, so X ends up at parents[1] of M_inner.
# After M_outer is cherry-picked to stable, M_inner becomes a top-level
# eligible commit and show-eligible must print --select=X_hash before it.

set -e

WORK_DIR="${1:?Usage: $0 <work-dir>}"
FIXTURES_OUT="$WORK_DIR/fixtures"

REPO=$(mktemp -d "$WORK_DIR/repo.XXXXXX")

git -C $REPO init -q
git -C $REPO config user.email test@test
git -C $REPO config user.name Test

# A - initial commit (common ancestor of master and stable)
git -C $REPO commit --allow-empty -m "Initial commit" -q

# stable branches off here (empty - tests will cherry-pick M_outer onto it)
git -C $REPO checkout -b stable -q
git -C $REPO checkout master -q

# X - a commit on master only (will become parents[1] of M_inner)
git -C $REPO commit --allow-empty -m "XXX-1: Master commit" -q

# feature from A (one commit before X)
git -C $REPO checkout -b feature "$(git -C $REPO rev-parse master~1)" -q

# F1
git -C $REPO commit --allow-empty -m "XXX-2: Feature part 1" -q

# M_inner: feature syncs with master — parents[0]=F1 (feature), parents[1]=X (mainline)
git -C $REPO merge --no-ff master -m "XXX-2: Sync with master" -q

# F2
git -C $REPO commit --allow-empty -m "XXX-2: Feature part 2" -q

# M_outer: master merges feature — parents[0]=X (mainline), parents[1]=F2
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature -m "XXX-2: Feature done" -q

git -C $REPO fast-export --all > "$FIXTURES_OUT/mainline_not_first_parent.fi"
echo "Written mainline_not_first_parent.fi"
