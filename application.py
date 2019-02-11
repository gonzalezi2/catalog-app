from flask import Flask, render_template, request, make_response, flash, url_for, redirect
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item, User

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/login')
def show_login():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
  login_session['state'] = state
  return render_template('login.html', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
  # Validate state token
  if request.args.get('state') != login_session['state']:
      response = make_response(json.dumps('Invalid state parameter.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response
      
  #code = request.data.decode('utf-8')
  code = request.data

  try:
      # Upgrade the authorization code into a credentials object
      oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
      oauth_flow.redirect_uri = 'postmessage'
      credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
      response = make_response(
          json.dumps('Failed to upgrade the authorization code.'), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Check that the access token is valid.
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
          % access_token)
  # Submit request, parse response - Python3 compatible
  h = httplib2.Http()
  response = h.request(url, 'GET')[1]
  str_response = response.decode('utf-8')
  result = json.loads(str_response)

  # If there was an error in the access token info, abort.
  if result.get('error') is not None:
      response = make_response(json.dumps(result.get('error')), 500)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Verify that the access token is used for the intended user.
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
      response = make_response(
          json.dumps("Token's user ID doesn't match given user ID."), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Verify that the access token is valid for this app.
  if result['issued_to'] != CLIENT_ID:
      response = make_response(
          json.dumps("Token's client ID does not match app's."), 401)
      response.headers['Content-Type'] = 'application/json'
      return response

  stored_access_token = login_session.get('access_token')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_access_token is not None and gplus_id == stored_gplus_id:
      response = make_response(json.dumps('Current user is already connected.'),
                                200)
      response.headers['Content-Type'] = 'application/json'
      return response

  # Store the access token in the session for later use.
  login_session['access_token'] = access_token
  login_session['gplus_id'] = gplus_id

  # Get user info
  userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
  params = {'access_token': access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params=params)

  data = answer.json()
  print(data)

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']

  # see if user exists, if it doesn't make a new one
  user_id = get_user_id(data["email"])
  if not user_id:
      user_id = create_user(login_session)
  login_session['user_id'] = user_id

  output = ''
  output += '<h1>Welcome, '
  output += login_session['username']
  output += '!</h1>'
  output += '<img src="'
  output += login_session['picture']
  output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
  flash(u"You are now logged in as %s" % login_session['username'], 'success')
  return output

@app.route('/disconnect')
def disconnect():
  access_token = login_session.get('access_token')
  if access_token is None:    
    response= make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]

  if result['status'] == '200':
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(render_template('index.html'), 200)
    response.headers['Content-Type'] = 'text/html'
    flash(u'You have successfully been logged out', 'success')
    return response
  else:
    response = make_response(
      json.dumps('Failed to revoke token for given user.'), 400
    )
    flash(u'Failed to revoke token for given user.', 'error')
    response = make_response(render_template('index.html'), 400)
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
@app.route('/catalog/')
def index():
  categories = session.query(Category).all()
  recentItems = session.query(Item).join(Category, Item.cat_id == Category.id).all()
  # latest_items = session.query(Item)
  return render_template('index.html', categories = categories, recentItems = recentItems)

@app.route('/catalog/new', methods=['GET', 'POST'])
def add_category():
  if 'username' not in login_session:
    flash('Please login before attempting to add a new category')
    return redirect('/login')
  else:
    if request.method == 'GET':
      return render_template('new_category.html')
    else:
      newCategory = Category(name = request.form['name'], user_id = login_session['user_id'])
      session.add(newCategory)
      flash('Successfully added new category: %s' % newCategory.name, 'success')
      session.commit()
      return redirect(url_for('index'))

@app.route('/catalog/<string:category>/', methods=['GET'])
def show_category(category):
  categories = session.query(Category).all()
  #categoryItems = session.query(Item).join(Category).filter_by(name = category).all()
  #print(categoryItems[0])
  return render_template('item.html', categories = categories)

@app.route('/catalog/items/new', methods=['GET', 'POST'])
def add_item():
  if 'username' not in login_session:
    flash('Please login before attempting to add a new item')
    return redirect('/login')
  else:    
    if request.method == 'GET':
      categories = session.query(Category).all()
      return render_template('new_item.html', categories = categories)
    else:
      newItem = Item(
        name = request.form['name'],
        description = request.form['description'],
        cat_id = request.form['category'],
        user_id = login_session['user_id'])
      session.add(newItem)
      flash('Successfully added new category: %s' % newItem.name, 'success')
      session.commit()
      return redirect(url_for('index'))

@app.route('/catalog/<string:category>/<string:item>/', methods=['GET'])
def show_item(category, item):
  return 'This is the %s category %s' % (category, item)

@app.route('/catalog/<string:category>/<string:item>/edit', methods=['GET', 'POST'])
def edit_item(category, item):
  if 'username' not in login_session:
    return render_template('login.html')
  return 'This is the %s category' % category

@app.route('/catalog/<string:category>/<string:item>/delete', methods=['GET', 'POST'])
def delete_item(category, delete):
  if 'username' not in login_session:
    return render_template('/login')
  return 'This is the %s category' % category

def create_user(login_session):
  newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  print(user)
  return user.id

def get_user_info(user_id):
  user = session.query(User).filter_by(id = user_id).one()
  return user

def get_user_id(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user.id
  except:
    return None
  
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)