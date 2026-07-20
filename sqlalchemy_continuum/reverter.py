import sqlalchemy as sa

from .operation import Operation
from .utils import parent_class, versioned_column_properties


def first_level(paths):
    pass


def subpaths(paths, name):
    pass


class ReverterException(Exception):
    pass


class Reverter:
    def __init__(self, obj, visited_objects=None, relations=None):
        if relations is None:
            relations = []
        self.visited_objects = visited_objects or []
        self.obj = obj
        self.version_parent = self.obj.version_parent
        self.parent_class = parent_class(self.obj.__class__)
        self.parent_mapper = sa.inspect(self.parent_class)
        self.session = sa.orm.object_session(self.obj)

        self.relations = list(relations)
        for path in relations:
            subpath = path.split('.')[0]
            if subpath not in self.parent_mapper.relationships:
                raise ReverterException(
                    f"Could not initialize Reverter. Class '{parent_class(self.obj.__class__).__name__}' does not have "
                    f"relationship '{subpath}'."
                )

    def revert_properties(self):
        pass

    def revert_association(self, prop):
        pass

    def revert_relationship(self, prop):
        pass

    def revert_child(self, child, prop):
        pass

    def revert_relationships(self):
        pass

    def __call__(self):
        if self.obj in self.visited_objects:
            return (
                None
                if self.obj.operation_type == Operation.DELETE
                else self.version_parent
            )

        if self.obj.operation_type == Operation.DELETE:
            self.session.delete(self.version_parent)
            return

        self.visited_objects.append(self.obj)

        if self.version_parent is None:
            self.version_parent = parent_class(self.obj.__class__)()

        self.revert_properties()
        self.revert_relationships()
        self.session.add(self.version_parent)

        return self.version_parent
