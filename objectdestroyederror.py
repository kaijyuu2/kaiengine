

#custom error type for using objects that have been destroyed


class ObjectDestroyedError(Exception):
    '''Raise when an attempt to modify or access a destroyed object occurs'''
