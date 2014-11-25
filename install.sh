#! /bin/bash

prefix="/usr/local"

function check_bindir() {
    if [ -d $bindir ] ; then
        return 0
    fi

    mkdir -p $bindir

    if [ $? -ne 0 ] ; then
        echo Error: cannot create directory $bindir
        exit -1
    fi

    return 0
}

function install_bin_scripts() {
    for s in $bin_scripts ; do
        cp -d $s $bindir
    done
}


case "$1" in
    --prefix)
        prefix=$2
        ;;
    --prefix=*)
    prefix=$(echo "$1" | cut -d= -f2-)
    ;;
esac

bindir=$prefix/bin

icmdw_scripts=$(dirname $0)/icmdw/i*

bin_scripts=$icmdw_scripts


check_bindir

install_bin_scripts