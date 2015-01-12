# -*- python -*-

import os.path

from icommand import IrodsCommand

def iquest_replicas( path, user = None, recursive = False, resource = None, resource_group_replicas = True ):
    "gather replica status dictionary"

    resc_column = "RESC_GROUP_NAME"
    if not resource_group_replicas:
        resc_column = "RESC_NAME"

    def iquest_filter(e):
        if "CAT_NO_ROWS_FOUND" in e: return {}
        ret = {}

        for l in e.split():
            path, replnum = l.split(':')
            if path not in ret: ret[path] = 0
            ret[path] += int(replnum)

        return ret

    iquest = IrodsCommand("iquest", ["--no-page", "no-distinct", "%s/%s:%s"],
                          output_filter = iquest_filter, verbose = False )

    condition1_list = ["COLL_NAME = '%s'" % path]
    condition2_list = ["COLL_NAME like '%s/%%'" % path]

    if user:
        user_condition = "DATA_OWNER_NAME = '%s'" % user
        condition1_list.append(user_condition)
        condition2_list.append(user_condition)

    if resource:
        rg_condition = resc_column + " = '%s'" % resource
        condition1_list.append(rg_condition)
        condition2_list.append(rg_condition)

    condition1 = " and ".join(condition1_list)
    condition2 = " and ".join(condition2_list)

    select = "select COLL_NAME, DATA_NAME, count(DATA_REPL_NUM)"

    select1 = select + " where " + condition1
    select2 = select + " where " + condition2

    ret = {}

    retcode, ret1 = iquest([select1])

    if retcode == 0:
        ret.update(ret1)

        if recursive:
            retcode, ret2 = iquest([select2])

            if retcode == 0:
                ret.update(ret2)

    return ret

def file_replicas( path, resource_group_replicas = True ):
    "return ordered list of replicas represented by RG and replica number"

    resc_column = "RESC_GROUP_NAME"
    if not resource_group_replicas:
        resc_column = "RESC_NAME"

    def iquest_filter( e ):
        if "CAT_NO_ROWS_FOUND" in e: return []
        values = e.strip().split('\n')
        return [e.split(":") for e in values]

    iquest = IrodsCommand("iquest", ["--no-page", "no-distinct", "%s:%s"],
                          output_filter = iquest_filter, verbose = False)

    retcode, replicas = iquest( ["select %s, order_asc(DATA_REPL_NUM) where COLL_NAME = '%s' and DATA_NAME = '%s'" % ( ( resc_column, ) + os.path.split( path ) )] )

    # FIXME: check return code

    return replicas
