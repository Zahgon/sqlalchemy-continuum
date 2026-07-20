
import json
from collections.abc import Iterable
from inspect import isclass

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import ColumnProperty, attributes, class_mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.interfaces import MapperProperty, PropComparator
from sqlalchemy.orm.session import _state_session
from sqlalchemy.util import set_creation_order

try:
    from sqlalchemy.dialects.postgresql import JSON

    has_postgres_json = True
except ImportError:
    has_postgres_json = False




class ImproperlyConfigured(Exception):
    pass




def get_declarative_base(model):
    pass


def naturally_equivalent(obj, obj2):
    """
    Returns whether or not two given SQLAlchemy declarative instances are
    naturally equivalent (all their non primary key properties are equivalent).

    ::

        from sqlalchemy_continuum._compat import naturally_equivalent

        user = User(name='someone')
        user2 = User(name='someone')

        user == user2  # False

        naturally_equivalent(user, user2)  # True

    :param obj: SQLAlchemy declarative model object
    :param obj2: SQLAlchemy declarative model object to compare with `obj`
    """
    for column_key, column in sa.inspect(obj.__class__).columns.items():
        if column.primary_key:
            continue

        if not (getattr(obj, column_key) == getattr(obj2, column_key)):
            return False
    return True




def get_columns(mixed):
    """
    Return a collection of all Column objects for given SQLAlchemy object.

    The type of the collection depends on the type of the object to return the
    columns from.

    ::

        get_columns(User)
        get_columns(User())
        get_columns(User.__table__)
        get_columns(User.__mapper__)
        get_columns(sa.orm.aliased(User))
        get_columns(sa.orm.aliased(User.__table__))

    :param mixed:
        SA Table object, SA Mapper, SA declarative class, SA declarative class
        instance or an alias of any of these objects
    """
    if isinstance(mixed, sa.sql.selectable.Selectable):
        try:
            return mixed.selected_columns
        except AttributeError:  # SQLAlchemy <1.4
            return mixed.c
    if isinstance(mixed, sa.orm.util.AliasedClass):
        return sa.inspect(mixed).mapper.columns
    if isinstance(mixed, sa.orm.Mapper):
        return mixed.columns
    if isinstance(mixed, InstrumentedAttribute):
        return mixed.property.columns
    if isinstance(mixed, ColumnProperty):
        return mixed.columns
    if isinstance(mixed, sa.Column):
        return [mixed]
    if not isclass(mixed):
        mixed = mixed.__class__
    return sa.inspect(mixed).columns


def get_primary_keys(mixed):
    """
    Return a dict of all primary keys for given Table object,
    declarative class or declarative class instance. The dict preserves
    column definition order.

    :param mixed:
        SA Table object, SA declarative class or SA declarative class instance

    ::

        get_primary_keys(User)
        get_primary_keys(User())
        get_primary_keys(User.__table__)
        get_primary_keys(User.__mapper__)
        get_primary_keys(sa.orm.aliased(User))
        get_primary_keys(sa.orm.aliased(User.__table__))
    """
    return {
        key: column for key, column in get_columns(mixed).items() if column.primary_key
    }


def identity(obj_or_class):
    pass


def get_column_key(model, column):
    pass


def has_changes(obj, attrs=None, exclude=None):
    """
    Simple shortcut function for checking if given attributes of given
    declarative model object have changed during the session. Without
    parameters this checks if given object has any modifications. Additionally
    exclude parameter can be given to check if given object has any changes
    in any attributes other than the ones given in exclude.

    ::

        from sqlalchemy_continuum._compat import has_changes

        user = User()

        has_changes(user, 'name')  # False

        user.name = 'someone'

        has_changes(user, 'name')  # True

        has_changes(user)  # True

    You can check multiple attributes as well.
    ::

        has_changes(user, ['age'])  # True
        has_changes(user, ['name', 'age'])  # True

    This function also supports excluding certain attributes.

    ::

        has_changes(user, exclude=['name'])  # False
        has_changes(user, exclude=['age'])  # True

    :param obj: SQLAlchemy declarative model object
    :param attrs: Names of the attributes
    :param exclude: Names of the attributes to exclude
    """
    if attrs:
        if isinstance(attrs, str):
            return sa.inspect(obj).attrs.get(attrs).history.has_changes()
        else:
            return any(has_changes(obj, attr) for attr in attrs)
    else:
        if exclude is None:
            exclude = []
        return any(
            attr.history.has_changes()
            for key, attr in sa.inspect(obj).attrs.items()
            if key not in exclude
        )




def _get_class_registry(class_):
    """
    Helper function to get the class registry for SQLAlchemy models.
    Handles differences between SQLAlchemy versions.
    """
    try:
        return class_.registry._class_registry
    except AttributeError:  # SQLAlchemy <1.4
        return class_._decl_class_registry



if not has_postgres_json:

    class PostgresJSONType(sa.types.UserDefinedType):

        def get_col_spec(self):
            pass

    ischema_names['json'] = PostgresJSONType


class JSONType(sa.types.TypeDecorator):

    impl = sa.UnicodeText
    hashable = False
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        pass

    def process_bind_param(self, value, dialect):
        pass

    def process_result_value(self, value, dialect):
        pass




class GenericAttributeImpl(attributes.ScalarAttributeImpl):

    def __init__(self, *args, **kwargs):
        """
        The constructor of attributes.AttributeImpl changed in SQLAlchemy 2.0.22,
        adding a 'default_function' required positional argument before 'dispatch'.
        This adjustment ensures compatibility across versions by inserting None for
        'default_function' in versions >= 2.0.22.

        Arguments received: (class, key, dispatch)
        Required by AttributeImpl: (class, key, default_function, dispatch)
        Setting None as default_function here.
        """
        sqlalchemy_version = tuple(map(int, sa.__version__.split('.')))
        if sqlalchemy_version >= (2, 0, 22):
            args = (*args[:2], None, *args[2:])

        super().__init__(*args, **kwargs)

    def get(self, state, dict_, passive=attributes.PASSIVE_OFF):
        if self.key in dict_:
            return dict_[self.key]

        session = _state_session(state)
        if session is None:
            return None

        discriminator = self.get_state_discriminator(state)
        target_class = _get_class_registry(state.class_).get(discriminator)

        if target_class is None:
            return None

        id = self.get_state_id(state)

        target = session.get(target_class, id)

        return target

    def get_state_discriminator(self, state):
        discriminator = self.parent_token.discriminator
        if isinstance(discriminator, hybrid_property):
            return getattr(state.obj(), discriminator.__name__)
        else:
            return state.attrs[discriminator.key].value

    def get_state_id(self, state):
        return tuple(state.attrs[id.key].value for id in self.parent_token.id)

    def set(
        self,
        state,
        dict_,
        initiator,
        passive=attributes.PASSIVE_OFF,
        check_old=None,
        pop=False,
    ):
        pass


class GenericRelationshipProperty(MapperProperty):

    def __init__(self, discriminator, id, doc=None):
        super().__init__()
        self._discriminator_col = discriminator
        self._id_cols = id
        self._id = None
        self._discriminator = None
        self.doc = doc

        set_creation_order(self)

    def _column_to_property(self, column):
        pass

    def init(self):
        pass

    class Comparator(PropComparator):
        def __init__(self, prop, parentmapper):
            self.property = prop
            self._parententity = parentmapper

        def __eq__(self, other):
            discriminator = type(other).__name__
            q = self.property._discriminator_col == discriminator
            other_id = identity(other)
            for index, id in enumerate(self.property._id_cols):
                q &= id == other_id[index]
            return q

        def __ne__(self, other):
            return ~(self == other)

        def is_type(self, other):
            pass

    def instrument_class(self, mapper):
        pass


def generic_relationship(*args, **kwargs):
    pass
