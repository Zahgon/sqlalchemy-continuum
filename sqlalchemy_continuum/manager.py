from functools import wraps

import sqlalchemy as sa
from sqlalchemy.orm import object_session

from ._compat import get_column_key
from .builder import Builder
from .fetcher import SubqueryFetcher, ValidityFetcher
from .operation import Operation
from .plugins import PluginCollection
from .transaction import TransactionFactory
from .unit_of_work import UnitOfWork
from .utils import is_modified, is_versioned, version_table


def tracked_operation(func):
    pass


class VersioningManager:

    def __init__(
        self,
        unit_of_work_cls=UnitOfWork,
        transaction_cls=None,
        user_cls=None,
        options=None,
        plugins=None,
        builder=None,
    ):
        if options is None:
            options = {}
        self.uow_class = unit_of_work_cls
        if builder is None:
            self.builder = Builder()
        else:
            self.builder = builder
        self.builder.manager = self
        self.reset()
        if transaction_cls is not None:
            self.transaction_cls = transaction_cls
        else:
            self.transaction_cls = TransactionFactory()
        if user_cls is not None:
            self.user_cls = user_cls

        self.options = {
            'versioning': True,
            'base_classes': None,
            'table_name': '%s_version',
            'exclude': [],
            'include': [],
            'native_versioning': False,
            'create_models': True,
            'create_tables': True,
            'transaction_column_name': 'transaction_id',
            'end_transaction_column_name': 'end_transaction_id',
            'operation_type_column_name': 'operation_type',
            'strategy': 'validity',
            'use_module_name': False,
            'create_composite_index': True,
        }
        if plugins is None:
            self.plugins = []
        else:
            self.plugins = plugins
        self.options.update(options)

    @property
    def plugins(self):
        pass

    @plugins.setter
    def plugins(self, plugin_collection):
        pass

    def fetcher(self, obj):
        pass

    def reset(self):
        """
        Resets this manager's internal state.

        This method should be used in test cases that create models on the fly.
        Otherwise history_class_map and some other variables would be polluted
        by no more used model classes.
        """
        self.tables = {}
        self.pending_classes = []
        self.association_tables = set()
        self.association_version_tables = set()
        self.declarative_base = None
        self.version_class_map = {}
        self.parent_class_map = {}
        self.session_listeners = {
            'before_flush': self.before_flush,
            'after_flush': self.after_flush,
            'after_commit': self.clear,
            'after_rollback': self.clear,
        }
        self.mapper_listeners = {
            'after_delete': self.track_deletes,
            'after_update': self.track_updates,
            'after_insert': self.track_inserts,
        }
        self.class_config_listeners = {
            'instrument_class': self.builder.instrument_versioned_classes,
            'after_configured': self.builder.configure_versioned_classes,
        }

        self.units_of_work = {}

        self.session_connection_map = {}

        self.metadata = None

    def create_transaction_model(self):
        pass

    def is_excluded_column(self, model, column):
        pass

    def is_excluded_property(self, model, key):
        """
        Returns whether or not given property of given model is excluded from
        the associated history model.

        :param model: SQLAlchemy declarative model object.
        :param key: Model property key
        """
        if key in self.option(model, 'include'):
            return False
        return key in self.option(model, 'exclude')

    def option(self, model, name):
        """
        Returns the option value for given model. If the option is not found
        from given model falls back to default values of this manager object.
        If the option is not found from this manager object either this method
        throws a KeyError.

        :param model: SQLAlchemy declarative object
        :param name: name of the versioning option
        """
        if not hasattr(model, '__versioned__'):
            raise TypeError(f'Model {model!r} is not versioned.')
        try:
            return model.__versioned__[name]
        except KeyError:
            return self.options[name]

    def apply_class_configuration_listeners(self, mapper):
        """
        Applies class configuration listeners for given mapper.

        The listener work in two phases:

        1. Class instrumentation phase
            The first listeners listens to class instrumentation event and
            handles the collecting of versioned models and adds them to
            the pending_classes list.
        2. After class configuration phase
            The second listener listens to after class configuration event and
            handles the actual history model generation based on list that
            was collected during class instrumenation phase.

        :param mapper:
            SQLAlchemy mapper to apply the class configuration listeners to
        """
        for event_name, listener in self.class_config_listeners.items():
            sa.event.listen(mapper, event_name, listener)

    def remove_class_configuration_listeners(self, mapper):
        """
        Remove versioning class configuration listeners from specified mapper.

        :param mapper:
            mapper to remove class configuration listeners from
        """
        for event_name, listener in self.class_config_listeners.items():
            sa.event.remove(mapper, event_name, listener)

    def track_operations(self, mapper):
        """
        Attach listeners for specified mapper that track SQL inserts, updates
        and deletes.

        :param mapper: mapper to track the SQL operations from
        """
        for event_name, listener in self.mapper_listeners.items():
            sa.event.listen(mapper, event_name, listener)

    def remove_operations_tracking(self, mapper):
        """
        Remove listeners from specified mapper that track SQL inserts, updates
        and deletes.

        :param mapper:
            mapper to remove the SQL operations tracking listeners from
        """
        for event_name, listener in self.mapper_listeners.items():
            sa.event.remove(mapper, event_name, listener)

    def track_session(self, session):
        """
        Attach listeners that track the operations (flushing, committing and
        rolling back) of given session. This method should be used in
        conjunction with `track_operations`.

        :param session: SQLAlchemy session to track the operations from
        """
        for event_name, listener in self.session_listeners.items():
            sa.event.listen(session, event_name, listener)

    def remove_session_tracking(self, session):
        """
        Remove listeners that track the operations (flushing, committing and
        rolling back) of given session. This method should be used in
        conjunction with `remove_operations_tracking`.

        :param session:
            SQLAlchemy session to remove the operations tracking from
        """
        for event_name, listener in self.session_listeners.items():
            sa.event.remove(session, event_name, listener)

    @tracked_operation
    def track_inserts(self, uow, target):
        pass

    @tracked_operation
    def track_updates(self, uow, target):
        pass

    @tracked_operation
    def track_deletes(self, uow, target):
        pass

    def unit_of_work(self, session):
        pass

    def _uow_from_conn(self, conn):
        pass

    def before_flush(self, session, flush_context, instances):
        pass

    def after_flush(self, session, flush_context):
        pass

    def clear(self, session):
        pass

    def clear_connection(self, conn):
        pass

    def append_association_operation(self, conn, table_name, params, op):
        pass

    def track_cloned_connections(self, c, opt):
        pass

    def track_association_operations(
        self,
        conn,
        clauseelement,
        multiparams,
        params,
        execution_options,
    ):
        pass
