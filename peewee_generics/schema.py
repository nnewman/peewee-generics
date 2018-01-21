"""
This module provides some tools for marshmallow schemata that make use in an
API-driven application easier, also adding convenience and utility around some
built-in functionality.
"""
from __future__ import annotations

from marshmallow import fields, Schema, post_dump, validate

from .shortcuts import (ITERABLE, MODEL_INST, MODEL_TYPE)


class GenericSchema(Schema):
    """
    Generic schema class to be extended from by your individual data models.
    """
    remove_fields: ITERABLE = ()
    required: ITERABLE = ()
    allow_none: ITERABLE = ()

    id = fields.Integer(allow_none=True, validate=validate.Range(min=1))

    class Meta:
        """
        Override this to add a model attribute. This enables the class to
        behave in a similar fashion to `marshmallow-sqlalchemy.ModelSchema`
        """
        model: (MODEL_TYPE, None) = None
        dateformat: str = '%Y-%m-%dT%H:%M:%S+00:00'

    def __init__(self, *args, **kwargs) -> None:
        """
        Set some attributes on schema initialization through similar means used
        elsewhere in this toolset; i.e. through `context`.
        """
        super().__init__(*args, **kwargs)

        # Pass in extra kwargs through context
        context: dict = kwargs.get('context', {})

        self.strict: bool = True  # Strong validation
        self.ordered: bool = True  # Order by field definition

        for _attr in ('required', 'allow_none'):
            attr: ITERABLE = getattr(self, _attr, ())
            if attr and isinstance(attr, (tuple, list)):
                for field in attr:
                    setattr(self.fields[field], _attr, True)

        if (isinstance(context, dict) and context.get('exclude')
                and isinstance(context.get('exclude'), (tuple, list))):
            self.exclude: ITERABLE = context['exclude']

    @classmethod
    def make_instance(cls, data: dict) -> MODEL_INST:
        """
        Create a model instance for the model associated with this schema based
        on input data, validating it before creation. The `save` method is not
        included here to explicitly allow for control of that outside the
        schema and provide better convenience for atomic transactions if these
        are necessary.
        """
        klass: cls = cls()

        if not klass.Meta.model:
            raise AttributeError("Missing model class to make instance")

        serialized_data: dict = klass.load(data).data
        return klass.Meta.model(**serialized_data)

    @classmethod
    def _strip_data(cls, request_data: dict) -> None:
        for field in cls.remove_fields:
            request_data.pop(field, None)

    @classmethod
    def for_serialization(cls, request) -> GenericSchema:
        many = False
        if request.mimetype == 'multipart/form-data':
            cls._strip_data(request.form)
        elif request.mimetype == 'application/json':
            if (isinstance(request.json, list)
                    and all([isinstance(_, dict) for _ in request.json])):
                many = True
            cls._strip_data(request.json)
        else:
            raise AttributeError('Incorrect mimetype for serialization')

        return cls(context={
            'return_dict': True, 'convert_fks': False, 'convert_dates': False
        }, many=many)

    def wrap_data(self, data: dict) -> dict:
        if 'metadata' in self.context and not self.context.get('child'):
            _data = self.context['metadata']
            _data['items'] = data
            return _data
        return data

    @post_dump(pass_many=True)
    def wrap_with_wrapper(self, data: dict, many: bool) -> dict:
        return self.wrap_data(data)
