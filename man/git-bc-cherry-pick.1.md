git-bc-cherry-pick(1) -- Apply the changes introduced by some existing commits
==============================================================================

## SYNOPSIS

`git bc-cherry-pick` [<options>] <commit>

## DESCRIPTION

Given an existing commit, apply the changes it introduced, recording a new
commit in the current branch. This requires your working tree to be clean (no
modifications from the HEAD commit).

The command applies a standard git-cherry-pick(1) with the given commit. It
works the same way, except that in case the given commit is a merge, it asks
interactively what is the branch to consider in the cherry pick. By default it
does not commit, but only stages the changes, so it allows you to review them.

In case the command can't figure out what branch to apply automatically, this
is the prompt it presents to you:

```
This is a merge commit
Select one option to review the state or the branch to apply:
    graph)      review the commit graph
    commits)    review the list of commits
    diff)       review the diff
    1|2)        select the branch to be applied (1 or 2)
    help)       show this message
    quit)       abort

Selection (<NUM>/g/c/d/h/q)
```

Options `graph`, `commits` and `diff` gives an overview of the branches to be
considered, `1` selects the first branch and `2` the second one. Option `q` is
to abort the cherry-pick.

If conflicts arise, you will need to resolve them by editing the files and
adding them with git-add(1) and continue the cherry-pick with git-cherry-pick(1)
with the `--continue` option. You can use git-status(1) to be guided through
this process.

## OPTIONS

  * `-n`, `--no-commit`:
    Stage changes if the cherry-pick succedes, but do not commit.

  * `--dry-run`:
    Do not actually execute the git commands, but only print them.

  * `<commit>`:
    The SHA-1 identifier of the commit to use for the cherry-pick. See
    gitrevisions(7). This parameter is mandatory.

## EXAMPLES

Suppose to have this history:

```
     .---B---C---D---
    /   /       /
---A   /       /
    \ /       /
     E-------F

---G---H
```

The commits are:

  * A is the common ancestor between two branches.
  * Commits B, C, D are part of the master branch.
  * Commits E, F are part of a feature branch.
  * Commits B and D are merge commits between the two branches. They are however
    different, because D is a normal merge bringing together commits B, C and F,
    while B has been created with `--ff-only option`, so even if master hasn't
    changed in the meantime, instead of fast forwarding master to E, a new merge
    commit has been created.
  * Commits G, H are commits of a release branch (H is its last commit).

You want to cherry pick onto the release branch one of the commits in the
other two branches. The other two branches are not affected. The end result for
the release branch will be this in all the examples:

```
---G---H---I
```

If you want to cherry-pick the commit F:

    $ git bc-cherry-pick F

    The command will simply cherry pick the commit and create I, without user
    interaction.

If you want to cherry-pick the commit B:

    $ git bc-cherry-pick B

    The command will simply cherry pick the commit and create I, without user
    interaction. This is possible because she branch to select is unambiguosly
    the one containing E, since the other one is empty (i.e. there are no
    commits between A (common ancestor) and B.

If you want to cherry-pick the commit D, with the commits introduced in the
feature branch:

    $ git bc-cherry-pick D

    The command will stop asking user interaction, because it doesn't know which
    branch to apply. The choice is between commits E, F, or B, C. In this case
    we want E, F. To do so, we get the branch number by selecting `c` in the
    selection prompt. The outupt will be this:

    Branch 1:
    C message 2
    B message 1

    Branch 2:
    E message 3
    F message 4

    In this case we need to input `2` to select the second branch.

## SEE ALSO

git-cherry-pick(1)
