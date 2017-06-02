class __Model(object):
    tableName = None
    tableSchema = None

    def __init__(self, *args):
        for i in range(0, len(self.tableSchema)):
            entry = tableSchema[i]
            setattr(self, entry[0], args[i])