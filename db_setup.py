import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
  __tablename__ = 'category'
  id = Column(Integer, primary_key = True)
  name = Column(String, nullable = False)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name
    }

class Item(Base):
  __tablename__ = 'item'
  id = Column(Integer, primary_key = True)
  name = Column(String, nullable = False)
  description = Column(String, nullable = False)
  cat_id = Column(Integer, ForeignKey('category.id'))
  category = relationship(Category)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'cat_id': self.cat_id
    }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)