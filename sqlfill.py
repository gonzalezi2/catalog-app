
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

session.add_all([
    Category(name='Soccer'),
    Category(name='Baseketball'),
    Category(name='Baseball'),
    Category(name='Frisbee'),
    Category(name='Snowboarding'),
    Category(name='Rock Climbing'),
    Category(name='Foosball'),
    Category(name='Skating'),
    Category(name='Hockey')
  ])

session.commit()