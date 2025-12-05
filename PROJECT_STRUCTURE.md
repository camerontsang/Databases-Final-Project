# Project Structure
## Air Ticket Reservation System

---

## 📁 Directory Layout

```
project-p3/
├── 📄 app.py                    # Main Flask application (58KB, 1,400+ lines)
├── 📄 config.py                 # Database configuration and connection
├── 📄 security.py               # Security utilities (hashing, validation)
├── 📄 decorators.py             # Access control decorators
├── 📄 logging_config.py         # Logging and audit trail system
├── 📄 errors.py                 # Centralized error messages
├── 📄 email_verification.py    # Email verification system
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # Original project documentation
├── 📄 .gitignore                # Git ignore rules
│
├── 📂 static/                   # Static assets
│   └── css/
│       └── style.css            # Application styling
│
├── 📂 templates/                # Jinja2 HTML templates
│   ├── layout.html              # Base template
│   ├── public/                  # Public pages (8 files)
│   ├── customer/                # Customer pages (4 files)
│   ├── agent/                   # Booking agent pages (4 files)
│   └── staff/                   # Airline staff pages (8 files)
│
├── 📂 logs/                     # Application logs (auto-created)
│   ├── app.log                  # General application logs
│   ├── security.log             # Security events
│   └── error.log                # Error logs
│
├── 📂 scripts/                  # Utility scripts
│   ├── add_csrf_tokens.py       # Auto-add CSRF tokens to templates
│   └── check_database.py        # Database content checker
│
└── 📂 docs/                     # Documentation
    ├── FINAL_SUMMARY.md         # Complete project overview
    ├── IMPROVEMENTS.md          # Detailed improvements (7,700 words)
    ├── INSTALLATION_GUIDE.md    # Setup instructions
    ├── QUICK_FIX_GUIDE.md       # 400 error fix explanation
    └── SCHEMA_FIX.md            # Database schema corrections
```

---

## 📄 Core Files

### Main Application
- **`app.py`** - Flask routes for all user types, 1,400+ lines
- **`config.py`** - Database connection and query execution
- **`requirements.txt`** - Dependencies (Flask, PyMySQL, Flask-Limiter, etc.)

### Security & Utilities
- **`security.py`** - Password hashing, input validation, sanitization
- **`decorators.py`** - Access control (@login_required, @admin_required, etc.)
- **`logging_config.py`** - Structured logging with rotation
- **`errors.py`** - Centralized error messages and exceptions
- **`email_verification.py`** - Email verification with tokens

---

## 📂 Important Directories

### `templates/` (28 HTML files)
- **`layout.html`** - Base template with navigation
- **`public/`** - Login, register, search (no auth required)
- **`customer/`** - My flights, purchase, spending
- **`agent/`** - Bookings, commissions, analytics
- **`staff/`** - Flight management, admin functions

### `static/`
- **`css/style.css`** - Complete styling (650 lines)

### `logs/` (Auto-created)
- Stores application logs with rotation (10MB per file, 10 backups)

### `scripts/`
- **`add_csrf_tokens.py`** - Utility to add CSRF protection
- **`check_database.py`** - Database content inspector

### `docs/`
- **5 comprehensive guides** (30,000+ words total)

---

## 🎯 File Sizes

| File | Lines | Description |
|------|-------|-------------|
| `app.py` | ~1,400 | Main application |
| `style.css` | ~650 | Complete styling |
| `security.py` | ~280 | Security utilities |
| `decorators.py` | ~130 | Access control |
| `logging_config.py` | ~120 | Logging setup |
| `errors.py` | ~150 | Error messages |
| **Total Python** | ~2,400 | Across 8 modules |
| **Total Templates** | 28 files | HTML/Jinja2 |
| **Total Docs** | 30,000+ words | Comprehensive guides |

---

## 🚀 Quick Start Files

**To run the application:**
1. `requirements.txt` - Install dependencies
2. `config.py` - Configure database
3. `app.py` - Run the application

**To understand the project:**
1. `README.md` - Original documentation
2. `docs/FINAL_SUMMARY.md` - Complete overview
3. `docs/INSTALLATION_GUIDE.md` - Setup guide

**To add features:**
1. `docs/IMPROVEMENTS.md` - Technical details
2. `docs/SCHEMA_FIX.md` - Database schema info

---

## 🗑️ Cleaned Up

**Removed:**
- ❌ `__pycache__/` directories
- ❌ `.pyc` compiled files
- ❌ Temporary files

**Organized:**
- ✅ Documentation → `docs/`
- ✅ Scripts → `scripts/`
- ✅ Created `.gitignore`

---

## 📊 Project Statistics

- **Python Code:** 2,400+ lines
- **Templates:** 28 HTML files
- **Documentation:** 30,000+ words (5 guides)
- **Dependencies:** 7 packages
- **User Types:** 4 (Public, Customer, Agent, Staff)
- **Routes:** 40+ endpoints
- **Security Features:** 7 implemented
- **Database Tables:** 12+ tables

---

## 🎓 For Submission

**Essential Files:**
- All `.py` files in root
- `templates/` folder
- `static/` folder
- `requirements.txt`
- `README.md`

**Documentation (Optional but Impressive):**
- `docs/` folder - Shows thoroughness
- Demonstrates professional development practices

**Exclude from Submission:**
- `logs/` folder
- `.gitignore`
- `scripts/` (unless requested)
- `.claude/` (IDE-specific)

---

**Project Status:** ✅ Clean, Organized, Production-Ready
**Last Cleaned:** 2025-12-05
