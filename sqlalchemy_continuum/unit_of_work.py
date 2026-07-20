from copy import copy

import sqlalchemy as sa

from ._compat import get_primary_keys, identity
from .operation import Operations
from .utils import (
    end_tx_column_name,
    is_session_modified,
    tx_column_name,
    version_class,
    versioned_column_properties,
)


class UnitOfWork:
    def __init__(self, manager):
        self.manager = manager
        self.reset()

    def reset(self, session=None):
        """
        Reset the internal state of this UnitOfWork object. Normally this is
        called after transaction has been committed or rolled back.
        """
        self.version_session = None
        self.current_transaction = None
        self.operations = Operations()
        self.pending_statements = []
        self.version_objs = {}

    def is_modified(self, session):
        """
        Return whether or not given session has been modified. Session has been
        modified if any versioned property of any version object in given
        session has been modified or if any of the plugins returns that
        session has been modified.

        :param session: SQLAlchemy session object
        """
        return is_session_modified(session) or any(
            self.manager.plugins.is_session_modified(session)
        )

    def process_before_flush(self, session):
        pass

    def process_after_flush(self, session):
        pass

    def transaction_args(self, session):
        pass

    def create_transaction(self, session):
        pass

    def get_or_create_version_object(self, target):
        pass

    def process_operation(self, operation):
        pass

    def create_version_objects(self, session):
        pass

    def version_validity_subquery(self, parent, version_obj, alias=None):
        pass

    def update_version_validity(self, parent, version_obj):
        pass

    def create_association_versions(self, session):
        pass

    def make_versions(self, session):
        pass

    @property
    def has_changes(self):
        """
        Return whether or not this unit of work has changes.
        """
        return self.operations or self.pending_statements

    def assign_attributes(self, parent_obj, version_obj):
        pass
