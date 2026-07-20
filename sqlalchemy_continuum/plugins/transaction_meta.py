
import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from ..factory import ModelFactory
from .base import Plugin


class TransactionMetaBase:
    transaction_id = sa.Column(sa.BigInteger, primary_key=True)
    key = sa.Column(sa.Unicode(255), primary_key=True)
    value = sa.Column(sa.UnicodeText)


class TransactionMetaFactory(ModelFactory):
    model_name = 'TransactionMeta'

    def create_class(self, manager):
        pass


class TransactionMetaPlugin(Plugin):
    def after_build_tx_class(self, manager):
        pass

    def after_build_models(self, manager):
        pass
