# -*- python -*-

import os.path

from icommand import DirectOutputIrodsCommand, IrodsCommand

def iquest_replicas( path, user = None, recursive = False, resource = None, resource_group_replicas = True,
                     date = False ):
    "gather replica status dictionary"

    def replica_dict( output ):
        ret = {}

        for pr in output:

            if pr is None: continue

            path, replnum, dataid = pr

            if path not in ret: ret[path] = [replnum, dataid]
            else:
                ret[path][0] += replnum


        return ret

    def iquest_filter( e ):
        if "CAT_NO_ROWS_FOUND" in e: return None

        path, replnum, dataid = e.rsplit( ':', 2 )

        return path, int( replnum ), dataid

    def replica_dict_with_date( output ):
        ret = {}

        for pr in output:

            if pr is None: continue

            path, replnum, dataid, date = pr

            if path not in ret: ret[path] = [replnum, dataid, date]
            else:
                ret[path][0] += replnum
                ret[path][2] = max( ret[path][2], date )

        return ret

    def iquest_filter_with_date(e):
        if "CAT_NO_ROWS_FOUND" in e: return None

        path, replnum, dataid, date = e.rsplit( ':', 3 )

        return path, int( replnum ), dataid, int( date )

    resc_column = "RESC_GROUP_NAME"
    if not resource_group_replicas:
        resc_column = "RESC_NAME"

    fmt = "%s/%s:%s:%s"
    filter_ = iquest_filter
    build_dict = replica_dict
    select = "select COLL_NAME, DATA_NAME, count(DATA_REPL_NUM), DATA_ID"
    if date:
        fmt = fmt + ":%s"
        filter_ = iquest_filter_with_date
        build_dict = replica_dict_with_date
        select += ", max(DATA_MODIFY_TIME)"

    iquest = DirectOutputIrodsCommand( "iquest", ["--no-page", "no-distinct", fmt],
                                       output_filter = filter_, verbose = False )

    condition1_list = []
    condition2_list = []

    if user:
        user_condition = "DATA_OWNER_NAME = '%s'" % user
        condition1_list.append(user_condition)
        condition2_list.append(user_condition)

    if resource:
        rg_condition = resc_column + " = '%s'" % resource
        condition1_list.append(rg_condition)
        condition2_list.append(rg_condition)

    condition1_list.append("COLL_NAME = '%s'" % path)
    condition2_list.append("COLL_NAME like '%s/%%'" % path)

    condition1 = " and ".join(condition1_list)
    condition2 = " and ".join(condition2_list)

    select1 = select + " where " + condition1
    select2 = select + " where " + condition2

    ret = {}

    output = iquest( [select1] )

    ret.update( build_dict( output ) )

    if recursive:
        output = iquest( [select2] )

        ret.update( build_dict( output ) )

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

    #FIXME: won't work if DATA_NAME contains apostrophes, also some charactes can't be escaped correctly
    coll, name = os.path.split( path )
    _retcode, replicas = iquest( ["select %s, order_asc(DATA_REPL_NUM) where DATA_NAME = '%s' and COLL_NAME = '%s'" %
                                  (resc_column, name, coll)] )


    # FIXME: check return code

    return replicas

def dataid_replicas( data_id, resource_group_replicas = True ):
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

    _retcode, replicas = iquest(["select %s, order_asc(DATA_REPL_NUM) where DATA_ID = '%s'" % (resc_column, data_id)])


    # FIXME: check return code

    return replicas
