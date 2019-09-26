# -*- coding: utf-8 -*-

from itertools import zip_longest

class Coordinate(tuple):

    def __add__(self, other):
        return Coordinate([a+b for a, b in zip_longest(self, other, fillvalue=0)])

    __radd__ = __add__

    def __sub__(self, other):
        return Coordinate([a-b for a, b in zip_longest(self, other, fillvalue=0)])

    __rsub__ = __sub__
