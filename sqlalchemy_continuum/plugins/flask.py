
from .._compat import ImproperlyConfigured
from .base import Plugin

flask = None
try:
    import flask
    from flask import has_app_context, has_request_context, request
except ImportError:
    pass


def fetch_current_user_id():
    pass


def fetch_remote_addr():
    pass


class FlaskPlugin(Plugin):
    def __init__(self, current_user_id_factory=None, remote_addr_factory=None):
        self.current_user_id_factory = (
            fetch_current_user_id
            if current_user_id_factory is None
            else current_user_id_factory
        )
        self.remote_addr_factory = (
            fetch_remote_addr if remote_addr_factory is None else remote_addr_factory
        )

        if not flask:
            raise ImproperlyConfigured(
                'Flask is required with FlaskPlugin. Please install Flask by'
                ' running pip install Flask'
            )

    def transaction_args(self, uow, session):
        pass
