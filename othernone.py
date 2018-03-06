

#an alternative to None. Should act identically *except* OtherNone == None should be False


class OtherNone():
    def __eq__(self, other):
        return isinstance(other, OtherNone)
    
    def __copy__(self):
        return self
    
    def __deepcopy__(self, memo):
        return self

    #python 2
    def __nonzero__(self):
        return False

    #python 3
    def __bool__(self):
        return False


OTHER_NONE = OtherNone()
