# Peewee Generics

Peewee-Generics is a minimal library of components I have been using for a few 
years now to prototype Flask applications and build small example projects. It 
is suitable as a starting point for larger scale, more complex projects, but in
itself encompasses all the things you need to build a CRUD API with very little
code (see examples/todo_app.py).

It is:

- Highly opinionated
- Configurable and extensible
- Dependent on core libraries that I use and love

It is **NOT**:

- Meant to tell you the right way to build your application
- Meant to be used in production without some modification
- A learning tool for how to use Peewee
    - All the code you see here is the result of a lot of learning, trial & 
      error, and late nights reading source code
- A way to manage your database migrations or state

## Getting Started

### Installing

Requirements:

- git
- pip

Run:
`pip install git@github.com:nnewman/peewee_generics.git@master#egg=peewee_generics`

### Usage

In your code, you'll first want to extend the components, starting with a 
model.

```python
# models.py
from peewee import SqliteDatabase
from peewee_generics import GenericModel

database = SqliteDatabase('test.db')

class BaseModel(GenericModel):
    class Meta:
        database = database
        
class MyFirstModel(BaseModel):
    # ...your model fields
    pass
```

Then you need a schema for validation of fields for your model.

```python
# schemata.py
from peewee_generics import GenericSchema

from .models import MyFirstModel

class MyFirstSchema(GenericSchema):
    class Meta:
        model = MyFirstModel
        
    # ...schema fields matching your model fields
```

Then, create your component:

```python
# component.py
from peewee_generics import GenericComponent

from .models import MyFirstModel
from .schemata import MyFirstSchema

class MyFirstComponent(GenericComponent):
    model = MyFirstModel
    schema = MyFirstSchema
```

From here, you're able to run full CRUD operations my instantiating an 
instance of `MyFirstComponent` and calling `MyFirstComponent.create_item({})`

For a more complete example, see the examples folder.
