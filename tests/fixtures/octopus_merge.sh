#!/bin/bash
# Builds the octopus_merge fixture repo and exports it as a
# fast-import stream to octopus_merge.fi.
#
# Re-run this script whenever you need to update the fixture topology.
#
# master:   A(init) --- X(x.txt) --- M_oct
#                                   /    \
# feature1: (A): F1(f1.txt)--F2(f2.txt)  |
# feature2: (A): G1(g1.txt)--------------+
#
# stable:   A(init) --- S1(stable.txt)
#
# M_oct: parents[0]=X (mainline), parents[1]=F2, parents[2]=G1
# All commits add a unique file so cherry-picks never conflict.

set -e

WORK_DIR="${1:?Usage: $0 <work-dir>}"
FIXTURES_OUT="$WORK_DIR/fixtures"

REPO=$(mktemp -d "$WORK_DIR/repo.XXXXXX")

git -C $REPO init -q
git -C $REPO config user.email test@test
git -C $REPO config user.name Test

# A - initial commit
echo "init" > $REPO/init.txt
git -C $REPO add init.txt
git -C $REPO commit -m "Initial commit" -q

# stable branches off at A
git -C $REPO checkout -b stable -q
echo "stable" > $REPO/stable.txt
git -C $REPO add stable.txt
git -C $REPO commit -m "STABLE: stable fix" -q
git -C $REPO checkout master -q

# X - a commit on master only
echo "x" > $REPO/x.txt
git -C $REPO add x.txt
git -C $REPO commit -m "XXX-1: Master commit" -q

# feature1 from A
git -C $REPO checkout -b feature1 "$(git -C $REPO rev-parse master~1)" -q
echo "f1" > $REPO/f1.txt
git -C $REPO add f1.txt
git -C $REPO commit -m "XXX-2: Feature1 part 1" -q
echo "f2" > $REPO/f2.txt
git -C $REPO add f2.txt
git -C $REPO commit -m "XXX-2: Feature1 part 2" -q

# feature2 from A
git -C $REPO checkout -b feature2 "$(git -C $REPO rev-parse master~1)" -q
echo "g1" > $REPO/g1.txt
git -C $REPO add g1.txt
git -C $REPO commit -m "XXX-3: Feature2 commit" -q

# M_oct - octopus merge on master (parents[0]=X, parents[1]=F2, parents[2]=G1)
git -C $REPO checkout master -q
git -C $REPO merge --no-ff feature1 feature2 -m "XXX-2/3: Merge feature1 and feature2" -q

git -C $REPO fast-export --all > "$FIXTURES_OUT/octopus_merge.fi"
echo "Written octopus_merge.fi"
