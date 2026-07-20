from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles

from .dialects.postgresql import (
    CreateTemporaryTransactionTableSQL,
    InsertTemporaryTransactionSQL,
    TransactionTriggerSQL,
)
from .exc import ImproperlyConfigured
from .factory import ModelFactory


def utc_now():
    pass


@compiles(sa.types.BigInteger, 'sqlite')
def compile_big_integer(element, compiler, **kw):
    pass


class NoChangesAttribute(Exception):
    pass


class TransactionBase:
    issued_at = sa.Column(sa.DateTime, default=utc_now)

    @property
    def entity_names(self):
        pass

    @property
    def changed_entities(self):
        pass


procedure_sql = """
CREATE OR REPLACE FUNCTION transaction_temp_table_generator()
RETURNS TRIGGER AS $$
BEGIN
    {temporary_transaction_sql}
    INSERT INTO temporary_transaction (id) VALUES (NEW.id);
    RETURN NEW;
END;
$$
LANGUAGE plpgsql
"""


def create_triggers(cls):
    pass


class TransactionFactory(ModelFactory):
    model_name = 'Transaction'

    def __init__(self, remote_addr=True):
        self.remote_addr = remote_addr

    def create_class(self, manager):
        pass
