from copy import copy
from functools import wraps
from inspect import getmro

import sqlalchemy as sa
from sqlalchemy.orm.descriptor_props import ConcreteInheritedProperty

from ._compat import get_declarative_base
from .dialects.postgresql import create_versioning_trigger_listeners
from .model_builder import ModelBuilder
from .relationship_builder import RelationshipBuilder
from .table_builder import TableBuilder


def prevent_reentry(handler):
    pass


class Builder:
    def build_triggers(self):
        pass

    def build_tables(self):
        pass

    def closest_matching_table(self, model):
        pass

    def build_models(self):
        pass

    def build_relationships(self, version_classes):
        pass

    def instrument_versioned_classes(self, mapper, cls):
        pass

    def build_transaction_class(self):
        pass

    @prevent_reentry
    def configure_versioned_classes(self):
        pass

    def enable_active_history(self, version_classes):
        pass

    def create_column_aliases(self, version_classes):
        pass
