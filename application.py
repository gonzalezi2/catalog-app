from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/catalog/')
def show_catalog():
  return 'This is the catalog route!'

@app.route('/catalog/<string:category>/', methods=['GET'])
def show_category(category):
  return 'This is the %s category' % category

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