# SmartPlacement – Campus Placement Intelligence & Eligibility System

SmartPlacement is a self-contained, 100% API-free web application developed for college placement departments. It processes student profiles, matches them against visiting company criteria locally using a normalized MySQL database, and provides transparent eligibility, skill gap, and recommendation reports.

---

## Technical Stack & Architecture

- **Backend:** Python 3.10+ & Flask Framework
- **Database:** MySQL 8.0+ (3rd Normal Form Schema)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS), Bootstrap 5
- **Authentication:** Flask Session-based Auth with `pbkdf2:sha256` Password Hashing
- **API Dependency:** **0% (100% Self-Contained Local Execution)**

---

## Directory Layout

```
smartplacement/
│
├── app.py                     # Main Flask Application Entry Point
├── config.py                  # Database & Session Configuration
├── requirements.txt           # Python Dependencies
│
├── database/                  # MySQL Relational Database Scripts
│   ├── schema.sql             # 3NF DDL Table Schema Creation
│   └── sample_data.sql        # Seed Data for Testing & Demonstration
│
├── routes/                    # Flask Blueprint Routes
│   ├── auth.py                # Student & Admin Authentication
│   ├── student.py             # Profile Management & Dashboard
│   ├── company.py             # Placement Drives & Specifications
│   ├── admin.py               # Placement Cell Admin Tools & CSV Export
│   └── placement.py           # Eligibility, Recommendations & Skill Gap
│
├── services/                  # Core Algorithmic Business Logic
│   ├── db.py                  # MySQL Connection Pool & Parameterized Queries
│   ├── eligibility.py         # Rule-Based Eligibility Engine
│   ├── skill_gap.py           # Skill Gap Analyzer
│   ├── recommendation.py      # Rule-Based Candidate Matching Engine
│   └── readiness.py           # 0-100 Placement Readiness Score Calculator
│
├── templates/                 # Responsive HTML5 Templates (Bootstrap 5)
├── static/                    # CSS & JS Static Assets
└── tests/                     # Unit Test Suite
```

---

## Quick Setup Instructions

### 1. Database Setup (MySQL)
Open MySQL Workbench or MySQL Command Line Client:

```sql
SOURCE path/to/smartplacement/database/schema.sql;
SOURCE path/to/smartplacement/database/sample_data.sql;
```

### 2. Environment Configuration
Copy or update your database settings in `config.py` or `.env`:
```python
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = 'your_mysql_password'
DB_NAME = 'smartplacement_db'
```

### 3. Install Dependencies & Launch Application
```bash
cd smartplacement
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run Unit Tests
python -m unittest discover -s tests

# Launch Local Flask Development Server
python app.py
```

Open browser at: `http://localhost:5000`

---

## Default Login Credentials (Seed Data)

- **Placement Officer (Admin):**
  - **Email:** `admin@college.edu`
  - **Password:** `admin123`

- **Student Account:**
  - Create a new student account via the `/register` route.

---

## College Website Integration

No API integration is needed. Add a hyperlink on the existing main college website navbar:
```html
<a href="http://placement.college.edu" target="_blank" class="nav-link">Placement Portal</a>
```
