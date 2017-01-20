<!--
Copyright 2017 Bright Computing Holding BV.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->

Git Helpers
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
