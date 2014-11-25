#! /bin/bash

# try to mimic icommands detection of irodsCwd while we are in a subshell
function _guess_iwd() {
    local iwd=INVALID

    local ppid=$(ps -p $$ -o ppid= | sed -e 's/^ *//g')

    # check for irodsEnv file for our pid and its parent.
    for pid in $$ $ppid ; do
        if [ -f $HOME/.irods/.irodsEnv.$pid ] ; then
            # read wd from irodsEnv
            source $HOME/.irods/.irodsEnv.$pid
            iwd=$irodsCwd
            break
        fi
    done

    if [ $iwd = INVALID ] ; then
        # fallback to ipwd (many chances it's irodsHome)
        iwd=$(ipwd)
    fi

    echo $iwd
}

# returns true if arguments contains a wildcard
function _iswild() {
    echo "$@" | grep -e "[*?]" > /dev/null
}

# replaces shell wildcards in arguments with SQL compatible ones while escaping SQL wildcards from initial expression
function _sql_escape() {
    echo "$@" | sed -e 's/_/\\_/g' | sed -e 's/%/\\%/g' | sed -e 's/\*/%/g' | sed -e 's/?/_/g'
}

# returns true if argument represents a relative path (i.e. doesn't begin with a "/")
function _isrel() {
    echo "$@" | grep -v -e "^/.*$" > /dev/null
}

# returns true if both argument strings contains the same number of slashes
function _slashvalidate() {
    local one=$(echo "$1" | sed -e 's/[^/]//g')
    local other=$(echo "$2" | sed -e 's/[^/]//g')

    test x"$one" = x"$other"
    local ret=$?
    return $ret
}

# queries iRODS Catalog for wildcard path expansion
function _iquestw() {
    local ret=""

    local path="$1"
    local orig_path="$2"

    local coll=$(dirname "$path")
    local data=$(basename "$path")

    # expand data names
    local dsel="select COLL_NAME, DATA_NAME where COLL_NAME like '$coll' AND DATA_NAME like '$data'"
    local dret=$(eval iquest --no-page "%s/%s" \"$dsel\")

    if echo "$dret" | grep -v CAT_NO_ROWS_FOUND >/dev/null ; then
        # remove query results which contain more "/" characters than the original query
        # because they aren't on the same collection depth we asked
        for r in $dret ; do
            if _slashvalidate "$path" "$r" ; then
                ret="$ret $r"
            fi
        done
    fi

    # expand collection names
    local csel="select COLL_NAME where COLL_NAME like '$path'"
    local cret=$(eval iquest --no-page "%s" \"$csel\")

    if echo "$cret" | grep -v CAT_NO_ROWS_FOUND >/dev/null ; then
        # remove query results which contain more "/" characters than the original query
        # because they aren't on the same collection depth we asked
        for r in $cret ; do
            if _slashvalidate "$path" "$r" ; then
                ret="$ret $r"
            fi
        done
    fi

    if [ -z "$ret" ] ; then
        # no match at all
        ret="$orig_path"
    fi

    echo "$ret"
}

function _ipathw() {
    local arg="$1"
    local iwd="$2"
    local newarg="$arg"

    if _isrel "$newarg" ; then
        newarg="$iwd/$newarg"
    fi

    newarg=$(_sql_escape "$newarg")
    newarg=$(_iquestw "$newarg" "$arg")

    echo "$newarg"
}

function _icmdw() {
    local cmd="$1"
    shift

    local iwd=$(_guess_iwd)

    local wargs=""
    for arg in "$@" ; do
        if _iswild "$arg" ; then
            newarg=$(_ipathw "$arg" "$iwd")

            wargs="$wargs $newarg"
        else
            wargs="$wargs $arg"
        fi
    done

    eval $cmd $wargs
}

function _icmdw_igetw() {
    _icmdw iget "$@"
}

function _icmdw_ilsw() {
    _icmdw ils "$@"
}

function _icmdw_irmw() {
    _icmdw irm "$@"
}

cmd=$(basename "$0")

case "$cmd" in
    igetw|ilsw|irmw)
        _icmdw_"$cmd" "$@"
        ;;
    *)
        echo ERROR: unknown command: "$cmd"
        ;;
esac