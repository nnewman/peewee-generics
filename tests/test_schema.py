import pytest
from marshmallow import ValidationError
from marshmallow.fields import String

from examples.todo_app import TodoSchema
from peewee_generics.schema import GenericSchema


def test_required():

    class TestSchema(GenericSchema):
        required = ('text',)
        text = String(allow_none=True)

    with pytest.raises(ValidationError):
        TestSchema().load({})


def test_allow_none():

    class TestSchema(GenericSchema):
        allow_none = ('text',)
        text = String(allow_none=False)

    assert TestSchema().load({'text': None}).data['text'] is None


def test_meta_model():

    class TestSchema(TodoSchema):
        class Meta:
            model = None

    with pytest.raises(AttributeError):
        TestSchema.make_instance({'text': 'Something'})


def test_exclude():

    class TestSchema(GenericSchema):
        text_one = String(allow_none=True)
        text_two = String(allow_none=True)

    data = TestSchema(exclude=('text_two',)).load(
        {'text_one': 'Test', 'text_two': 'Test'}
    ).data

    assert 'text_one' in data
    assert 'text_two' not in data
