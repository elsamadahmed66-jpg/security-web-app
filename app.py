# اضف هذا الملف إلى security-web-app/app.py
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات التطبيق
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# أمان الكوكيز
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# إنشاء قاعدة البيانات
@app.cli.command('init-db')
def init_db():
    db.create_all()
    print('Database initialized.')
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# أنشئ الجداول تلقائياً إذا لم تكن موجودة
with app.app_context():
    db.create_all()
# بيانات تسجيل الدخول الثابتة
def check_credentials(username, password):
    return username == "admin" and password == "123456"

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('dashboard'))

        flash('اسم مستخدم أو كلمة مرور خاطئة', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    records = Record.query.order_by(Record.created_at.desc()).all()
    return render_template('dashboard.html', records=records)

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('العنوان والمحتوى مطلوبان', 'warning')
            return redirect(url_for('add_record'))

        r = Record(title=title, content=content)
        db.session.add(r)
        db.session.commit()

        flash('تم إضافة السجل', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_record.html')

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
