
from sortedcontainers import SortedSet

try:
    from math import inf
except ImportError: #python 2
    inf = float('inf')

class SSet(SortedSet):

    def __getitem__(self, val):
        returnvals = []
        try:
            start = val.start if val.start is not None else -inf
            stop = val.stop if val.stop is not None else inf
            for item in self:
                if item >= start:
                    if item > stop:
                        break
                    returnvals.append(item)
        except AttributeError:
            raise TypeError("SSet does not support indexing")
        return returnvals
