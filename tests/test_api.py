import pytest

from flask import url_for
from peewee import DoesNotExist

from examples.todo_app import TodoModel


def test_get_items(client, faker):
    items = [faker.random_todo() for _ in range(3)]

    resp = client.get(url_for('TodoApiView:read_many'))

    assert resp.status_code == 200
    assert resp.json
    assert resp.json['count'] == 3
    assert len(resp.json['items']) == 3
    assert ([model_obj.id for model_obj in items]
            == [obj['id'] for obj in resp.json['items']])


def test_get_items_pagination(client, faker):
    items = [faker.random_todo() for _ in range(3)]

    resp = client.get(url_for('TodoApiView:read_many') + '?limit=1&offset=2')

    assert resp.status_code == 200
    assert resp.json
    assert resp.json['count'] == 3
    assert resp.json['limit'] == 1
    assert resp.json['offset'] == 2
    assert resp.json['next']
    assert resp.json['previous']
    assert len(resp.json['items']) == 1
    assert items[1].id == resp.json['items'][0]['id']


def test_get_item(client, faker):
    item = faker.random_todo()

    resp = client.get(url_for('TodoApiView:read_single', item_id=item.id))

    assert resp.status_code == 200
    assert resp.json
    for key, value in resp.json.items():
        assert getattr(item, key) == value


def test_create_item(client, faker):
    data = faker.random_todo_data()

    resp = client.post(url_for('TodoApiView:create_item'), json=data)

    assert resp.status_code == 201
    assert resp.json
    assert resp.json['text'] == data['text']
    assert resp.json['id']


def test_update_item(faker, client):
    item = faker.random_todo()
    new_data = faker.random_todo_data()

    resp = client.put(
        url_for('TodoApiView:put_item', item_id=item.id), json=new_data
    )

    assert resp.status_code == 200
    assert resp.json
    assert resp.json['text'] == new_data['text']
    assert resp.json['id'] == item.id


def test_delete_item(faker, client):
    item = faker.random_todo()

    resp = client.delete(url_for('TodoApiView:delete_item', item_id=item.id))

    assert resp.status_code == 200
    assert resp.json

    with pytest.raises(DoesNotExist):
        TodoModel.get_by_id(item.id)

