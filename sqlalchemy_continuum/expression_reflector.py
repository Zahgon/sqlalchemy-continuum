import sqlalchemy as sa
from sqlalchemy.sql.expression import bindparam

from .utils import version_table


class VersionExpressionReflector(sa.sql.visitors.ReplacingCloningVisitor):
    def __init__(self, parent, relationship):
        self.parent = parent
        self.relationship = relationship

    def replace(self, column):
        pass

    def __call__(self, expr):
        return self.traverse(expr)
