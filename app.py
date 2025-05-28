from flask import Flask, send_from_directory, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os
from werkzeug.utils import secure_filename
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'forms.db')

app = Flask(__name__, static_folder='static', template_folder='public')
CORS(app)  # Ενεργοποίηση CORS για όλα τα endpoints

# Φάκελος για αποθήκευση αρχείων
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Μέγιστο μέγεθος upload 16MB

# Επιτρεπόμενες επεκτάσεις αρχείων
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}

# Dummy χρήστες για login
users = {
    "student1": "password123",
    "student2": "mypassword",
    "dssec": "secpassword",
}

# Προφίλ φοιτητών με βασικά στοιχεία
student_profiles = {
    "12345678": {
        "stud_name": "ΚΩΝΣΤΑΝΤΙΝΟΣ",
        "stud_surname": "ΠΑΠΑΔΟΠΟΥΛΟΣ",
        "stud_fname": "ΧΡΗΣΤΟΣ"
    },
    "87654321": {
        "stud_name": "ΕΛΕΑΝΝΑ",
        "stud_surname": "ΠΑΠΑΓΕΩΡΓΙΟΥ",
        "stud_fname": "ΚΥΡΙΑΚΟΣ"
    }
}


# Σύνδεση με βάση δεδομένων
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Αρχικοποίηση βάσης δεδομένων
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
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
        department TEXT,
        sxolh TEXT,
        university TEXT,
        supervisor TEXT,
        current_date TEXT,
        start_date TEXT,
        rep TEXT,
        org TEXT,
        addr TEXT,
        job_desc TEXT,
        upeuthunos TEXT,
        pos TEXT,
        contact TEXT,
        email TEXT,
        date TEXT,
        repr_name TEXT,
        repr_job TEXT,
        birthdate TEXT,
        birthplace TEXT,
        idnumber TEXT,
        ad_number TEXT,
        FAX TEXT,
        anal_vathm_path TEXT,
        vevaiwsi_apodoxis_path TEXT,
        up_dilwsh_path TEXT,
        vevaiwsi_apodoxis_html TEXT,
        up_dilwsh_html TEXT,
        status TEXT DEFAULT 'Pending', 
        secretary_comments TEXT,
        submission_date TEXT
    )''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Έλεγχος αν το αρχείο έχει επιτρεπόμενη επέκταση
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Αποθήκευση αρχείου με μοναδικό όνομα
def save_file(file):
    if file and allowed_file(file.filename):
        # Δημιουργία μοναδικού ονόματος αρχείου
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return file_path
    return ''

@app.route('/')
def index():
    return send_from_directory('public', 'login.html')

# Στατικά αρχεία
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('public', filename)

# Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    student_id = data.get('studentId')

    if username in users and users[username] == password:
        user_role = "secretary" if username.startswith("dssec") else "student"

        if user_role == "student":
            if not student_id:
                return jsonify({"success": False, "error": "Λείπει ο ΑΜ"}), 400

            # Έλεγχος αντιστοίχισης username <-> ΑΜ
            correct_id = None
            if username == "student1":
                correct_id = "12345678"
            elif username == "student2":
                correct_id = "87654321"

            if student_id != correct_id:
                return jsonify({"success": False, "error": "Ο ΑΜ δεν αντιστοιχεί στον χρήστη"}), 403

            # Πάρε τα στοιχεία φοιτητή από τα profiles
            profile = student_profiles.get(student_id, {})
            print("Login profile data:", profile)  # Για έλεγχο στη κονσόλα


            return jsonify({
                "success": True,
                "role": user_role,
                "student_id": student_id,
                "stud_name": profile.get("stud_name", ""),
                "stud_surname": profile.get("stud_surname", ""),
                "stud_fname": profile.get("stud_fname", "")
            })

        return jsonify({"success": True, "role": user_role})

    return jsonify({"success": False, "error": "Λανθασμένα στοιχεία σύνδεσης"}), 401



# Υποβολή Φόρμας
@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        print("Form data received:", request.form)

        # Λήψη δεδομένων από τη φόρμα
        form_data = request.form
        
        # Αρχικοποίηση για τα πεδία που θα εισαχθούν στη βάση
        data = {}
        
        # Μεταφορά όλων των πεδίων φόρμας στο dictionary
        for key in form_data:
            data[key] = form_data[key]
        
        # Διόρθωση των ονομάτων κλειδιών που έχουν παύλα
        if 'current_date' in data:
            data['current_date'] = data.pop('current_date')
        if 'start_date' in data:
            data['start_date'] = data.pop('start_date')
        
        # Επεξεργασία και αποθήκευση αρχείων
        files = request.files
        
        # Αποθήκευση αρχείων αν υπάρχουν
        if 'anal_vathm' in files:
            data['anal_vathm_path'] = save_file(files['anal_vathm'])
        
        if 'up_dilwsh_file' in files:
            data['up_dilwsh_path'] = save_file(files['up_dilwsh_file'])
        
        if 'vevaiwsi_apodoxis_file' in files:
            data['vevaiwsi_apodoxis_path'] = save_file(files['vevaiwsi_apodoxis_file'])
        
        # Προσθήκη τρέχουσας ημερομηνίας υποβολής
        data['submission_date'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Δημιουργία SQL ερωτήματος για εισαγωγή δεδομένων
        fields = list(data.keys())
        values = list(data.values())
        placeholders = ', '.join(['?' for _ in fields])
        
        # Σύνδεση με βάση δεδομένων και εισαγωγή δεδομένων
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"""
            INSERT INTO students ({', '.join(fields)})
            VALUES ({placeholders})
        """
        
        cursor.execute(query, values)
        conn.commit()
        
        # Λήψη του ID της εγγραφής που μόλις εισήχθη
        application_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "success": True, 
            "message": "Η υποβολή ήταν επιτυχής! Ευχαριστούμε!",
            "application_id": application_id
        }), 200
        
    except Exception as e:
        print(f"Error in submit_form: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# Λήψη όλων των αιτήσεων
@app.route('/applications', methods=['GET'])
def get_applications():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, stud_surname, stud_name, stud_id, emp_name, submission_date, status, secretary_comments, current_date
            FROM students
            ORDER BY submission_date DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        applications = []
        for row in rows:
            applications.append({
                'id': row['id'],
                'stud_surname': row['stud_surname'],
                'stud_name': row['stud_name'],
                'stud_id': row['stud_id'],
                'emp_name': row['emp_name'],
                'submission_date': row['submission_date'],
                'status': row['status'],
                'secretary_comments': row['secretary_comments'],
                'current_date': row['current_date']
            })
        
        return jsonify({"success": True, "applications": applications})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Λήψη συγκεκριμένης αίτησης
@app.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students WHERE id = ?', (application_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"success": False, "error": "Η αίτηση δεν βρέθηκε"}), 404
        
        # Μετατροπή του αποτελέσματος σε dictionary
        application = {}
        for key in row.keys():
            application[key] = row[key]
        
        return jsonify({"success": True, "application": application})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Ενημέρωση κατάστασης αίτησης
@app.route('/applications/<int:application_id>', methods=['PUT'])
def update_application_status(application_id):
    try:
        data = request.json
        status = data.get('status')
        comments = data.get('secretary_comments', '')
        
        if not status:
            return jsonify({"success": False, "error": "Δεν δόθηκε κατάσταση"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE students SET status = ?, secretary_comments = ? WHERE id = ?',
            (status, comments, application_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Η κατάσταση της αίτησης ενημερώθηκε με επιτυχία"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    

# Εκτέλεση της εφαρμογής
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)