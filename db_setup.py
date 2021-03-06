import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  email = Column(String(250), nullable = False)
  picture = Column(String(250))

  
class Category(Base):
  __tablename__ = 'category'
  id = Column(Integer, primary_key = True)
  name = Column(String(250), nullable = False)
  items = relationship("Item")
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'items': [item.serialize for item in self.items],
      'name': self.name,
      'user_id': self.user_id
    }

class Item(Base):
  __tablename__ = 'item'
  id = Column(Integer, primary_key = True)
  name = Column(String, nullable = False)
  description = Column(String, nullable = False)
  cat_id = Column(Integer, ForeignKey('category.id'))
  user_id = Column(Integer, ForeignKey('user.id'))
  category = relationship(Category)
  user = relationship(User)

  @property
  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'cat_id': self.cat_id,
      'user_id': self.user_id
    }


engine = create_engine('postgresql+psycopg2://catalog:linuxSecret@/catalogdb')

Base.metadata.create_all(engine)
