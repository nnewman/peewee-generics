#!/usr/bin/env python

from distutils.core import setup

setup(name='PeeweeFlaskGenerics',
      version='1.0',
      description='Generic tools for Peewee + Flask',
      author='Neil Newman',
      url='https://github.com/nnewman/peewee-flask-generics/',
      packages=['peewee_generics'],
      install_requires=[
          'flask>=1.0.2,<1.1',
          'flask-classful>=0.14.1,<0.15',
          'marshmallow>=2.15,<2.16',
          'peewee>=3.6.4,<3.7',
          'webargs>=4.0.0,<4.1',
      ]
      )
