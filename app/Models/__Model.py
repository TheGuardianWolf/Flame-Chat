class __Model(object):
    tableName = None
    tableSchema = None

    def __init__(self, *args):
        for i in range(0, len(self.tableSchema)):
            entry = self.tableSchema[i]
            setattr(self, entry[0], args[i])

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def serialize(self, intoList=False):
        if intoList:
            obj = []
            for i, entry in enumerate(self.tableSchema):
                obj.append(getattr(self, entry[0]))
        else:
            obj = {}
            for entryName, entryType in self.tableSchema:
                obj[entryName] = getattr(self, entryName)
        return obj

    @classmethod
    def deserialize(c, obj):
        def parseValue(value, dbValueType):
            if value == 'NULL' or value == 'null':
                pyValue = None
            elif dbValueType.find('integer') > -1:
                pyValue = int(value)
            else:
                pyValue = str(value)
            return pyValue

        args = []
        if isinstance(obj, (list, tuple)):
            for i, entry in enumerate(c.tableSchema):
                try:
                    value = obj[i]
                except IndexError:
                    value = 'NULL'
                pyValue = parseValue(value, entry[1])
                args.append(pyValue)
        elif isinstance(obj, dict):
            for i, entry in enumerate(c.tableSchema):
                try:
                    value = obj[entry[0]]
                except KeyError:
                    value = 'NULL'
                pyValue = parseValue(value, entry[1])
                args.append(pyValue)
        else:
            raise TypeError('Type must be a list, tuple or dict.')

        return c(*args)
