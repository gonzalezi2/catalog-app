from flask import Flask, render_template, request, make_response, flash
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
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
  login_session['state'] = state
  return render_template('login.html', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
  if request.args.get('state') != login_session['state']:
    response = make_response(json.dumps('Invalid state parameter'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  code = request.data
  try:
    oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
    oauth_flow.redirect_uri = 'postmessage'
    credentials = oauth_flow.step2_exchange(code)
  except FlowExchangeError:
    response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = credentials.access_token
  url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
  h = httplib2.Http()
  result = json.loads(h.request(url, 'GET')[1])
  if result.get('error') is not None:
    response = make_response(json.dumps(result.get('error')), 50)
    response.headers['Content-Type'] = 'application/json'
  gplus_id = credentials.id_token['sub']
  if result['user_id'] != gplus_id:
    response = make_response(
      json.dumps("Token's user ID doesn't match the given user ID."), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  if result['issued_to'] != CLIENT_ID:
    response = make_response(
      json.dumps("Token's client ID does not match app's."), 401)
    print("Token's client ID does not match app's.")
    response.headers['Content-Type'] = 'application/json'
    return response

  stored_credentials = login_session.get('credentials')
  stored_gplus_id = login_session.get('gplus_id')
  if stored_credentials is not None and gplus_id == stored_gplus_id:
    flash('Current user is already connected.')
    response = make_response(json.dumps('Successfully disconnected'), 200)
    response.headers['Content-Type'] = 'application/json'

  login_session['credentials'] = credentials
  login_session['gplus_id'] = gplus_id

  userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
  params = {'access_token': credentials.access_token, 'alt': 'json'}
  answer = requests.get(userinfo_url, params = params)
  data = json.loads(answer.text)

  login_session['username'] = data['name']
  login_session['picture'] = data['picture']
  login_session['email'] = data['email']
  print(login_session['picture'])
  output = '<h1>Welcome, %s</h1><img src=\'%s\' style="width:300px; height: 300px; border-radius: 50%%\'>' % (login_session['username'], login_session['picture'])
  return output

@app.route('/disconnect')
def disconnect():
  credentials = login_session.get('credentials')
  if credentials is None:
    response= make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  access_token = credentials.access_token
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]

  if result['status'] == '200':
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    response = make_response(render_template('index.html'), 200)
    response.headers['Content-Type'] = 'text/html'
    return response
  else:
    response = make_response(
      json.dumps('Failed to revoke token for given user.'), 400
    )
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/')
@app.route('/catalog/')
def index():
  categories = session.query(Category).all()
  recentItems = session.query(Item).all()
  # latest_items = session.query(Item)
  return render_template('index.html', categories = categories, recentItems = recentItems)

@app.route('/catalog/new', methods=['GET', 'POST'])
def new_catalog():
  if request.method == 'GET':
    return render_template('newCategory.html')
  else:
    return 'this is the post route'

@app.route('/catalog/<string:category>/', methods=['GET'])
def show_category(category):
  categories = session.query(Category).all()
  #categoryItems = session.query(Item).join(Category).filter_by(name = category).all()
  #print(categoryItems[0])
  return render_template('item.html', categories = categories)

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
    return render_template('login.html')
  return 'This is the %s category' % category

def create_user(login_session):
  newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email = login_session['email']).one()
  return user.id

def getUserInfo(user_id):
  user = session.query(User).filter_by(id = user_id).one()
  return user

def getUserID(email):
  try:
    user = session.query(User).filter_by(email = email).one()
    return user
  except:
    return None
  
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)