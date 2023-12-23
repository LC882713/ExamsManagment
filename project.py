import os
from flask import request, redirect, url_for, flash,abort
from flask import Flask, render_template, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from init import Users, engine
from flask_bcrypt import Bcrypt
from datetime import timedelta
from init import *
from forms import *
from professors_route import professor_bp
from students_route import student_bp
from functools import wraps



app = Flask( __name__ )

#per criptare password
bcrypt=Bcrypt(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

engine=create_engine('postgresql://postgres:admin@localhost:5432/ProgettoBasiDati23', echo = True)
#engine=create_engine('postgresql://postgres:postgres@localhost:5432/ProgettoBasi', echo = True)

app.config ['SECRET_KEY'] = 'admin'
login_manager = LoginManager()
login_manager.init_app(app)

#creazione della sessione
Session = sessionmaker(bind=engine)
session = Session()


app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)


app.register_blueprint(professor_bp, url_prefix='/professor')
app.register_blueprint(student_bp, url_prefix='/student')


class User(UserMixin):
    def __init__(self, id, name, surname, email, pwd,  gender, role):
        self.id=id
        self.name=name
        self.surname=surname
        self.email=email
        self.pwd=pwd
        self.gender=gender
        self.role=role

def get_user_by_email(email): 
    conn=engine.connect()
    rs=session.query(Users).filter(Users.email==email)
    user=rs.first()
    conn.close()
    if user is None:
        return None  
    return User(user.id, user.name, user.surname, user.email, user.password, user.gender, user.role)      

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                flash("You don't have the privilege to access this section")
                abort(403)  
        return wrapper
    return decorator
  
@login_manager.user_loader
def load_user(user_id):
    conn=engine.connect()
    rs=session.query(Users).filter(Users.id==user_id)
    user=rs.first()
    conn.close()
    if user is None:
        return None
    return User(user.id, user.name, user.surname, user.email, user.password, user.gender, user.role)

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    return render_template('500.html'), 500


@app.route('/')
def index():
    if current_user.is_authenticated:
        if(current_user.role=='professor'):                 
            return redirect(url_for('professorMenu'))
        else:
            return redirect(url_for('studentMenu'))
    return render_template("homepage.html")

@app.route('/setup_favicon')
def setup_favicon():
    app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))
    return 'Favicon setup complete'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = session.query(Users).filter(Users.email == email).first()

        if user is not None and user.password is not None and bcrypt.check_password_hash(user.password, password):
            user = get_user_by_email(email)
            login_user(user, remember=form.remember.data)

            if user.role == 'professor':
                return redirect(url_for('professorMenu'))
            else:
                return redirect(url_for('studentMenu'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            return render_template("login.html", form=form)
    else:
        flash('Error, form not validated.', 'error')
        return render_template("login.html", form=form)


@app.route('/professorMenu')
@login_required
@role_required('professor')
def professorMenu():
    return render_template("professorMenu.html")   

@app.route('/studentMenu')
@login_required
@role_required('student')
def studentMenu():
    return render_template("studentMenu.html")  

@app.route('/information')
@login_required
def users_information():
    return render_template('students_information.html', )

#------------------------------------------------------------------------------

@app.route('/logout')
@login_required
def logout():
    logout_user() # chiamata a Flask - Login
    flash('You have been logged out', category='info')
    return redirect('/')

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method=='POST':
        if form.validate():
            name = form.firstName.data
            surname = form.lastName.data
            email = form.email.data
            password = form.password.data
            role = form.role.data
            gender = form.gender.data
            
            #controlla se esiste già un utente con questa email
            user_exist=session.query(Users).filter_by(email=email).first()
           
            if user_exist:
                flash("email already exist, use a different one")
                return redirect(url_for('signup'))
            
            new_user=Users(email=email, role=role, name=name, surname=surname, gender=gender, password=bcrypt.generate_password_hash(password).decode('utf-8'))
            session.add(new_user)  #aggiunge l'utente al database
            session.commit()  #conferma le modifiche

            flash('User registered successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

 
if __name__ == '__main__':
    app.run()