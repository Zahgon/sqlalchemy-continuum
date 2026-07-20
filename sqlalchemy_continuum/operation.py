from copy import copy

import sqlalchemy as sa

from ._compat import identity


class Operation:
    INSERT = 0
    UPDATE = 1
    DELETE = 2

    def __init__(self, target, type):
        self.target = target
        self.type = type
        self.processed = False

    def __eq__(self, other):
        return self.target == other.target and self.type == other.type


class Operations:

    def __init__(self):
        self.objects = {}

    def format_key(self, target):
        pass

    def __contains__(self, target):
        return self.format_key(target) in self.objects

    def __setitem__(self, key, operation):
        self.objects[key] = operation

    def __getitem__(self, key):
        return self.objects[key]

    def __delitem__(self, key):
        del self.objects[key]

    def __bool__(self):
        return bool(self.objects)

    def __repr__(self):
        return repr(self.objects)

    @property
    def entities(self):
        pass

    def items(self):
        return self.objects.items()

    def add(self, operation):
        pass

    def add_insert(self, target):
        pass

    def add_update(self, target):
        pass

    def add_delete(self, target):
        pass
