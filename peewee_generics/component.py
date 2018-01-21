"""
This module provides generic component methods for your Flask app.

A component is a class which provides the "glue" between your models and your
data marshalling/validation. The advantages to this pattern are that it allows
for extensive code reuse, a single place for business logic, and consistent
handling for validation that leverages the `marshmallow` library.
"""
from abc import ABC

from flask import current_app, url_for

from .model import GenericModel
from .schema import GenericSchema
from .shortcuts import (
    DEFAULT_DICT, MODEL_INST, MODEL_TYPE, SCHEMA_INST, SCHEMA_TYPE, SELECT_INST
)


class GenericComponent(ABC):
    """
    A generic component with all the basics needed to perform CRUD operations
    on a database table via your Python app. This component is designed to be
    extended for your model; simply inherit from it, and specify the
    appropriate model and corresponding schema.
    """
    schema: SCHEMA_TYPE = GenericSchema
    model: MODEL_INST = GenericModel

    def __init__(self, context=DEFAULT_DICT, *args, **kwargs):
        """
        Set context for the class. Context is a great way to pass data around
        the component and methods.
        """
        self.context: dict = context

    @classmethod
    def add_metadata(cls, query: SELECT_INST, context: dict) -> (
            SELECT_INST, dict):
        """
        Add in metadata for API methods. This enables for basic pagination
        support via the schema.
        """
        offset: int = context.get('offset', 1)
        limit: int = context.get('limit', 0)

        total: int = query.count()

        remaining: int = 0
        if query and offset:
            query: SELECT_INST = query.paginate(offset, limit)
            remaining: int = max(
                total - (limit * (offset - 1)) - query.count(), 0
            )

        context['metadata'] = {
            'count': total,
            'remaining': remaining,
            'offset': offset,
            'limit': limit,
            'next': context.get('next') if remaining > 0 else None,
            'previous': context.get('previous') if offset > 1 else None,
            'route_args': context.get('route_args', {}),
        }

        return query, context

    @staticmethod
    def context_urls(route_name: str, **kwargs: dict) -> (str, str):
        """
        Generate next and previous urls for pagination purposes.
        """
        context_next: str = url_for(
            route_name,
            _external=True,
            _scheme='https' if current_app.config.get('USE_HTTPS') else 'http',
            **kwargs
        )

        context_previous: str = url_for(
            route_name,
            _external=True,
            _scheme='https' if current_app.config.get('USE_HTTPS') else 'http',
            **kwargs
        )

        return context_next, context_previous

    def base_query(self) -> SELECT_INST:
        """
        Surface a base query for this model. This method is meant to be
        overridden for the specific model. For instance, if a JOIN condition
        should be part of the default querying, or if query optimization is
        needed, this is an excellent place to put it to avoid bloating the
        models.
        """
        return self.model.base_query()

    def search(self, query: SELECT_INST, request_args: dict=DEFAULT_DICT) -> (
            SELECT_INST):  # pylint: disable=unused-argument
        """
        This method is designed to be overridden to provide an interface for
        searching via query parameters passed in from the endpoint.
        """
        return query

    def get_by_id(self, item_id: int) -> MODEL_TYPE:
        """
        Convenience function for getting an item by ID. This may be overridden,
        for example to provide for permission schemes via business logic in the
        component.
        """
        return self.model.get(self.model.id == item_id)

    def get_items(self, request_args: dict=DEFAULT_DICT,
                  context: dict=DEFAULT_DICT) -> dict:
        """
        Generic method to retrieve all items from the database for the model
        associated with this component, and serialize it to a dictionary via
        the schema. This method is designed to be flexible in filtering results
        via overriding the `search` method.
        """
        items: SELECT_INST = self.search(self.base_query(), request_args)

        if self.context.get('wrapper'):
            items, context = self.add_metadata(items, self.context)

        return self.schema(context=context).dump(items, many=True).data

    def get_item(self, item_id) -> dict:
        """
        Retrieve a specific item from the database for the model associated
        with this component by ID, and serialize it to a dictionary via the
        schema.
        """
        return self.schema().dump(self.get_by_id(item_id), many=False).data

    def create_item(self, data: dict) -> dict:
        """
        Create an item for the associated model. This method will serialize
        and validate the data before model creation, then will serialize the
        return data into a dictionary.
        """
        schema: SCHEMA_INST = self.schema()
        item: MODEL_INST = schema.make_instance(data)
        item.save()
        return schema.dump(item, many=False).data

    def update_item(self, item_id: int, data: dict) -> dict:
        """
        Update an existing item from the database with new data. This method
        will serialize and validate the data before updating the model item,
        then will serialize the return data into a dictionary.
        """
        schema: SCHEMA_INST = self.schema()
        serialized_data: dict = schema.load(data).data
        item: MODEL_INST = self.get_by_id(item_id)
        item.update_instance(serialized_data)

        return schema.dump(item, many=False).data

    def delete_item(self, item_id: int) -> dict:
        """
        Delete an item via ID. This will return the data from the deleted item.
        """
        schema: SCHEMA_INST = self.schema(context=self.context)
        item: MODEL_INST = self.get_by_id(item_id)
        item.delete_instance()
        item.save()

        return schema.dump(item, many=False).data
