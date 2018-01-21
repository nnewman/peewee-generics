import typing

from marshmallow.schema import Schema
from peewee import ModelSelect
from playhouse.signals import Model
from werkzeug.datastructures import ImmutableDict

###############################################################################
# TYPE SHORTCUTS
###############################################################################

SELECT_INST = ModelSelect

MODEL_INST = Model
MODEL_TYPE = typing.Type[MODEL_INST]

SCHEMA_INST = Schema
SCHEMA_TYPE = typing.Type[SCHEMA_INST]

ITERABLE = (typing.Tuple[str], typing.List[str])

###############################################################################
# ARG DEFAULTS
###############################################################################

DEFAULT_DICT = ImmutableDict()
