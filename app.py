from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vacc_tracker'

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('vacc_html.html')

@app.route('/dashboard')
def dashboard():
    return render_template('vacc_html2.html')

@app.route('/records')
def records():
    return render_template('vacc_record.html')

@app.route('/addrecord')
def addrecord():
    return render_template('vacc_addrec.html')

@app.route('/schedule')
def schedule():
    return render_template('vacc_schedule.html')

@app.route('/bookings')
def bookings():
    return render_template('vacc_book.html')

@app.route('/updaterecord')
def updaterecord():
    return render_template('vacc_update.html')

@app.route('/logout')
def logout():
    return render_template('vacc_html.html')

@app.route('/register')
def register_page():
    return render_template('vacc_register.html')

@app.route('/nurse/dashboard')
def nurse_dashboard():
    return render_template('vacc_nursehtml.html')

@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email', '').strip().lower()
    password = data.get('password')

    user_role = "nurse" if email.startswith('nur') else "patient"

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", [email])
        existing_user = cur.fetchone()
        
        if existing_user:
            cur.close()
            return jsonify({"message": "Email is already registered"}), 400

        cur.execute("INSERT INTO users(username, email, password, role) VALUES (%s, %s, %s, %s)", (username, email, password, user_role))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Registration Successful"})
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

@app.route('/api/login', methods=['POST', 'GET'])
def login_api():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password')

    cur = mysql.connection.cursor()
    
    cur.execute("SELECT password, role, username, id FROM users WHERE email = %s", [email])
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if password == user[0]:
        return jsonify({
            "message": "Login Successful",
            "role": user[1],
            "username": user[2],
            "user_id": user[3]
        })
    else:
        return jsonify({"message": "Incorrect password"}), 401

@app.route('/api/booking', methods=['POST'])
def booking():
    data = request.get_json()
    user_id = data.get('user_id')
    vaccine_name = data.get('vaccine_name')
    vaccine_centre = data.get('vaccine_centre')
    booking_date = data.get('booking_date')

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO appointments(patient_id, vaccine_name, vaccine_centre, booking_date) VALUES (%s, %s, %s, %s)",
        (user_id, vaccine_name, vaccine_centre, booking_date)
    )
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Booking Successful"})


@app.route('/api/get_bookings', methods=['GET'])
def get_bookings():
   
    user_id = request.args.get('user_id')
    cur = mysql.connection.cursor()
    
    if user_id:
        
        cur.execute("""
            SELECT a.vaccine_name, a.vaccine_centre, a.booking_date, a.patient_id 
            FROM appointments a 
            WHERE a.patient_id = %s AND a.booking_date >= CURDATE() 
            ORDER BY a.booking_date ASC
        """, [user_id])
    else:
        
        cur.execute("""
            SELECT a.vaccine_name, a.vaccine_centre, a.booking_date, a.patient_id 
            FROM appointments a 
            WHERE a.booking_date >= CURDATE() 
            ORDER BY a.booking_date ASC
        """)
        
    rows = cur.fetchall()
    cur.close()

    bookings_list = []
    for row in rows:
        bookings_list.append({
            "vaccine_name": row[0],
            "vaccine_centre": row[1],
            "booking_date": str(row[2]),
            "user_id": row[3]
        })
    return jsonify({"data": bookings_list})
@app.route('/api/addrecord', methods=['POST'])
def add_record():
    data = request.get_json()
    patient_id = data.get('patient_id')
    input_name = data.get('patient_name', '').strip()
    vaccine_name = data.get('vaccine_name')
    vaccination_date = data.get('vaccination_date')
    dose_number = data.get('dose_number')
    status = data.get('status', 'Completed')
    administered_by = data.get('administered_by')
    remarks = data.get('remarks')

    cur = mysql.connection.cursor()
    
   
    cur.execute("SELECT username, role FROM users WHERE id = %s", [patient_id])
    user = cur.fetchone()
    
    if not user:
        cur.close()
        return jsonify({"message": f"User ID #{patient_id} does not exist in the system."}), 404
        
    registered_name = user[0]
    user_role = user[1]
    
    
    if user_role == 'nurse':
        cur.close()
        return jsonify({"message": f"User ID #{patient_id} belongs to a Nurse. Records can only be added for Patients."}), 400

   
    if input_name.lower() != registered_name.lower():
        cur.close()
        return jsonify({
            "message": f"Identity Mismatch! User ID #{patient_id} is strictly registered to '{registered_name}'. You entered '{input_name}'."
        }), 400

   
    cur.execute(
        "INSERT INTO records(patient_id, patient_name, vaccine_name, vaccination_date, dose_number, status, administered_by, remarks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (patient_id, registered_name, vaccine_name, vaccination_date, dose_number, status, administered_by, remarks)
    )
    mysql.connection.commit()
    cur.close()
    
    return jsonify({"message": "Record Added Successfully"})

@app.route('/api/records', methods=['GET'])

def get_records():
    
    user_id = request.args.get('user_id')
    cur = mysql.connection.cursor()
    
    if user_id:
        
        cur.execute("SELECT patient_id, patient_name, vaccine_name, vaccination_date, dose_number, status, administered_by, remarks FROM records WHERE patient_id = %s ORDER BY vaccination_date DESC", [user_id])
    else:
        
        cur.execute("SELECT patient_id, patient_name, vaccine_name, vaccination_date, dose_number, status, administered_by, remarks FROM records ORDER BY vaccination_date DESC")
        
    rows = cur.fetchall()
    cur.close()

    records_list = []
    for row in rows:
        records_list.append({
            "user_id": row[0],
            "patient_name": row[1],
            "vaccine_name": row[2],
            "vaccination_date": str(row[3]),
            "dose_number": row[4],
            "status": row[5],
            "administered_by": row[6],
            "remarks": row[7]
        })
    return jsonify({"data": records_list})

@app.route('/api/get_record_by_patient/<int:patient_id>', methods=['GET'])
def get_record_by_patient(patient_id):
    cur = mysql.connection.cursor()
   
    cur.execute("SELECT id, patient_id, patient_name, vaccine_name, vaccination_date, dose_number, administered_by, remarks FROM records WHERE patient_id = %s ORDER BY id DESC LIMIT 1", [patient_id])
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"message": "No vaccination record exists yet for this User ID. Please add an initial record first."}), 404

    record_data = {
        "id": row[0],
        "patient_id": row[1],
        "patient_name": row[2],
        "vaccine_name": row[3],
        "vaccination_date": str(row[4]),
        "dose_number": row[5],
        "administered_by": row[6],
        "remarks": row[7]
    }
    return jsonify({"data": record_data})
    



@app.route('/api/updaterecord/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.get_json()
    patient_name = data.get('patient_name')
    vaccine_name = data.get('vaccine_name')
    vaccination_date = data.get('vaccination_date')
    dose_number = data.get('dose_number')
    administered_by = data.get('administered_by')
    remarks = data.get('remarks')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE records 
        SET patient_name = %s, vaccine_name = %s, vaccination_date = %s, dose_number = %s, administered_by = %s, remarks = %s 
        WHERE id = %s
    """, (patient_name, vaccine_name, vaccination_date, dose_number, administered_by, remarks, record_id))
    
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Vaccination Record Updated Successfully!"})

if __name__ == '__main__':
    app.run(debug=True)