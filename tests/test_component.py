import pytest
from peewee import DoesNotExist

from examples.todo_app import TodoComponent


def test_get_item(faker):
    item = faker.random_todo()
    item_dict = TodoComponent().get_item(item.id)

    for key, value in item_dict.items():
        assert getattr(item, key) == value


def test_get_items(faker):
    items = [faker.random_todo() for _ in range(3)]
    items_dict = TodoComponent().get_items()

    assert len(items_dict) == 3
    assert ([model_obj.id for model_obj in items]
            == [obj['id'] for obj in items_dict])


def test_get_items_with_wrapper(faker):
    items = [faker.random_todo() for _ in range(3)]
    context = {'wrapper': True}
    items_dict = TodoComponent(context=context).get_items()

    assert items_dict['count'] == 3
    assert len(items_dict['items']) == 3
    assert ([model_obj.id for model_obj in items]
            == [obj['id'] for obj in items_dict['items']])


def test_get_items_with_wrapper_pagination(faker):
    items = [faker.random_todo() for _ in range(3)]
    context = {'wrapper': True, 'limit': 1, 'offset': 2}
    items_dict = TodoComponent(context=context).get_items()

    assert items_dict['count'] == 3
    assert items_dict['limit'] == 1
    assert items_dict['offset'] == 2
    assert len(items_dict['items']) == 1
    assert items[1].id == items_dict['items'][0]['id']


def test_create_item(faker):
    data = faker.random_todo_data()
    item = TodoComponent().create_item(data)

    assert item['text'] == data['text']
    assert item['id']


def test_update_item(faker):
    item = faker.random_todo()
    new_data = faker.random_todo_data()
    new_item = TodoComponent().update_item(item.id, new_data)

    assert new_item['text'] == new_data['text']
    assert new_item['id'] == item.id


def test_delete_item(faker):
    item = faker.random_todo()
    TodoComponent().delete_item(item.id)

    with pytest.raises(DoesNotExist):
        TodoComponent().get_item(item.id)
