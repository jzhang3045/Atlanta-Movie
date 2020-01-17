from flask import Flask, render_template, request, url_for, redirect, make_response, g, session
from utils import *
from register import *

app = Flask(__name__)

app.config['MYSQL_DATABASE_HOST']='3.90.186.137'
app.config['MYSQL_DATABASE_USER']='remote'
app.config['MYSQL_DATABASE_PASSWORD']='Q1w@e3'
app.config['MYSQL_DATABASE_DB']='team23'
app.secret_key = 'cs440019fall'
mysql.init_app(app)


@app.before_request
def load_user():
    if session.get('username'):
        user = {
            'username':session['username'],
            'is_admin': session.get('is_admin'),
            'is_customer': session.get('is_customer'),
            'is_manager': session.get('is_manager'),
        }
    else:
        user = None

    g.user = user

@app.route('/')
def index():
    if g.get('user'):
        # we add username in cookies as auth
        # if it is there, we redirect user to a screen
        return render_template('index.html')
    else:
        return redirect(url_for('login', next=request.path))


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        cursor = mysql.get_db().cursor()
        # cursor.execute(f'''call user_login("{request.form['username']}","{request.form['password']}")''')
        cursor.callproc('user_login', (request.form['username'], request.form['password']))
        user = cursor.fetchone()
        cursor.close()
        if user:
            g.user = user
            session.clear()
            session['username'] = user[0]
            session['is_admin'] = user[3]
            session['is_manager'] = user[4]
            session['is_customer'] = user[2]
            return redirect(request.args.get('next','/'))
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    error = None
    if request.method == 'POST':
        role = request.form['role']
        if role == 'user':
            error = register_user(request.form)
        elif role == 'customer':
            error = register_customer(request.form)
        elif role == 'manager':
            error = register_manager(request.form)  
        elif role == 'manager-customer':
            error = register_customermanager(request.form)
        if not error:
            return redirect(url_for('login')) 
    context = {
        'companies': get_companies2(),
        'error': error
    }
    return render_template('register.html', **context)


@app.route('/explore-movie', methods=['GET', 'POST'])
def explore_movie():
    if request.method == 'POST':
        credit_card = request.form.get('credit_card')
        execute_proc('customerviewmov',(credit_card,))
        return redirect(url_for('view_history'))
    context = {
        'cities': get_cities(),
        'movies': get_movies(),
        'companies': get_companies(),
        'states': get_states(),
        'credit_cards': get_credit_cards(g.user['username']),
    }
    mov_name = request.args.get('movie', '')
    company_name = request.args.get('company', '')
    city = request.args.get('city', '')
    state = request.args.get('state', '')
    minMovPlayDate = request.args.get('from_date', None)
    maxMovPlayDate = request.args.get('to_date', None)
    
    result = fetch_proc('customer_filter_mov',(mov_name, company_name, city, state, minMovPlayDate, maxMovPlayDate))
    context['result'] = result
    return render_template('exploreMovie.html', **context)

@app.route('/view-history', methods=['GET'])
def view_history():
    result = fetch_proc('customer_view_history',(g.user['username'],))
    return render_template('viewHistory.html', result=result)

@app.route('/visit-history', methods=['GET'])
def visit_history():
    comName = request.args.get('company', '')
    min_visit = request.args.get('from_date', None)
    max_visit = request.args.get('to_date', None)
    temp = fetch_proc('user_filter_visitHistory',(g.user['username'], min_visit, max_visit))
    result = [
        [t[0], ', '.join(t[1:3])+' '+t[4], t[5], t[6]]
        for t in temp if (comName == '' or t[5] == comName)
    ]
    context = {
        'result': result,
        'companies': get_companies(),
    }
    return render_template('visitHistory.html', **context)

@app.route('/explore-theater', methods=['GET'])
def explore_theater():
    context = {
        'cities': get_cities(),
        'companies': get_companies(),
        'states': get_states(),
        'theaters': get_theaters(),
    }
    thName = request.args.get('theater', '')
    thCity = request.args.get('city', '')
    thState = request.args.get('state', '')
    comName = request.args.get('company', '')
    result = fetch_proc('user_filter_th',(thName, comName, thCity, thState))
    context['result'] = result
    return render_template('exploreTheater.html', **context)

@app.route('/create-theater', methods=['GET','POST'])
def admin_create_theater():
    context = {
        'companies': get_companies(),
        'states': get_states(),
        'managers': get_managers()
    }
    if request.method == 'POST':
        execute_proc('admin_create_theater', (request.form['Name'], request.form['Company'],request.form['Street Address'], request.form['City'], request.form['State'], request.form['Zipcode'], request.form['Capacity']))
        #result = cursor.callproc('admin_create_theater', (request.form['Name'], request.form['Company'], request.form['Street Address'], request.form['City'], request.form['State'], request.form['Zipcode'], request.form['Capacity'], request.form['Manager'])
    return render_template('admin_create_theater.html', **context)


@app.route('/manage-user', methods=['GET', 'POST'])
def manage_user():
    if request.method == 'POST':
        print(request.form)
        update_user(request.form['username'], request.form['status'])
    users = get_users(request.args.get('username'), request.args.get('status'))
    status = ('Approved', 'Pending', 'Declined')
    context = {
        'users': users,
        'status': status,
    }
    return render_template('manageUser.html', **context)


@app.route('/create-movie', methods=['GET','POST'])
def admin_create_movie():
    if request.method == 'POST':
        execute_proc('admin_create_mov', (request.form['Name'],request.form['Duration'], request.form['Release Date']))
    return render_template('admin_create_mov.html')

@app.route('/company-detail', methods=['GET'])
def admin_company_detail():
    comName = request.args.get('comName')
    company = one_company(comName)
    employee = certain_employee(comName)
    context = {
        'comName':comName,
        'company':company,
        'employee':', '.join([e[0] for e in employee])
    }
    return render_template('admin_company_detail.html', **context)  

@app.route('/manage-company', methods=['GET'])  ##working on this now
def admin_manage_company():
    company_detail = filter_companies(request.args.get('Name'), request.args.get('minCityNumber'),\
                                        request.args.get('maxCityNumber'), request.args.get('minTheaterNumber'),\
                                        request.args.get('maxTheaterNumber'), request.args.get('minEmployee'),\
                                        request.args.get('maxEmployee'))
    companies = get_companies()
    context = {
        'company_detail': company_detail,
        'companies': companies,
    }
    return render_template('admin_manage_company.html', **context)

@app.route('/manager-filter-theater', method=['GET'])
def manager_filter_theater():
    username = g.user['username']
    mov_name = request.args.get('movie', '')
    min_duration = request.args.get('min_duration', None)
    max_duration = request.args.get('max_duration', None)
    min_release = request.args.get('min_release', None)
    max_release = request.args.get('max_release', None)
    min_play = request.args.get('min_play', None)
    max_play = request.args.get('max_play', None)
    include = request.args.get('include', None)
    result = fetch_proc('manager_filter_th', (username,
    mov_name,
    min_duration,
    max_duration,
    min_release,
    max_release,
    min_play,
    max_play,
    include))
    context = {
        'result': result,
        'movies': get_movies(),
    }
    return render_template('theaterOverview.html', **context)