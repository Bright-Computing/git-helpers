git-bc-log(1) -- Show text-based graph logs
===========================================

## SYNOPSIS

`git bc-log` [<options>] [<revision range>] [[--] <path>...]

## DESCRIPTION

Show text-based graph logs.

The command adds options to the builtin git-log(1) command to prettify the
output as a graph. All options of `git log` are also applicable for this
command. Please refer to git-log(1) for additional options.

## OPTIONS

  * `-a`, `--all`:
    Show all the branches in the log.

  * `<revision range>`:
    Show only commits in the specified revision range. When no
    `<revision-range>` is specified, it defaults to HEAD (i.e. the whole
    history leading to the current commit). For a complete list of ways to
    spell `<revision range>`, see gitrevisions(7).

  * `[--] <path>...`:
    Show only commits that are enough to explain how the files that match the
    specified paths came to be.

    Paths may need to be prefixed with "--" to separate them from options or
    the revision range, when confusion arises.

## SEE ALSO

git-log(1)
