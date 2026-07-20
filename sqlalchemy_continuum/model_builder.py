from copy import copy

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property

from ._compat import get_declarative_base
from .utils import adapt_columns, option
from .version import VersionClassBase


def find_closest_versioned_parent(manager, model):
    pass


def versioned_parents(manager, model):
    pass


def get_base_class(manager, model):
    pass


def version_base(manager, parent_cls, base_class_factory=None):
    pass


def copy_mapper_args(model):
    pass


class ModelBuilder:

    def __init__(self, versioning_manager, model):
        """
        :param versioning_manager:
            VersioningManager object
        :param model:
            SQLAlchemy declarative model object that acts as a parent for the
            built version model
        """
        self.manager = versioning_manager
        self.model = model

    def build_parent_relationship(self):
        pass

    def build_transaction_relationship(self, tx_class):
        pass

    def base_classes(self):
        pass

    def inheritance_args(self, cls, version_table, table):
        pass

    def get_inherited_denormalized_columns(self, table):
        pass

    def build_model(self, table):
        pass

    def __call__(self, table, tx_class):
        """
        Build history model and relationships to parent model, transaction
        log model.
        """
        self.model.__versioned__ = copy(self.model.__versioned__)
        self.model.__versioning_manager__ = self.manager
        self.version_class = self.build_model(table)
        self.build_parent_relationship()
        self.build_transaction_relationship(tx_class)
        return self.version_class
