import pytest

from examples.todo_app import TodoModel


def test_base_query(faker):
    item = faker.random_todo()

    query = TodoModel.base_query()

    assert query.count() == 1
    assert query.get().id == item.id


def test_update_instance(faker):
    item = faker.random_todo()
    item_id = item.id
    new_text = faker.random_todo_data()

    assert item.text != new_text['text']
    item.update_instance(new_text)

    assert item.text == new_text['text']
    assert item.id == item_id


def test_update_instance_invalid_fields(faker):

    class TestModel(TodoModel):
        invalid = False  # Fake type

        class Meta:
            db_table = 'todomodel'

    item = TestModel(text='Something')
    item.save()

    new_text = faker.random_todo_data()

    new_text['invalid'] = 'test'

    with pytest.raises(AttributeError):
        item.update_instance(new_text)
