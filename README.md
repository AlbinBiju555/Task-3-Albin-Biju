# Task-3-Albin-Biju

#  Vaccination Tracker — Database Configuration & Connectivity Manual

This technical documentation details the relational database connection layer, configuration mappings, and transactional design patterns implemented within the backend control file (`app.py`).

---

##  Technology Stack Requirements

* **Database Management System:** MySQL Server (v8.0+ recommended)
* **Application Platform Environment:** Python 3.x
* **Database Driver Intermediary:** `flask_mysqldb`
* **Data Exchange Standard:** JSON format for API payload transmissions

---

##  Connection Architecture & Configuration Mappings

The backend engine initializes thread-safe connectivity to the MySQL database engine via native Flask object context keys. All relational interaction processes utilize parameterized execution loops to decouple the underlying database code execution from client-side input string data.

```python
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# --- RELATIONAL STORAGE ENVIRONMENT MAPPINGS ---
app.config['MYSQL_HOST'] = 'localhost'       # Database server network location
app.config['MYSQL_USER'] = 'root'            # Administrative access privilege user
app.config['MYSQL_PASSWORD'] = 'root'        # Access authorization credential key
app.config['MYSQL_DB'] = 'vacc_tracker'      # Targeted operational workspace schema

# Instantiate the global MySQL gateway attachment object
mysql = MySQL(app)
