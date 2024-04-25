import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just a secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
    logger.debug('Redirecting to login page')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_status = None  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        logger.debug(f'Login instance created by email: {email}')

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['username'] = user.username
            flash('Login successful!', 'login_success')  
            logger.info(f'User {user.username} logged in successfully')
            return redirect(url_for('main'))
        else:
            login_status = 'Invalid email or password. Please try again.'
            flash(login_status, 'login_error')
            logger.warning('Invalid email or password entered')
    return render_template('main.html', login_status=login_status, signup_status=None)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    logger.debug('Signup route accessed')
    signup_status = None  
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        logger.debug(f'Signup form submitted with email: {email}')

        if password!= confirm_password:
            signup_status = 'Passwords do not match. Please try again.'
            flash(signup_status, 'signup_error')  
            logger.warning('Passwords do not match')
        elif User.query.filter_by(email=email).first():
            signup_status = 'Email already exists. Please choose a different one.'
            flash(signup_status, 'signup_error')  
            logger.warning('Email already exists')
        elif not email.endswith('@gmail.com'):
            signup_status = 'invalid email address!'
            flash(signup_status, 'signup_error')  
            logger.warning('inavid email attemp!')
        else:
            new_user = User(email=email, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! You can now log in.', 'signup_success')  
            logger.info(f'New user {username} signed up successfully')
            return redirect(url_for('login'))
    return render_template('main.html', login_status=None, signup_status=signup_status)


@app.route('/main')
def main():
    logger.debug('Main route accessed')
    if 'username' in session:
        username = session['username']
        logger.debug(f'Rendering main page for user {username}')
        return render_template('index.html', username=username)
    else:
        flash('You need to log in first.', 'error')
        logger.warning('User attempted to access main page without logging in')
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)
