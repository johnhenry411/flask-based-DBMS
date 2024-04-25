import logging
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import io
import pandas as pd
from flask_session import Session
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'just a secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/path/to/session/files'

Session(app)

db = SQLAlchemy(app)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


def create_database():
    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS birds_data (bird_id INTEGER PRIMARY KEY,bird_name text, owner_name text, owner_id INTEGER, owner_location text, owner_phone_no integer, bird_sex text, bird_age text)")
    conn.commit()
    conn.close()

def create_database():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT UNIQUE, password TEXT)")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    else:
        username = session['username']
        return render_template('index.html', username=username)


@app.route('/login', methods=['GET', 'POST'])
def login():

    login_status = None  
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        logger.debug(f'Login form submitted with email: {email}')

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['username'] = user.username
            flash('Login successful!', 'login_success')  # Flash success message with 'success' category
            logger.info(f'User {user.username} logged in successfully')
            # After successful login, redirect to main page
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

@app.route('/add', methods=['POST'])
def add_item():
    bird_id = request.form['bird_id']
    bird_name = request.form['bird_name']
    owner_name = request.form['owner_name']
    owner_id = request.form['owner_id']
    owner_location = request.form['owner_location']
    owner_phone_no = request.form['owner_phone_no']
    bird_sex = request.form['bird_sex']
    bird_age = request.form['bird_age']

    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO birds_data VALUES (?,?,?,?,?,?,?,?)", (bird_id, bird_name, owner_name, owner_id, owner_location, owner_phone_no, bird_sex, bird_age))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Item added successfully'})

@app.route('/get_data')

@app.route('/get_data')
def get_data():
    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM birds_data")
    rows = cur.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'bird_id': row[0],
            'bird_name': row[1],
            'owner_name': row[2],
            'owner_id': row[3],
            'owner_location': row[4],
            'owner_phone_no': row[5],
            'bird_sex': row[6],
            'bird_age': row[7]
        })

    return jsonify(data)
@app.route('/update', methods=['POST'])
def update_item():
    bird_id = request.form['bird_id']
    bird_name = request.form['bird_name']
    owner_name = request.form['owner_name']
    owner_id = request.form['owner_id']
    owner_location = request.form['owner_location']
    owner_phone_no = request.form['owner_phone_no']
    bird_sex = request.form['bird_sex']
    bird_age = request.form['bird_age']

    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("UPDATE birds_data SET bird_name=?, owner_name=?, owner_id=?, owner_location=?, owner_phone_no=?, bird_sex=?, bird_age=? WHERE bird_id=?", (bird_name, owner_name, owner_id, owner_location, owner_phone_no, bird_sex, bird_age, bird_id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Item updated successfully'})


@app.route('/delete', methods=['POST'])
def delete_item():
    bird_id = request.form['bird_id']

    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM birds_data WHERE bird_id=?", (bird_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Item deleted successfully'})

@app.route('/user_del/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users'))

@app.route('/logs')
def logs():
    with open('app.log', 'r') as f:
        logs = f.readlines()
    parsed_logs = []
    for log in logs:
        log_parts = log.strip().split(' ')
        log_dict = {
            'timestamp': log_parts[0] + ' ' + log_parts[1],
            'level': log_parts[2],
            'message': ' '.join(log_parts[3:])
        }
        parsed_logs.append(log_dict)
    return jsonify(parsed_logs)


@app.route('/search', methods=['POST'])
def search_item():
    search_text = request.form['search_text']

    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM birds_data WHERE bird_id LIKE? OR bird_name LIKE? OR owner_name LIKE? OR owner_id LIKE? OR owner_location LIKE? OR owner_phone_no LIKE? OR bird_sex LIKE? OR bird_age LIKE?", ("%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%", "%" + search_text + "%"))
    rows = cur.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            'bird_id': row[0],
            'bird_name': row[1],
            'owner_name': row[2],
            'owner_id': row[3],
            'owner_location': row[4],
            'owner_phone_no': row[5],
            'bird_sex': row[6],
            'bird_age': row[7]
        })

    return jsonify(data)


@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/export_csv')
def export_csv():
    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM birds_data")
    rows = cur.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=['bird_id', 'bird_name', 'owner_name', 'owner_id', 'owner_location', 'owner_phone_no', 'bird_sex', 'bird_age'])

    # Use a StringIO object as a buffer to avoid the need for an intermediate file
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    # Set the appropriate headers for the response
    response = app.response_class(
        csv_buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-disposition': 'attachment; filename=parrot_data.csv'}
    )

    return response

@app.route('/export_pdf')
def export_pdf():
    response = io.BytesIO()
    pdf = CsvtoPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Endangered Parrot DB Management Interface", ln=True, align="C")
    pdf.ln(10)

    # Fetch data from the database
    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM birds_data")
    rows = cur.fetchall()
    conn.close()

    # Write the header row
    pdf.cell(20, 10, txt="ID", border=1)
    pdf.cell(50, 10, txt="Name", border=1)
    pdf.cell(50, 10, txt="Owner Name", border=1)
    pdf.cell(30, 10, txt="ID", border=1)
    pdf.cell(50, 10, txt="Location", border=1)
    pdf.cell(30, 10, txt="Phone", border=1)
    pdf.cell(30, 10, txt="Sex", border=1)
    pdf.cell(30, 10, txt="Age", border=1)
    pdf.ln()

    # Write the data rows
    for row in rows:
        pdf.cell(20, 10, txt=str(row[0]), border=1)
        pdf.cell(50, 10, txt=row[1], border=1)
        pdf.cell(50, 10, txt=row[2], border=1)
        pdf.cell(30, 10, txt=str(row[3]), border=1)
        pdf.cell(50, 10, txt=row[4], border=1)
        pdf.cell(30, 10, txt=str(row[5]), border=1)
        pdf.cell(30, 10, txt=row[6], border=1)
        pdf.cell(30, 10, txt=row[7], border=1)
        pdf.ln()

    pdf.output(response)
    response.seek(0)

    return send_file(response, attachment_filename='parrot_data.pdf', as_attachment=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    create_database()
    app.run(host='0.0.0.0', debug=True)
