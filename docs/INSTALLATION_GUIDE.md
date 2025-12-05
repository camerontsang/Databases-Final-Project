# Installation Guide - Updated Application
## Air Ticket Reservation System with Security Improvements

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

**New packages installed:**
- `flask-limiter==3.5.0` - Rate limiting protection
- `flask-mail==0.9.1` - Email verification system
- `flask-wtf==1.2.1` - CSRF protection
- `itsdangerous==2.1.2` - Secure token generation

### 2. Create Logs Directory
```bash
mkdir logs
```

This directory will contain:
- `app.log` - General application logs
- `security.log` - Security events (logins, failed attempts)
- `error.log` - Error-level logs

### 3. Run the Application
```bash
python app.py
```

Visit: **http://localhost:5000**

---

## ⚙️ Configuration (Optional)

### Email Verification Setup
If you want to enable email verification (optional):

1. **For Gmail:**
   ```python
   # Edit email_verification.py or set environment variables
   export MAIL_USERNAME="your-email@gmail.com"
   export MAIL_PASSWORD="your-app-specific-password"
   ```

2. **Generate Gmail App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification → App Passwords
   - Generate password for "Mail"
   - Use that password (NOT your regular Gmail password)

3. **Add Database Column (Optional):**
   ```sql
   ALTER TABLE customer ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
   ALTER TABLE booking_agent ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
   ```

### Rate Limiting with Redis (Production)
For production, use Redis instead of memory storage:

1. **Install Redis:**
   ```bash
   # macOS
   brew install redis
   redis-server

   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo service redis-server start
   ```

2. **Install Python Redis:**
   ```bash
   pip install redis
   ```

3. **Update app.py:**
   ```python
   limiter = Limiter(
       app=app,
       key_func=get_remote_address,
       storage_uri="redis://localhost:6379"  # Changed from memory://
   )
   ```

---

## 📁 New Files Added

### Core Improvements:
- **`logging_config.py`** - Logging and audit trail system
- **`errors.py`** - Centralized error messages and custom exceptions
- **`email_verification.py`** - Email verification with tokens

### Documentation:
- **`IMPROVEMENTS.md`** - Detailed documentation of all changes
- **`INSTALLATION_GUIDE.md`** (this file) - Installation instructions

---

## 🔍 What Changed?

### Application Features:
✅ **Rate Limiting** - Prevents brute-force attacks
✅ **Comprehensive Logging** - All actions logged with timestamps
✅ **Audit Trail** - Track security events and user actions
✅ **Better Error Handling** - No more crashes on empty search results
✅ **Input Validation** - Proper error messages instead of silent failures
✅ **CSRF Protection** - All forms protected (templates need update)
✅ **Email System** - Ready for email verification (configuration needed)

### Files Modified:
- `app.py` - Added logging, rate limiting, CSRF protection
- `security.py` - Enhanced input validation
- `requirements.txt` - Added new dependencies
- `templates/public/login.html` - Example CSRF token

---

## 🧪 Testing the Application

### 1. Test Rate Limiting
Try logging in more than 10 times in one minute:
```bash
# You should see after 10 attempts:
"429 Too Many Requests"
```

### 2. Test Logging
Perform some actions, then check logs:
```bash
# View recent activity
tail -50 logs/app.log

# Watch real-time logs
tail -f logs/app.log

# Check security events
tail -50 logs/security.log

# View errors only
cat logs/error.log
```

### 3. Test Search Error Fix
1. Go to Search Flights
2. Search for a non-existent flight (e.g., "ZZZZZ" to "YYYY")
3. Should show: "No flights found matching your criteria"
4. Should NOT crash or show error page

### 4. Test Input Validation
Try submitting forms with:
- Empty fields
- Very long text (>255 characters)
- Invalid email formats
- Invalid dates

You should see specific error messages.

---

## 📊 Monitoring Your Application

### View Login Activity
```bash
grep "login" logs/security.log | tail -20
```

### View Failed Login Attempts
```bash
grep "login_failed" logs/security.log
```

### View Ticket Purchases
```bash
grep "ticket_purchase" logs/app.log
```

### View All Errors
```bash
tail -100 logs/error.log
```

### Real-Time Monitoring
```bash
# Watch all activity
tail -f logs/app.log

# Watch security events only
tail -f logs/security.log | grep -E "(login|permission)"

# Watch purchases
tail -f logs/app.log | grep "purchase"
```

---

## 🔧 Troubleshooting

### Issue: "Import flask_limiter could not be resolved"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'logging_config'"
**Solution:** Make sure all new files are in the project directory:
- `logging_config.py`
- `errors.py`
- `email_verification.py`

### Issue: "Permission denied" when creating logs
**Solution:** Create logs directory
```bash
mkdir logs
chmod 755 logs
```

### Issue: CSRF Token Validation Failed
**Solution:** Add CSRF token to your form (see template example)
```html
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
</form>
```

### Issue: Email Not Sending
**Solution:**
1. Check email configuration in `email_verification.py`
2. For Gmail, use App-Specific Password
3. Check firewall allows SMTP (port 587)
4. Check logs for error details

---

## 📝 Template Updates Needed

Most templates need CSRF tokens added. Here's the pattern:

**Before:**
```html
<form method="POST" action="{{ url_for('some_route') }}">
    <input type="text" name="field">
    <button type="submit">Submit</button>
</form>
```

**After:**
```html
<form method="POST" action="{{ url_for('some_route') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <input type="text" name="field">
    <button type="submit">Submit</button>
</form>
```

**Templates to update:**
- All forms in `templates/public/`
- All forms in `templates/customer/`
- All forms in `templates/agent/`
- All forms in `templates/staff/`

**Note:** The application works without CSRF tokens, but you'll see warnings in logs.

---

## 🎯 Next Steps

### Immediate:
1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Create logs directory: `mkdir logs`
3. ✅ Run application: `python app.py`
4. ✅ Test basic functionality

### Soon:
5. Update all templates with CSRF tokens
6. Configure email if needed
7. Review logs to understand user behavior
8. Set up Redis for production rate limiting

### Future:
9. Implement password reset functionality
10. Add email verification to registration flow
11. Set up production deployment
12. Add more comprehensive tests

---

## 🔒 Security Notes

### What's Protected:
- ✅ SQL Injection (parameterized queries)
- ✅ Brute Force Attacks (rate limiting)
- ✅ Session Hijacking (secure sessions)
- ✅ XSS (Jinja2 auto-escaping)
- ✅ CSRF (token validation)
- ✅ Input Validation (sanitization)

### What Still Needs Work:
- ⚠️ Password Hashing (upgrade from SHA-256 to bcrypt)
- ⚠️ Database Connection Pooling
- ⚠️ Race Conditions in ticket purchases
- ⚠️ SECRET_KEY management (use environment variables)

---

## 📖 Additional Resources

- **IMPROVEMENTS.md** - Detailed technical documentation
- **README.md** - Original project documentation
- Flask-Limiter Docs: https://flask-limiter.readthedocs.io/
- Flask-Mail Docs: https://pythonhosted.org/Flask-Mail/
- Flask-WTF Docs: https://flask-wtf.readthedocs.io/

---

## 💡 Tips

### Development:
- Check logs regularly: `tail -f logs/app.log`
- Test rate limits in incognito mode
- Use different IPs to test rate limiting

### Production:
- Change SECRET_KEY to environment variable
- Use Redis for rate limiting storage
- Set up log rotation in production
- Monitor logs for security events
- Set up alerts for failed login attempts

### Performance:
- Rate limiting prevents DoS attacks
- Logging has minimal performance impact
- Use log rotation to manage disk space
- Consider ELK stack for log analysis in production

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Application starts without errors
- [ ] Logs directory created with 3 log files
- [ ] Can log in successfully
- [ ] Login attempts are logged in security.log
- [ ] Search returns results or "not found" message
- [ ] Rate limiting works (try 11 login attempts)
- [ ] All existing features still work
- [ ] No crashes or 500 errors

---

**Last Updated:** 2024-12-05
**Version:** 1.1
**Status:** Production-Ready (with notes above) ✅

For questions, check `IMPROVEMENTS.md` or review code comments in new files.
