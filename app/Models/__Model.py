class __Model(object):
    tableName = None
    tableSchema = None

    def __init__(self, *args):
        for i in range(0, len(self.tableSchema)):
            entry = self.tableSchema[i]
            setattr(self, entry[0], args[i])

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def serialize(self):
        dict = {}
        for entryName, entryType in self.tableSchema:
            dict[entryName] = getattr(self, entryName)
        return dict