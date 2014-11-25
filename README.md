# Introduction

mcia-irods-utils is a set of commandline utilities for iRODS iCommands.

# Prerquisites

To use mcia-irods-utils, you need:
* Bash shell
* iRODS iCommands installed and accessible in your `PATH`

# Install

Untar mcia-irods-utils to some temporary directory. From this directory, you can run:

```
./install.sh [--prefix=</some/prefix>]
```

By default, install script will make the installation in `/usr/local`.

In case you provided a prefix, make sure `/some/prefix/bin` is in your `PATH`.

# Use

## Wildcards Commands

Some iRODS iCommands have been wrapped to allow server-side wildcards to be used in a similar way than shell expansion.

* `ilsw`
* `igetw`
* `irmw`
