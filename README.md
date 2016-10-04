Bright git
==========

This repository contains additional git commands, that help us with our
development workflow.

Build
-----

To update man pages, use `ronn`:

```
ronn --roff man/*.ronn
mv man/*.1 man/man1/
```

Install
-------

To install them, checkout this repository somewhere and add the subdirectory
`bin` in your `$PATH` variable. You can also add the subdirectory `man` to your
`$MANPATH`, if you want to use `git help <command>`.
