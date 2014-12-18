
from icommand import IrodsCommand

def iquest_collection_metadata( collection, metaname = None, metavalue = None, metaunit = None, recursive = False ):
    def iquest_filter2( e ):
        if "CAT_NO_ROWS_FOUND" in e: return []

        return [x.split( "'", 3 ) for x in e.strip().split( "\n" )]

    iquest = IrodsCommand( "iquest", ["%s'%s'%s'%s"], output_filter = iquest_filter2, verbose = False )

    select = "select COLL_NAME, META_COLL_ATTR_NAME, META_COLL_ATTR_VALUE, META_COLL_ATTR_UNITS"

    collection_condition = "COLL_NAME = '%s'" % collection

    conditions = []
    if metaname is not None:
        conditions.append( "META_COLL_ATTR_NAME = '%s'" % metaname )

    if metavalue is not None:
        conditions.append( "META_COLL_ATTR_VALUE = '%s'" % metavalue )

    if metaunit is not None:
        conditions.append( "META_COLL_ATTR_UNITS = '%s'" % metaunit )

    select_cmd = select + " where " + " and ".join( [collection_condition] + conditions )

    retcode, output = iquest( [select_cmd] )

    if retcode != 0:
        print "ERROR:", output
        return

    if recursive:
        recursive_condition = "COLL_NAME like '%s/%%'" % collection
        select_cmd = select + " where " + " and ".join( [recursive_condition] + conditions )
        retcode, output2 = iquest( [select_cmd] )

        if retcode != 0:
            print "ERROR:", output
            return
        if output2:
            output += output2

    return output

if __name__ == "__main__":
    print iquest_collection_metadata( "/MCIA/home/pigay", recursive = True )
    print iquest_collection_metadata( "/MCIA/home/pigay", "replFactor", recursive = True )
    print iquest_collection_metadata( "/MCIA/home/pigay", "replFactor", "1", recursive = True )
    print iquest_collection_metadata( "/MCIA/home/pigay", metaunit = "iRODSUserTagging:Tag", recursive = True )
