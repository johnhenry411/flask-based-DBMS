from flask import Flask, render_template, request, jsonify, session
import sqlite3
import csv
import os
import io
import pandas as pd

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('parrot.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS birds_data (bird_id INTEGER PRIMARY KEY,bird_name text, owner_name text, owner_id INTEGER, owner_location text, owner_phone_no integer, bird_sex text, bird_age text)")
    conn.commit()
    conn.close()

user_conn = sqlite3.connect('users.db')
user_cur = user_conn.cursor()
user_conn.close()

@app.route('/')
def index():
    username = session.get('username')

    return render_template('index.html', username=username)


    
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
    create_database()
    app.run(debug=True)