# Introduction

[mcia-irods-utils](https://github.com/mesocentre-mcia/mcia-irods-utils) is a set of commandline utilities for [iRODS](http://www.irods.org) iCommands.

# Prerequisites

To use mcia-irods-utils, you need:
* Python 3.6+
* Bash shell
* [iRODS](http://www.irods.org) iCommands installed and accessible in your `PATH`

# Install

Untar [mcia-irods-utils](https://github.com/mesocentre-mcia/mcia-irods-utils) to some temporary directory. From this directory, you can run:

```
python setup.py install [--prefix=</some/prefix>]
```

By default, install script will make the installation in `/usr/local`.

In case you provided a prefix, make sure `/some/prefix/bin` is in your `PATH` and `/some/prefix/lib/python2.x/site-packages` in your `PYTHONPATH` (replace `python2.x` by the version of your Python interpreter).

# Use

## Wildcards Commands

Some iRODS iCommands have been wrapped to allow server-side wildcards to be used in a similar way than shell expansion.

* `ilsw`
* `igetw`
* `irmw`
* `icpw`
* `imvw`

## Disk usage

* `idu`

## Replica number verification

* `irepl-check` - check and eventually repair file replicas number

## Metadata

* `imeta-coll` - manage metadata on collections, eventually recursively

## Data extraction

* `iextract` - extract data and metadata from iRODS, for backup or migration
