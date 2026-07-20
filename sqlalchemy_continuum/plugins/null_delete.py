from ..operation import Operation
from ..utils import is_internal_column, versioned_column_properties
from .base import Plugin


class NullDeletePlugin(Plugin):
    def should_nullify_column(self, version_obj, prop):
        pass

    def after_create_version_object(self, uow, parent_obj, version_obj):
        pass
