
import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect

from .._compat import JSONType, generic_relationship
from ..factory import ModelFactory
from ..utils import version_class, version_obj
from .base import Plugin


class ActivityBase:
    id = sa.Column(
        sa.BigInteger,
        sa.schema.Sequence('activity_id_seq'),
        primary_key=True,
        autoincrement=True,
    )

    verb = sa.Column(sa.Unicode(255))

    @hybrid_property
    def actor(self):
        pass


class ActivityFactory(ModelFactory):
    model_name = 'Activity'

    def create_class(self, manager):
        pass


class ActivityPlugin(Plugin):
    activity_cls = None

    def after_build_models(self, manager):
        pass

    def is_session_modified(self, session):
        """
        Return that the session has been modified if the session contains an
        activity class.

        :param session: SQLAlchemy session object
        """
        return any(isinstance(obj, self.activity_cls) for obj in session)

    def before_flush(self, uow, session):
        pass

    def after_version_class_built(self, parent_cls, version_cls):
        pass
