"""
This module provides generic classes and methods for routes to your Flask app.
"""

import typing
from functools import wraps

from flask import current_app, jsonify, request, Response
from flask_classful import FlaskView, route
from webargs.flaskparser import FlaskParser

from .component import GenericComponent


parser = FlaskParser()


def login_required(func):
    """
    Here to supplement the classic `flask_login.login_required`

    If the current app isn't configured for flask_login, then it will be
    missing the `login_manager` attribute; we can check for this and proceed
    to call the wrapped function if we have nothing to authenticate with.

    Assuming we do have something to authenticate with, we want to be able to
    conditionally turn off authorization requirements for the route via the
    `<function_name>_UNAUTHORIZED` property.
    """
    @wraps(func)
    def decorated_view(self, *args, **kwargs):
        unauthorized_allowed: str = func.__name__.upper() + '_UNAUTHORIZED'
        if (not hasattr(current_app, 'login_manager')
                or getattr(self, unauthorized_allowed, False)):
            return func(self, *args, **kwargs)
        try:
            from flask_login import login_required
            return login_required(self, *args, **kwargs)(func)
        except ImportError:
            return func(self, *args, **kwargs)
    return decorated_view


class GenericView(FlaskView):
    """
    Add helpers to the basic `flask_classful.FlaskView`. This generic view can
    be overridden and extended to make APIs or web views. (i.e. views that
    render a Jinja2 template)
    """

    route_base: str = '/'
    trailing_slash: bool = False

    component: typing.Type[GenericComponent] = None

    def generate_context(self) -> dict:
        """
        Generate the context that gets passed to a component (as extended from
        `peewee_generics.component.GenericComponent`. This will provision the
        data wrapper for calls to retrieve many items, and provide basic
        pagination support (i.e. counts, limits, offsets, next/previous urls).
        """

        next_url, previous_url = self.component.context_urls(
            request.url_rule.endpoint, **{**request.view_args, **request.args}
        )

        default_context = {
            "wrapper": True,
            "offset": request.args.get('offset', 0, type=int),
            "limit": request.args.get('limit', None, type=int),
            "archived": request.args.get('archived', type=bool),
            "next": next_url,
            "previous": previous_url,
            "route_args": {**request.view_args, **request.args},
            "route_endpoint": request.url_rule.endpoint,
            "current_user": None,
        }

        try:
            from flask_login import current_user
            default_context['current_user'] = current_user
        except ImportError:
            pass

        return default_context


class ApiCreateMixin(GenericView):
    """
    Mixin to add a generic create view to couple in with a component create
    method.
    """

    CREATE_ITEM_UNAUTHORIZED: bool = False

    @route('/', methods=('POST',))
    @login_required
    def create_item(self) -> (Response, int):
        """
        Generic create endpoint attached to the default API path for this
        blueprint. This method will validate input data against the schema
        before any operation is taken. In other words, data validation errors
        get thrown before the call to the component `create_item` method in
        order to avoid database errors and produce consistent responses.

        It is the opinion of the author that proper handling of validation
        errors be attached to the app to provide consistent error formatting.
        """
        comp: GenericComponent = self.component(
            context=self.generate_context()
        )
        data: dict = parser.parse(
            comp.schema.for_serialization, request
        )
        item: dict = comp.create_item(data)
        return jsonify(item), 201


class ApiUpdateMixin(GenericView):
    """
    Mixin to add a generic update view to couple in with a component update
    method.
    """

    PUT_ITEM_UNAUTHORIZED: bool = False

    @route('/<int:item_id>', methods=('PUT',))
    @login_required
    def put_item(self, item_id: int) -> Response:
        """
        Generic update endpoint. This method will validate input data against
        the schema before any operation is taken. In other words, data
        validation errors get thrown before the call to the component
        `create_item` method in order to avoid database errors and produce
        consistent responses.

        It is the opinion of the author that proper handling of validation
        errors be attached to the app to provide consistent error formatting.
        """
        comp: GenericComponent = self.component(
            context=self.generate_context()
        )
        data: dict = parser.parse(
            comp.schema.for_serialization, request
        )
        item: dict = comp.update_item(item_id, data)
        return jsonify(item)


class ApiReadManyMixin(GenericView):
    """
    Mixin to add a generic read view to couple in with a component read method.
    """

    READ_MANY_AUTHORIZED: bool = False

    @route('/')
    @login_required
    def read_many(self) -> Response:
        """
        Generic get many endpoint. This method will get all items from the
        database for the given component/model. It includes built-in pagination
        via query string parameters:

          * limit (int): the maximum number of items per page, default
                unlimited
          * offset (int): the page to view. Can only be used when `limit` is
                provided. Defaults to 1.
        """
        context: dict = self.generate_context()
        comp: GenericComponent = self.component(context=context)
        return jsonify(
            comp.get_items(request_args=request.args, context=context)
        )


class ApiReadSingleMixin(GenericView):
    """
    Mixin to add a generic item getter view to couple in with a component item
    getter method.
    """

    READ_SINGLE_AUTHORIZED: bool = False

    @route('/<int:item_id>')
    @login_required
    def read_single(self, item_id: int) -> Response:
        """
        Generic get single item endpoint. This method will return the specific
        item from the database for the given model by ID. This will raise a
        model-specific instance of `peewee.DoesNotExist` if the item is not
        found.

        It is the opinion of the author that proper handling of DoesNotExist
        errors be attached to the app to provide consistent error formatting.
        """
        context: dict = self.generate_context()
        comp: GenericComponent = self.component(context=context)
        return jsonify(comp.get_item(item_id))


class ApiDeleteMixin(GenericView):
    """
    Mixin to add a generic delete view to couple in with a component delete
    method.
    """

    DELETE_ITEM_UNAUTHORIZED: bool = False

    @route('/<int:item_id>', methods=('DELETE',))
    @login_required
    def delete_item(self, item_id: int) -> Response:
        """
        Generic delete item endpoint. This item will remove the item from the
        database as specified by ID, returning the data from the just-deleted
        item.
        """
        context: dict = self.generate_context()
        comp: GenericComponent = self.component(context=context)
        return jsonify(comp.delete_item(item_id))


class CrudMixin(ApiCreateMixin, ApiReadManyMixin, ApiReadSingleMixin,
                ApiUpdateMixin, ApiDeleteMixin):
    """
    Mixin to couple all CRUD methods in via a single inherited class
    """
