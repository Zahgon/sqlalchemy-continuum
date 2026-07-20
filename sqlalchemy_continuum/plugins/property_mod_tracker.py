
from copy import copy

import sqlalchemy as sa

from .._compat import has_changes
from ..utils import versioned_column_properties
from .base import Plugin


class PropertyModTrackerPlugin(Plugin):
    column_suffix = '_mod'

    def create_mod_column(self, column):
        pass

    def after_build_version_table_columns(self, table_builder, columns):
        pass

    def after_create_version_object(self, uow, parent_obj, version_obj):
        pass

    def after_construct_changeset(self, version_obj, changeset):
        for key in copy(changeset).keys():
            if key.endswith(self.column_suffix):
                del changeset[key]
