from .icommand import IquestCommand

def iquest_iscollection(path):

    def iquest_filter(e):
        return "CAT_NO_ROWS_FOUND" not in e

    iquest = IquestCommand(
        ["--no-page", "no-distinct", "%s"],
        output_filter=iquest_filter,
        verbose=False
    )

    retcode, iscoll = iquest(['select COLL_NAME where COLL_NAME = \'%s\';' % path])

    if retcode != 0:
        raise Exception("iquest returned nonzero status (%d).", retcode)


    return iscoll
