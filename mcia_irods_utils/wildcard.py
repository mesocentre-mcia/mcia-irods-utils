
import os.path

from icommand import IrodsCommand, isrel, guess_icwd


def iswild(path):
    "detects if path conatins a wildcard"
    return "*" in path or "?" in path

def _sql_escape(path):
    ret = path

    # escape SQL wildcards
    ret = ret.replace("_", "\_")
    ret = ret.replace("%", "\%")

    # replace shell wildcards by SQL ones
    ret = ret.replace("*", "%")
    ret = ret.replace("?", "_")

    return ret

def _iquestw(path, orig_path):
    "expands SQL wildcards in path by querying the catalog"

    path_slashes = path.count("/")

    def _filter(e):
        ret = []

        # empty result
        if "CAT_NO_ROWS_FOUND" in e:
            return []

        # remove query results which contain more "/" characters than the original query
        # because they aren't on the same collection depth we asked
        for p in e.strip().split("\n"):
            if p.count("/") == path_slashes:
                ret.append(p)
        return ret

    iquest = IrodsCommand("iquest", ["--no-page"], output_filter = _filter, verbose = False)

    coll, name = os.path.split(path)

    files = []
    collections = []

    # look for data objects (files)
    if not path.endswith("/"): 
        returncode, files = iquest(["%s/%s", "select COLL_NAME, DATA_NAME where COLL_NAME like '%s' AND DATA_NAME like '%s'" % (coll, name)])

    # look for collections (directories)
    if  path.endswith("/"):
        path = path[:-1]
        path_slashes -= 1
    returncode, collections = iquest(["%s", "select COLL_NAME where COLL_NAME like '%s' " % (path, )])

    return (files + collections) or [orig_path]

def ipathw(path, icwd = None):
    newpath = path

    if not iswild(newpath): return [os.path.normpath(newpath)]

    if isrel(newpath):
        if icwd is None: icwd = guess_icwd()
        newpath = os.path.join(icwd, newpath)

    newpath = _sql_escape(newpath)

    newpath = _iquestw(newpath, path)

    return newpath

__all__ = [iswild, ipathw]
