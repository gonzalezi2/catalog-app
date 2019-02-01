from flask import Flask, render_template, request
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
def index():
  categories = session.query(Category).all()
  # latest_items = session.query(Item)
  return render_template('index.html', categories = categories)

@app.route('/catalog/')
def show_catalog():
  categories = session.query(Category).all()
  recentItems = session.query(Item).all()[10]
  # latest_items = session.query(Item)
  return render_template('index.html', categories = categories, recentItems = recentItems)

@app.route('/catalog/<string:category>/', methods=['GET'])
def show_category(category):
  categories = session.query(Category).all()
  categoryItems = session.query(Item).join(Category).filter_by(name = category).all()
  print(categoryItems[0])
  return render_template('item.html', categories = categories, categoryItems = categoryItems)

@app.route('/catalog/<string:category>/<string:item>/', methods=['GET'])
def show_item(category, item):
  return 'This is the %s category %s' % (category, item)

@app.route('/catalog/<string:category>/<string:item>/edit', methods=['GET', 'POST'])
def edit_item(category, item):
  return 'This is the %s category' % category

@app.route('/catalog/<string:category>/<string:item>/delete', methods=['GET', 'POST'])
def delete_item(category, delete):
  return 'This is the %s category' % category

  
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)