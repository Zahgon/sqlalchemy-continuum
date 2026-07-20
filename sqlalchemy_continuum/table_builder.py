import sqlalchemy as sa


class ColumnReflector:
    def __init__(self, manager, parent_table, model=None):
        self.parent_table = parent_table
        self.model = model
        self.manager = manager

    def option(self, name):
        try:
            return self.manager.option(self.model, name)
        except TypeError:
            return self.manager.options[name]

    def reflect_column(self, column):
        pass

    @property
    def operation_type_column(self):
        pass

    @property
    def transaction_column(self):
        pass

    @property
    def end_transaction_column(self):
        pass

    @property
    def reflected_parent_columns(self):
        pass

    def __iter__(self):
        yield from self.reflected_parent_columns

        if not self.model or not sa.inspect(self.model).single:
            yield self.transaction_column
            if self.option('strategy') == 'validity':
                yield self.end_transaction_column
            yield self.operation_type_column


class TableBuilder:

    def __init__(self, versioning_manager, parent_table, model=None):
        self.manager = versioning_manager
        self.parent_table = parent_table
        self.model = model

    def option(self, name):
        try:
            return self.manager.option(self.model, name)
        except TypeError:
            return self.manager.options[name]

    @property
    def table_name(self):
        pass

    @property
    def columns(self):
        pass

    def _build_composite_indexes(self, table):
        pass

    def __call__(self, extends=None):
        """
        Builds version table.
        """
        columns = self.columns if extends is None else []
        self.manager.plugins.after_build_version_table_columns(self, columns)
        table = sa.schema.Table(
            extends.name if extends is not None else self.table_name,
            self.parent_table.metadata,
            *columns,
            schema=self.parent_table.schema,
            extend_existing=extends is not None,
        )

        if extends is None:
            for _ in self._build_composite_indexes(table):
                pass

        return table
