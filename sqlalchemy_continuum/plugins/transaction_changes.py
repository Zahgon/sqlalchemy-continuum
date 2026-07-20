
import sqlalchemy as sa

from ..factory import ModelFactory
from .base import Plugin


class TransactionChangesBase:
    transaction_id = sa.Column(sa.BigInteger, primary_key=True)
    entity_name = sa.Column(sa.Unicode(255), primary_key=True)


class TransactionChangesFactory(ModelFactory):
    model_name = 'TransactionChanges'

    def create_class(self, manager):
        pass


class TransactionChangesPlugin(Plugin):
    def after_build_tx_class(self, manager):
        pass

    def after_build_models(self, manager):
        pass

    def before_create_version_objects(self, uow, session):
        pass

    def after_version_class_built(self, parent_cls, version_cls):
        pass
