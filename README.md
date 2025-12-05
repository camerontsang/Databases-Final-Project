# Air Ticket Reservation System
## CSCI-SHU 213 - Project Part 3

A Flask-based web application for airline ticket reservations with four user types:
- **Public Users**: Search flights, check status, register/login
- **Customers**: View/purchase tickets, track spending with charts
- **Booking Agents**: Book for customers, view commission analytics
- **Airline Staff**: Manage flights, view analytics, admin functions

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- XAMPP with MySQL/MariaDB running
- Your Part 2 database schema already imported

### 2. Setup Database

Make sure your database `air_ticket_system` exists with all tables from Part 2.

Update `config.py` with your database credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Your MySQL password
    'database': 'airline_portal',  # Your database name
    ...
}
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## 📁 Project Structure

```
air_ticket_system/
├── app.py              # Main Flask application with all routes
├── config.py           # Database configuration
├── security.py         # Password hashing & input validation
├── decorators.py       # Access control decorators
├── requirements.txt    # Python dependencies
├── static/
│   └── css/
│       └── style.css   # All styling
└── templates/
    ├── layout.html     # Base template
    ├── public/         # Public pages (login, register, search)
    ├── customer/       # Customer pages
    ├── agent/          # Booking agent pages
    └── staff/          # Airline staff pages
```

---

## 🔐 Security Features

1. **Password Hashing**: SHA-256 (upgrade to bcrypt for production)
2. **SQL Injection Prevention**: Parameterized queries only
3. **Session-based Authentication**: Flask secure sessions
4. **Role-based Access Control**: Decorators for each user type
5. **Input Validation**: Server-side validation for all inputs
6. **XSS Protection**: Jinja2 auto-escaping

---

## 👤 User Types & Features

### Public (No Login)
- Search flights by city/airport/date
- Check flight status

### Customer
- View upcoming flights
- Search and purchase tickets
- View flight history with filters
- Spending analytics with bar charts

### Booking Agent
- Book flights for customers
- View all bookings
- Commission analytics
- Top customer charts

### Airline Staff
- View flights (next 30 days default)
- View passenger lists
- Customer flight lookup
- **Admin**: Add airports, airplanes, flights, authorize agents
- **Operator**: Update flight status
- Analytics dashboard with charts

---

## 📊 Charts (Chart.js)

The application includes interactive charts:
- Customer spending (bar chart)
- Agent top customers (horizontal bar)
- Staff ticket sales (line chart)
- Staff destinations (doughnut charts)
- Staff delay statistics (bar chart)

---

## 🧪 Testing Accounts

Create test accounts via the registration pages, or insert directly:

```sql
-- Customer (password: test123)
INSERT INTO customer (email, name, password) 
VALUES ('customer@test.com', 'Test Customer', 
        '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');

-- Booking Agent (password: test123)
INSERT INTO booking_agent (email, password)
VALUES ('agent@test.com', 
        '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');

-- Staff (password: test123)
INSERT INTO airline_staff (username, password, first_name, last_name, airline_name)
VALUES ('staffuser', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
        'Test', 'Staff', 'Your Airline Name');

-- Give staff Admin + Operator permissions
INSERT INTO permission (username, permission_type) VALUES ('staffuser', 'Admin');
INSERT INTO permission (username, permission_type) VALUES ('staffuser', 'Operator');
```

---

## ⚠️ Important Notes

1. **Change SECRET_KEY** in `config.py` before deployment
2. **Test SQL injection** by trying `'; DROP TABLE --` in inputs
3. All routes use **prepared statements** - never string concatenation
4. Session data is stored securely via Flask's signed cookies

---

## 📝 Deliverables Checklist

- [x] Source code (this folder)
- [x] Feature-to-query mapping (see routes in app.py)
- [ ] File manifest (list all files submitted)
- [ ] Contribution summary (if pair work)

---

## 🛠️ Troubleshooting

**Can't connect to database?**
- Check XAMPP MySQL is running
- Verify credentials in config.py
- Make sure database exists

**Import errors?**
- Run: `pip install -r requirements.txt`

**Templates not found?**
- Make sure templates/ folder structure is correct

**Charts not showing?**
- Check browser console for JavaScript errors
- Chart.js loads from CDN (needs internet)

---

Good luck with your project! 🎓
