"""
This module provides an updated model to extend, adding some minor convenience
functions.
"""
from __future__ import annotations

from abc import ABCMeta

import peewee
from playhouse.signals import Model

from .shortcuts import SELECT_INST


class GenericModel(Model):
    """
    Base model instance for your application.
    """

    class Meta(ABCMeta):
        """
        Your application should create it's own GenericModel for all models,
        which will set the right `database` attribute for all models.
        """
        database: peewee.Database = None

    @classmethod
    def base_query(cls) -> SELECT_INST:
        """
        A default query. Use this to exclude certain fields or add default
        joins.

        It is the opinion of the author that default query behavior
        should be added at the component level, with minimal business or
        functional logic provided in the model.
        """
        return cls.select()

    def update_instance(self, data: dict) -> GenericModel:
        """
        A method to update a model instance based on input data. This is a
        safe method, in that it will not destroy existing data if the existing
        data is not passed in via the `data` dict. It is intended that this
        method is used to update changed fields, however it could be used to
        update all fields.
        """
        for key, val in data.items():
            if not isinstance(getattr(self.__class__, key), peewee.Field):
                raise AttributeError(
                    f'Missing field for {key} on {self.__class__.__name__}'
                )

            setattr(self, key, val)

        self.save()
        return self
