#!/bin/bash
# Builds the bc_cherry_pick_scenarios fixture repo and exports it as a
# fast-import stream to bc_cherry_pick_scenarios.fi.
#
# Re-run this script whenever you need to update the fixture topology.
#
# master:   A(init) --- X(master.txt) --- M --- P(patch.txt)
#                                        /
# feature1: (A): F1(feat1.txt) --- F2(feat2.txt)
#
# stable:   A(init) --- S1(stable.txt)
#
# All commits add a unique file so cherry-picks never conflict.
# M: parents[0]=X (mainline), parents[1]=F2 (feature tip)
# P: standalone commit after the merge (for regular cherry-pick tests)

set -e

REPO=$(mktemp -d)
trap "rm -rf $REPO" EXIT

git -C $REPO init -q
git -C $REPO config user.email test@test
git -C $REPO config user.name Test

# A - initial commit
echo "init" > $REPO/init.txt
git -C $REPO add init.txt
git -C $REPO commit -m "Initial commit" -q

# stable branches off at A
git -C $REPO checkout -b stable -q
echo "stable fix" > $REPO/stable.txt
git -C $REPO add stable.txt
git -C $REPO commit -m "STABLE: stable fix" -q
git -C $REPO checkout master -q

# X - a commit on master only
echo "master change" > $REPO/master.txt
git -C $REPO add master.txt
git -C $REPO commit -m "XXX-1: Master commit" -q

# feature1 from A
git -C $REPO checkout -b feature1 "$(git -C $REPO rev-parse master~1)" -q
echo "feature 1" > $REPO/feat1.txt
git -C $REPO add feat1.txt
git -C $REPO commit -m "XXX-2: Feature part 1" -q
echo "feature 2" > $REPO/feat2.txt
git -C $REPO add feat2.txt
git -C $REPO commit -m "XXX-2: Feature part 2" -q

# M - master merges feature1 (parents[0]=X, parents[1]=F2)
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature1 -m "XXX-2: Feature done" -q

# P - standalone commit after the merge
echo "patch" > $REPO/patch.txt
git -C $REPO add patch.txt
git -C $REPO commit -m "XXX-3: Patch" -q

git -C $REPO fast-export --all > "$(dirname "$0")/bc_cherry_pick_scenarios.fi"
echo "Written bc_cherry_pick_scenarios.fi"
