import peewee
from flask import Flask
from marshmallow import fields, validate
from peewee_generics import (
    GenericView, GenericComponent, GenericSchema, GenericModel, CrudMixin
)


database = peewee.SqliteDatabase('todo.db')


class TodoModel(GenericModel):
    text = peewee.CharField(max_length=255, null=False)

    class Meta:
        database = database


class TodoSchema(GenericSchema):
    text = fields.String(allow_none=False, validate=validate.Length(min=1))

    class Meta:
        model = TodoModel


class TodoComponent(GenericComponent):
    model = TodoModel
    schema = TodoSchema


class TodoApiView(CrudMixin, GenericView):
    component = TodoComponent


def create_app() -> Flask:
    _app = Flask(__name__)
    TodoModel.create_table(safe=True)
    TodoApiView.register(_app)
    return _app


if __name__ == '__main__':
    create_app().run()
