class FlowDict(dict):
    """
    This is a custom dictionary class with tuples as keys. 
    If self[(u, v)] does not exist, then self[(u, v)] is 
    initialized with -self[(v, u)]
    """
    def __missing__(self, key):
        u, v = key
        try:
            self.__setitem__(key, -self.get((v, u)))
            return self[key]
        except KeyError:
            raise
