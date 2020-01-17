from flask import Flask, render_template, request
from flaskext.mysql import MySQL
import register

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST']='34.228.17.80'
app.config['MYSQL_DATABASE_USER']='remote'
app.config['MYSQL_DATABASE_PASSWORD']='Q1w@e3'
app.config['MYSQL_DATABASE_DB']='team23'


mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def index():
    context = register.user(1)
    return render_template('index.html', **context)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        cursor = mysql.get_db().cursor()
        # cursor.execute(f'''call user_login("{request.form['username']}","{request.form['password']}")''')
        result = cursor.callproc('user_login', (request.form['username'], request.form['password']))

        print(result)
        if len(result) > 0:

            return "logged in"
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

@app.route('/register')
def register_user():
    error = None
    if request.method == 'POST':
        cursor = mysql.get_db().cursor()
        result = cursor.callproc('user_registration', (request.form['First Name'], request.form['Last Name'],request.form['Username'],request.form['Password'],request.form['Confirm Password']))
        if request.form['Password']= request.form["Confirm Password"]:
            return "logged in"
        else 
            error= "Invalid login"
    return 'user'
def register_manager_only():
    error = None
    if request.method == 'POST':
     cursor = mysql.get_db().cursor()
     result = cursor.callproc('user_registration', (request.form['First Name'], request.form['Last Name'],request.form['Username'],request.form['Password'],request.form['Confirm Password'],request.form['Street Address], request.form['City'], request.form['State'],request.form['Zipcode']))
     if request.form['Password']= request.form["Confirm Password"]:
            return "logged in"
        else 
            error= "Invalid login"
def register_manager_customer():
    error = None
    if request.method == 'POST':
     cursor = mysql.get_db().cursor()
     result = cursor.callproc('user_registration', (request.form['First Name'], request.form['Last Name'],request.form['Username'],request.form['Password'],request.form['Confirm Password'],request.form['Street Address], request.form['City'], request.form['State'],request.form['Zipcode'], request.form["Credit Card"]))
     if request.form['Password']= request.form["Confirm Password"]:
            return "logged in"
        else 
            error= "Invalid login"
@app.route('/explore')
def explore():
    return ''