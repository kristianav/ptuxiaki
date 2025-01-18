from flask import Flask, send_from_directory, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os


app = Flask(__name__, static_folder='public')
CORS(app)  # Ενεργοποίηση CORS για όλα τα endpoints

@app.route('/')
def home():
    return send_from_directory('public', 'login.html')

# Φάκελος για αποθήκευση αρχείων
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dummy χρήστες για login
users = {
    "student1": "password123",
    "student2": "mypassword",
}

# Σύνδεση με βάση δεδομένων
def get_db_connection():
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row
    return conn

# Αρχικοποίηση βάσης δεδομένων
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stud_surname TEXT NOT NULL,
            stud_name TEXT NOT NULL,
            stud_fname TEXT,
            stud_mname TEXT,
            stud_id TEXT NOT NULL,
            stud_afm TEXT,
            stud_sem INTEGER,
            stud_address TEXT,
            stud_city TEXT,
            stud_zipcode TEXT,
            stud_tel TEXT,
            stud_email TEXT,
            emp_name TEXT,
            emp_addr TEXT,
            emp_phone TEXT,
            emp_email TEXT,
            emp_sup TEXT,
            org TEXT,
            repr TEXT,
            addr TEXT,
            job_desc TEXT,
            upeuthunos TEXT,
            pos TEXT,
            contact TEXT,
            email TEXT,
            date TEXT,
            repr_name TEXT,
            repr_job TEXT,
            fathername TEXT,
            mothername TEXT,
            birthdate TEXT,
            birthplace TEXT,
            idnumber TEXT,
            phone TEXT,
            city TEXT,
            address TEXT,
            number TEXT,
            postal_code TEXT,
            fax TEXT,
            anal_vathm_path TEXT,
            vevaiwsi_apodoxis_path TEXT,
            up_dilwsh_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

#static files
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)
# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username] == password:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

# Φόρμα φοιτητή (HTML)
@app.route('/form')
def student_form():
    return render_template("form.html")

# Υποβολή Φόρμας
@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Λήψη δεδομένων από τη φόρμα
        student_data = request.form

        # Λήψη και αποθήκευση αρχείων
        files = {}
        for field in ["anal_vathm", "vevaiwsi_apodoxis", "up_dilwsh"]:
            file = request.files.get(field)
            if file:
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)  # Αποθήκευση του αρχείου
                files[field] = filename  # Αποθήκευση διαδρομής

        # Εισαγωγή δεδομένων στη βάση
        query = '''
            INSERT INTO students (
                stud_surname, stud_name, stud_fname, stud_mname, stud_id, stud_afm, 
                stud_sem, stud_address, stud_city, stud_zipcode, stud_tel, stud_email, 
                emp_name, emp_addr, emp_phone, emp_email, emp_sup, org, repr, addr, 
                job_desc, upeuthunos, pos, contact, email, date, repr_name, repr_job, 
                fathername, mothername, birthdate, birthplace, idnumber, phone, 
                city, address, number, postal_code, fax, 
                anal_vathm_path, vevaiwsi_apodoxis_path, up_dilwsh_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            student_data['stud_surname'], student_data['stud_name'], student_data.get('stud_fname'), 
            student_data.get('stud_mname'), student_data['stud_id'], student_data.get('stud_afm'), 
            student_data.get('stud_sem'), student_data.get('stud_address'), student_data.get('stud_city'), 
            student_data.get('stud_zipcode'), student_data.get('stud_tel'), student_data.get('stud_email'), 
            student_data.get('emp_name'), student_data.get('emp_addr'), student_data.get('emp_phone'), 
            student_data.get('emp_email'), student_data.get('emp_sup'), student_data.get('org'), 
            student_data.get('repr'), student_data.get('addr'), student_data.get('job_desc'), 
            student_data.get('upeuthunos'), student_data.get('pos'), student_data.get('contact'), 
            student_data.get('email'), student_data.get('date'), student_data.get('repr_name'), 
            student_data.get('repr_job'), student_data.get('fathername'), student_data.get('mothername'), 
            student_data.get('birthdate'), student_data.get('birthplace'), student_data.get('idnumber'), 
            student_data.get('phone'), student_data.get('city'), student_data.get('address'), 
            student_data.get('number'), student_data.get('postal_code'), student_data.get('fax'), 
            files.get('anal_vathm'), files.get('vevaiwsi_apodoxis'), files.get('up_dilwsh')
        ))
        conn.commit()
        conn.close()

        return "Η υποβολή ήταν επιτυχής! Ευχαριστούμε!"
    except Exception as e:
        return f"Υπήρξε ένα σφάλμα: {str(e)}", 500

# Λήψη όλων των φοιτητών
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=True)
