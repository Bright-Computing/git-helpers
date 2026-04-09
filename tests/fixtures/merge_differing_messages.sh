#!/bin/bash
# Builds the merge_differing_messages fixture repo and exports it as a
# fast-import stream to merge_differing_messages.fi.
#
# Re-run this script whenever you need to update the fixture topology.
#
# master:   A --- M1 ----------- M2 --- P --- M3
#               /               /             /
# feature1: B-C+                |             |
# feature2:          D --- E ---+             |
# feature3:                          F - G - H+
#
# stable:   A --- S1 --- S2
#
# M1: feature1 messages match merge message (normal grouping case)
# M2: feature2 messages DIFFER from merge message (the original bug)
# P:  standalone commit (cherry-picked to stable in tests)
# M3: feature3, three commits deep

set -e

REPO=$(mktemp -d)
trap "rm -rf $REPO" EXIT

git -C $REPO init -q
git -C $REPO config user.email test@test
git -C $REPO config user.name Test

# A - initial commit (common ancestor of master and stable)
git -C $REPO commit --allow-empty -m "Initial commit" -q

# stable branches off here
git -C $REPO checkout -b stable -q
git -C $REPO commit --allow-empty -m "STABLE: Backport fix 1" -q
git -C $REPO commit --allow-empty -m "STABLE: Backport fix 2" -q

# feature1 - messages match merge
git -C $REPO checkout master -q
git -C $REPO checkout -b feature1 -q
git -C $REPO commit --allow-empty -m "XXX-10: Add widget A" -q
git -C $REPO commit --allow-empty -m "XXX-10: Add widget B" -q

# M1 - merge of feature1, message matches last child
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature1 -m "XXX-10: Add widget B" -q

# feature2 - messages DIFFER from merge (the original bug)
git -C $REPO checkout -b feature2 -q
git -C $REPO commit --allow-empty -m "XXX-20: Refactor part 1" -q
git -C $REPO commit --allow-empty -m "XXX-20: Refactor part 2" -q

# M2 - merge of feature2, message intentionally differs from children
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature2 -m "XXX-20: Refactor completed" -q

# P - standalone commit (conftest will cherry-pick this to stable in tests)
git -C $REPO commit --allow-empty -m "XXX-30: Fix nasty bug" -q

# feature3 - three commits deep
git -C $REPO checkout -b feature3 -q
git -C $REPO commit --allow-empty -m "XXX-40: New API v1" -q
git -C $REPO commit --allow-empty -m "XXX-40: New API v2" -q
git -C $REPO commit --allow-empty -m "XXX-40: New API v3" -q

# M3 - merge of feature3
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature3 -m "XXX-40: New API v3" -q

git -C $REPO fast-export --all > "$(dirname "$0")/merge_differing_messages.fi"
echo "Written merge_differing_messages.fi"
