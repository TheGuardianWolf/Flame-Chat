class MemoryService(object):
    """
    Holds shared memory across several users.
    """

    def __init__(self):
        self.data = {}


