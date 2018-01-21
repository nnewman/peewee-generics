import faker
from faker.providers import BaseProvider

from examples.todo_app import TodoModel


faker_instance = faker.Faker()


class TodoProvider(BaseProvider):
    def __init__(self, generator):
        super().__init__(generator)
        self.faker = faker.Faker()

    def random_todo_data(self):
        return {"text": self.faker.sentence()}

    def random_todo(self):
        item = TodoModel(**self.random_todo_data())
        item.save()
        return item


faker_instance.add_provider(TodoProvider)
