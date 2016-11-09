Bright git
==========

This repository contains additional git commands, that help us with our
development workflow.

Install
-------

To install them, checkout this repository somewhere and add the subdirectory
`bin` in your `$PATH` variable. You can also add the subdirectory `man` to your
`$MANPATH`, if you want to use `git help <command>`.

Build
-----

There is no need to build this package if you are using it stright away. If you
update the man pages however you need to rebuild them.

To update the man pages, you need the `ronn` package:

```
$ cd man
$ ./convert-to-man
```
