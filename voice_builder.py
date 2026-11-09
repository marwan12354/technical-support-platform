# voice_builder.py (النسخة النهائية - Lovable + Voice UI)
import os
import subprocess
import sys
import threading
import webbrowser
import time

TARGET_DIR = r"C:\Users\PC\Downloads\مشروع منصة الدعم التقني\itsupport\ghg"

# ==========================================
# 1. كود قاعدة البيانات (models.py)
# ==========================================
MODELS_CODE = """from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expenses = db.relationship('Expense', backref='department', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50), default='fa-folder')

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    expense_number = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    item = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    approval_status = db.Column(db.String(50), default='بانتظار الاعتماد')
    payment_status = db.Column(db.String(50), default='غير مدفوع')
    remaining_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
"""

# ==========================================
# 2. كود تعبئة البيانات (database.py)
# ==========================================
DATABASE_CODE = """from models import db, Department, Category, Expense

def init_database(app):
    with app.app_context():
        db.drop_all() # حذف الجداول القديمة لتجنب أخطاء الهيكل
        db.create_all()
        
        if Department.query.count() == 0:
            db.session.add_all([
                Department(name='الإدارة المالية'),
                Department(name='الموارد البشرية'),
                Department(name='تقنية المعلومات'),
                Department(name='المشتريات')
            ])
            
        if Category.query.count() == 0:
            db.session.add_all([
                Category(name='مستلزمات مكتبية', icon='fa-boxes-stacked'),
                Category(name='صيانة', icon='fa-screwdriver-wrench'),
                Category(name='طباعة', icon='fa-print'),
                Category(name='خدمات', icon='fa-network-wired'),
                Category(name='سفر وانتقال', icon='fa-plane')
            ])
        
        if Expense.query.count() == 0:
            dept = Department.query.filter_by(name='الإدارة المالية').first()
            db.session.add_all([
                Expense(expense_number='EX-0064', date='29/10/2026', item='مستلزمات مكتبية', department_id=dept.id, amount=1200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0063', date='28/10/2026', item='صيانة', department_id=dept.id, amount=800.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0062', date='27/10/2026', item='طباعة', department_id=dept.id, amount=450.0, approval_status='بانتظار الاعتماد', payment_status='غير مدفوع', remaining_amount=0.0),
                Expense(expense_number='EX-0061', date='25/10/2026', item='خدمات', department_id=dept.id, amount=4000.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1100.0),
            ])
            
        db.session.commit()
        print("[DB] ✅ تم تهيئة قاعدة البيانات بنجاح!")
"""

# ==========================================
# 3. كود الخادم (app.py)
# ==========================================
APP_CODE = """import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Expense, Department, Category
from database import init_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.context_processor
def inject_globals():
    return dict(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

def get_stats():
    expenses = Expense.query.all()
    stats = {"total_approved": 0, "total_paid": 0, "total_remaining": 0, "pending_approval": 0, "overdue": 4}
    for e in expenses:
        if e.approval_status == 'معتمد':
            stats['total_approved'] += e.amount
            stats['total_paid'] += (e.amount - e.remaining_amount)
            stats['total_remaining'] += e.remaining_amount
        if e.approval_status == 'بانتظار الاعتماد':
            stats['pending_approval'] += 1
    return stats

@app.route('/')
def dashboard():
    expenses = Expense.query.order_by(Expense.id.desc()).all()
    return render_template('dashboard.html', expenses=expenses, stats=get_stats(), active_page='home')

@app.route('/expenses')
def expenses_page():
    expenses = Expense.query.order_by(Expense.id.desc()).all()
    departments = Department.query.all()
    categories = Category.query.all()
    return render_template('expenses.html', expenses=expenses, departments=departments, categories=categories, stats=get_stats(), active_page='expenses')

@app.route('/data')
def data_page():
    departments = Department.query.all()
    return render_template('data.html', departments=departments, stats=get_stats(), active_page='data')

@app.route('/approvals')
def approvals_page():
    pending = Expense.query.filter_by(approval_status='بانتظار الاعتماد').all()
    return render_template('approvals.html', pending=pending, stats=get_stats(), active_page='approvals')

@app.route('/categories')
def categories_page():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories, stats=get_stats(), active_page='categories')

@app.route('/reports')
def reports_page():
    return render_template('reports.html', stats=get_stats(), active_page='reports')

@app.route('/settings')
def settings_page():
    return render_template('settings.html', stats=get_stats(), active_page='settings')

@app.route('/help')
def help_page():
    return render_template('help.html', stats=get_stats(), active_page='help')

@app.route('/add', methods=['POST'])
def add_expense():
    item = request.form.get('item')
    dept_id = int(request.form.get('department_id'))
    amount = float(request.form.get('amount'))
    app_status = request.form.get('approval_status')
    pay_status = request.form.get('payment_status')
    
    last_exp = Expense.query.order_by(Expense.id.desc()).first()
    next_num = int(last_exp.expense_number.split('-')[1]) + 1 if last_exp else 1
    exp_num = f"EX-{str(next_num).zfill(4)}"
    remaining = 0.0 if pay_status == "مدفوع" else amount
    
    new_exp = Expense(
        expense_number=exp_num, date=datetime.now().strftime("%d/%m/%Y"),
        item=item, department_id=dept_id, amount=amount,
        approval_status=app_status, payment_status=pay_status, remaining_amount=remaining
    )
    
    try:
        db.session.add(new_exp)
        db.session.commit()
        flash('تم إضافة المصروف بنجاح، عمل رائع!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ، يرجى المحاولة مرة أخرى.', 'error')
    return redirect(url_for('expenses_page'))

@app.route('/approve/<int:id>')
def approve(id):
    exp = Expense.query.get(id)
    if exp:
        exp.approval_status = 'معتمد'
        db.session.commit()
        flash('تم اعتماد المصروف بنجاح!', 'success')
    return redirect(url_for('approvals_page'))

if __name__ == '__main__':
    init_database(app)
    print("🚀 المنصة تعمل الآن على: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False, port=5000)
"""

# ==========================================
# 4. ملفات الواجهة (Templates) - تصميم Lovable + Audio
# ==========================================
BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl" x-data="{ sidebarOpen: false, modalOpen: false, isMuted: false }">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة المصروفات - Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = { theme: { extend: { fontFamily: { sans: ['Cairo', 'sans-serif'] }, colors: { brand: '#ea580c', dark: '#0f172a', surface: '#f8fafc' } } } }
    </script>
    <style>
        body { font-family: 'Cairo', sans-serif; background: #f1f5f9; }
        [x-cloak] { display: none !important; }
        
        /* Lovable Animations */
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in-up { animation: fadeInUp 0.6s ease-out forwards; }
        .animate-delay-1 { animation-delay: 0.1s; }
        .animate-delay-2 { animation-delay: 0.2s; }
        
        /* Glassmorphism */
        .glass-card { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.4); }
        .glass-sidebar { background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); }
        
        .nav-link { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .nav-link:hover { background: rgba(255,255,255,0.08); transform: translateX(-4px); }
        .nav-active { background: linear-gradient(90deg, #ea580c 0%, #c2410c 100%); color: white; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.4); border-radius: 12px; }
        
        .badge { padding: 0.35rem 0.8rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px; }
        .badge-green { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .badge-yellow { background: #fef08a; color: #854d0e; border: 1px solid #fde047; }
        .badge-blue { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
        .badge-red { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    </style>
    <script>
        // الدوال الصوتية
        function speak(text) {
            if ('speechSynthesis' in window && !window.isMuted) {
                window.speechSynthesis.cancel(); // إلغاء أي كلام سابق
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'ar-SA';
                utterance.rate = 1.0;
                utterance.pitch = 1.1; // نبرة ودودة
                window.speechSynthesis.speak(utterance);
            }
        }

        // مؤثرات صوتية (بدون ملفات خارجية)
        function playSound(type) {
            if (window.isMuted) return;
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                
                if (type === 'success') {
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
                    oscillator.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.1); // A6
                } else if (type === 'error') {
                    oscillator.type = 'square';
                    oscillator.frequency.setValueAtTime(300, audioCtx.currentTime);
                }
                
                gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                
                oscillator.start();
                oscillator.stop(audioCtx.currentTime + 0.3);
            } catch (e) { console.log('Audio disabled'); }
        }

        // مراقبة الرسائل المنبثقة لتشغيل الصوت
        document.addEventListener('DOMContentLoaded', () => {
            const flashMessages = document.querySelectorAll('.flash-message');
            if (flashMessages.length > 0) {
                const msg = flashMessages[0].getAttribute('data-msg');
                const type = flashMessages[0].getAttribute('data-type');
                playSound(type === 'success' ? 'success' : 'error');
                speak(msg);
            }
        });
    </script>
</head>
<body class="flex h-screen overflow-hidden text-gray-800" x-data="{ isMuted: false }" @mute-changed.window="window.isMuted = $event.detail">
    <div x-show="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black/50 z-20 lg:hidden backdrop-blur-sm" x-cloak></div>
    
    <!-- Sidebar -->
    <aside :class="sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'" class="fixed lg:relative w-[280px] h-full glass-sidebar text-gray-300 flex flex-col shrink-0 shadow-2xl z-30 transform transition-transform duration-300 ease-in-out border-l border-gray-700/50">
        <div class="p-8 flex flex-col items-center border-b border-gray-700/50">
            <div class="bg-gradient-to-br from-brand to-orange-400 p-4 rounded-2xl mb-4 shadow-lg shadow-brand/30">
                <i class="fa-solid fa-file-invoice-dollar text-4xl text-white"></i>
            </div>
            <h1 class="text-white font-extrabold text-xl text-center leading-tight">المصروفات<br><span class="text-brand text-sm tracking-widest">التشغيلية</span></h1>
        </div>
        <nav class="flex-1 py-6 space-y-2 px-4 text-sm font-bold overflow-y-auto">
            <a href="/" class="{% if active_page == 'home' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-house w-6 text-center text-lg"></i> الرئيسية</a>
            <a href="/data" class="{% if active_page == 'data' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-database w-6 text-center text-lg"></i> إدارة البيانات</a>
            <a href="/expenses" class="{% if active_page == 'expenses' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-file-lines w-6 text-center text-lg"></i> سجل المصروفات</a>
            <a href="/approvals" class="{% if active_page == 'approvals' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-check-double w-6 text-center text-lg"></i> الاعتماد والسداد</a>
            <a href="/categories" class="{% if active_page == 'categories' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-layer-group w-6 text-center text-lg"></i> بنود الصرف</a>
            <a href="/reports" class="{% if active_page == 'reports' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-chart-pie w-6 text-center text-lg"></i> التقارير</a>
            <div class="border-t border-gray-700/50 my-2 pt-2"></div>
            <a href="/settings" class="{% if active_page == 'settings' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-gear w-6 text-center text-lg"></i> الإعدادات</a>
            <a href="/help" class="{% if active_page == 'help' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3.5 rounded-xl"><i class="fa-solid fa-book-open w-6 text-center text-lg"></i> دليل الاستخدام</a>
        </nav>
    </aside>
    
    <!-- Main Content -->
    <main class="flex-1 flex flex-col h-full overflow-hidden relative w-full bg-surface">
        <header class="glass-card px-8 py-5 flex justify-between items-center border-b border-gray-200/50 sticky top-0 z-10">
            <div class="flex items-center gap-4">
                <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden text-gray-600 hover:text-brand transition"><i class="fa-solid fa-bars text-2xl"></i></button>
                <div>
                    <h2 class="text-2xl font-extrabold text-gray-800">{% block title %}{% endblock %}</h2>
                    <p class="text-sm text-gray-500 font-semibold mt-1">نظرة عامة | {{ now }}</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                {% block header_actions %}{% endblock %}
                
                <!-- زر كتم الصوت -->
                <button @click="isMuted = !isMuted; $dispatch('mute-changed', isMuted)" class="w-10 h-10 rounded-full bg-white border border-gray-200 text-gray-600 hover:text-brand hover:border-brand flex items-center justify-center transition shadow-sm">
                    <i class="fa-solid" :class="isMuted ? 'fa-volume-xmark text-red-500' : 'fa-volume-high text-green-500'"></i>
                </button>
                
                <div class="w-11 h-11 rounded-full bg-gradient-to-br from-brand to-orange-600 text-white flex items-center justify-center font-extrabold shadow-lg shadow-brand/30 border-2 border-white cursor-pointer hover:scale-105 transition">م</div>
            </div>
        </header>

        <!-- Toast Notifications (تتفاعل مع الصوت) -->
        <div class="absolute top-24 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4" x-data="{ show: true }" x-show="show" x-init="setTimeout(() => show = false, 5000)" x-cloak>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="flash-message mb-2 p-4 rounded-2xl shadow-xl flex items-center justify-between font-bold text-sm animate-fade-in-up {{ 'bg-green-50 text-green-800 border border-green-200' if category == 'success' else 'bg-red-50 text-red-800 border border-red-200' }}" data-msg="{{ message }}" data-type="{{ category }}">
                            <span><i class="fa-solid {{ 'fa-check-circle' if category == 'success' else 'fa-exclamation-triangle' }} ml-2 text-lg"></i> {{ message }}</span>
                            <button @click="show = false" class="text-gray-400 hover:text-gray-800"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>

        <div class="p-8 overflow-y-auto h-full">
            {% block content %}{% endblock %}
        </div>
    </main>
</body>
</html>
"""

DASHBOARD_HTML = """
{% extends "base.html" %}
{% block title %}لوحة القيادة{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-fade-in-up">
    <!-- KPI 1 -->
    <div class="glass-card rounded-3xl p-6 shadow-xl hover:-translate-y-2 transition duration-300 border-r-4 border-brand">
        <div class="flex justify-between items-start mb-4">
            <div class="w-12 h-12 rounded-2xl bg-orange-100 text-brand flex items-center justify-center text-2xl"><i class="fa-solid fa-user-clock"></i></div>
            <span class="text-green-500 font-bold text-sm bg-green-50 px-2 py-1 rounded-lg">نشط</span>
        </div>
        <p class="text-gray-500 font-bold text-sm mb-1">بانتظار الاعتماد</p>
        <h3 class="text-4xl font-extrabold text-gray-800">{{ stats.pending_approval }}</h3>
    </div>
    <!-- KPI 2 -->
    <div class="glass-card rounded-3xl p-6 shadow-xl hover:-translate-y-2 transition duration-300 border-r-4 border-red-500">
        <div class="flex justify-between items-start mb-4">
            <div class="w-12 h-12 rounded-2xl bg-red-100 text-red-500 flex items-center justify-center text-2xl"><i class="fa-solid fa-calendar-xmark"></i></div>
            <span class="text-red-500 font-bold text-sm bg-red-50 px-2 py-1 rounded-lg">تنبيه</span>
        </div>
        <p class="text-gray-500 font-bold text-sm mb-1">متأخرة في السداد</p>
        <h3 class="text-4xl font-extrabold text-gray-800">{{ stats.overdue }}</h3>
    </div>
    <!-- KPI 3 -->
    <div class="bg-gradient-to-br from-[#1e293b] to-[#0f172a] text-white rounded-3xl p-6 shadow-xl hover:-translate-y-2 transition duration-300 relative overflow-hidden">
        <div class="absolute -left-10 -bottom-10 opacity-10 text-9xl"><i class="fa-solid fa-sack-dollar"></i></div>
        <p class="text-gray-400 font-bold text-sm mb-1 relative z-10">المتبقي</p>
        <h3 class="text-3xl font-extrabold text-white relative z-10">{{ "{:,.0f}".format(stats.total_remaining) }} <span class="text-sm text-gray-400">ر.س</span></h3>
    </div>
    <!-- KPI 4 -->
    <div class="bg-gradient-to-br from-brand to-orange-600 text-white rounded-3xl p-6 shadow-xl hover:-translate-y-2 transition duration-300 relative overflow-hidden">
        <div class="absolute -left-10 -bottom-10 opacity-10 text-9xl"><i class="fa-solid fa-hand-holding-dollar"></i></div>
        <p class="text-orange-100 font-bold text-sm mb-1 relative z-10">المدفوع</p>
        <h3 class="text-3xl font-extrabold text-white relative z-10">{{ "{:,.0f}".format(stats.total_paid) }} <span class="text-sm text-orange-200">ر.س</span></h3>
    </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up animate-delay-2">
    <div class="lg:col-span-2 glass-card p-8 rounded-3xl shadow-xl border border-white/50">
        <div class="flex justify-between items-center mb-6">
            <h3 class="font-extrabold text-xl text-gray-800"><i class="fa-solid fa-chart-line text-brand ml-2"></i> الأداء المالي</h3>
        </div>
        <div class="h-72"><canvas id="dashChart"></canvas></div>
    </div>
    
    <div class="space-y-6">
        <!-- بطاقة التحفيز الصوتي -->
        <div class="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden cursor-pointer group" onclick="speak('أنت تبلي بلاءً حسناً! استمر في تنظيم مصروفاتك لتحقيق أهدافك المالية.')">
            <i class="fa-solid fa-quote-right absolute -bottom-4 -left-4 text-8xl opacity-20 group-hover:scale-110 transition"></i>
            <h3 class="font-bold text-lg mb-2 relative z-10">رسالة تحفيزية <i class="fa-solid fa-volume-high text-sm ml-1"></i></h3>
            <p class="text-sm text-purple-100 font-semibold relative z-10">"التنظيم المالي هو الخطوة الأولى نحو الحرية المالية. أنت في الطريق الصحيح!"</p>
            <p class="text-xs text-purple-200 mt-4 relative z-10">انقر للاستماع <i class="fa-solid fa-arrow-left"></i></p>
        </div>

        <div class="glass-card p-6 rounded-3xl shadow-xl border border-white/50">
            <h3 class="font-extrabold text-lg text-gray-800 mb-4"><i class="fa-solid fa-clock-rotate-left text-brand ml-2"></i> أحدث العمليات</h3>
            <div class="space-y-3">
                {% for exp in expenses[:4] %}
                <div class="flex justify-between items-center p-3 bg-white/60 rounded-xl border border-white hover:bg-white transition cursor-pointer">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-full bg-orange-50 flex items-center justify-center text-brand text-xs"><i class="fa-solid fa-receipt"></i></div>
                        <div><p class="font-bold text-gray-800 text-xs">{{ exp.item }}</p><p class="text-[10px] text-gray-500">{{ exp.date }}</p></div>
                    </div>
                    <span class="font-extrabold text-gray-700 text-sm">{{ exp.amount }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
<script>
    const ctx = document.getElementById('dashChart').getContext('2d');
    let gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(234, 88, 12, 0.4)');
    gradient.addColorStop(1, 'rgba(234, 88, 12, 0.0)');
    
    new Chart(ctx, {
        type: 'line',
        data: { labels: ['مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر'], datasets: [{ label: 'المصروفات', data: [12000, 19000, 15000, 22000, 18000, 24800], borderColor: '#ea580c', backgroundColor: gradient, borderWidth: 3, fill: true, tension: 0.4, pointBackgroundColor: '#fff', pointBorderColor: '#ea580c', pointBorderWidth: 2, pointRadius: 4 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { borderDash: [5, 5] } }, x: { grid: { display: false } } } }
    });
</script>
{% endblock %}
"""

EXPENSES_HTML = """
{% extends "base.html" %}
{% block title %}سجل المصروفات{% endblock %}
{% block header_actions %}
<button @click="modalOpen = true" class="bg-brand text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-orange-700 shadow-lg shadow-brand/30 transition hover:-translate-y-0.5"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
{% endblock %}
{% block content %}
<div class="glass-card rounded-3xl shadow-xl border border-white/50 overflow-hidden animate-fade-in-up">
    <div class="p-6 border-b border-gray-200/50 flex justify-between items-center bg-white/50">
        <div class="relative w-72">
            <i class="fa-solid fa-magnifying-glass absolute right-4 top-3.5 text-gray-400"></i>
            <input type="text" placeholder="بحث..." class="w-full bg-white border border-gray-200 rounded-xl py-3 pr-11 pl-4 text-sm font-bold focus:outline-none focus:border-brand focus:ring-2 focus:ring-brand/20 transition">
        </div>
        <span class="text-sm font-bold text-gray-500 bg-gray-100 px-4 py-2 rounded-lg">إجمالي السجلات: {{ expenses|length }}</span>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-right text-sm whitespace-nowrap">
            <thead class="bg-gray-50/80 text-gray-500 font-extrabold border-b border-gray-200/50">
                <tr>
                    <th class="py-4 px-6">رقم المصروف</th><th class="py-4 px-6">التاريخ</th><th class="py-4 px-6">البند</th><th class="py-4 px-6">الإدارة</th><th class="py-4 px-6">المبلغ</th><th class="py-4 px-6 text-center">الاعتماد</th><th class="py-4 px-6 text-center">السداد</th><th class="py-4 px-6 text-center">المتبقي</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100/50">
                {% for exp in expenses %}
                <tr class="hover:bg-white/80 transition-colors group">
                    <td class="py-4 px-6 font-extrabold text-brand">{{ exp.expense_number }}</td>
                    <td class="py-4 px-6 text-gray-600 font-semibold">{{ exp.date }}</td>
                    <td class="py-4 px-6 font-bold text-gray-800">{{ exp.item }}</td>
                    <td class="py-4 px-6 text-gray-600">{{ exp.department.name }}</td>
                    <td class="py-4 px-6 font-extrabold text-gray-800">{{ exp.amount }} <span class="text-xs text-gray-400">ر.س</span></td>
                    <td class="py-4 px-6 text-center"><span class="badge {{ 'badge-green' if exp.approval_status == 'معتمد' else 'badge-blue' }}">{{ exp.approval_status }}</span></td>
                    <td class="py-4 px-6 text-center"><span class="badge {{ 'badge-yellow' if exp.payment_status == 'مدفوع جزئياً' else 'badge-red' }}">{{ exp.payment_status }}</span></td>
                    <td class="py-4 px-6 text-center font-extrabold text-gray-800">{{ exp.remaining_amount }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Modal -->
<div x-show="modalOpen" x-cloak class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
    <div @click.away="modalOpen = false" class="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl w-full max-w-lg p-8 border border-white" x-transition:enter="ease-out duration-300" x-transition:enter-start="opacity-0 scale-95" x-transition:enter-end="opacity-100 scale-100">
        <div class="flex justify-between items-center mb-6 border-b pb-4">
            <h3 class="text-2xl font-extrabold text-gray-800">إضافة مصروف</h3>
            <button @click="modalOpen = false" class="text-gray-400 hover:text-red-500 hover:rotate-90 transition"><i class="fa-solid fa-xmark text-2xl"></i></button>
        </div>
        <form action="/add" method="POST" class="space-y-5">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-2">البند</label>
                <select name="item" class="w-full border border-gray-200 p-3 rounded-xl bg-gray-50 focus:bg-white focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none transition font-bold" required>
                    {% for cat in categories %}<option value="{{ cat.name }}">{{ cat.name }}</option>{% endfor %}
                </select>
            </div>
            <div class="grid grid-cols-2 gap-5">
                <div><label class="block text-sm font-bold text-gray-700 mb-2">المبلغ</label><input type="number" name="amount" required class="w-full border border-gray-200 p-3 rounded-xl bg-gray-50 focus:bg-white focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none transition font-bold"></div>
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-2">الإدارة</label>
                    <select name="department_id" class="w-full border border-gray-200 p-3 rounded-xl bg-gray-50 focus:bg-white focus:border-brand focus:ring-2 focus:ring-brand/20 outline-none transition font-bold">
                        {% for dept in departments %}<option value="{{ dept.id }}">{{ dept.name }}</option>{% endfor %}
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-5">
                <div><label class="block text-sm font-bold text-gray-700 mb-2">الاعتماد</label><select name="approval_status" class="w-full border border-gray-200 p-3 rounded-xl bg-gray-50 font-bold"><option value="بانتظار الاعتماد">بانتظار الاعتماد</option><option value="معتمد">معتمد</option></select></div>
                <div><label class="block text-sm font-bold text-gray-700 mb-2">السداد</label><select name="payment_status" class="w-full border border-gray-200 p-3 rounded-xl bg-gray-50 font-bold"><option value="غير مدفوع">غير مدفوع</option><option value="مدفوع">مدفوع</option></select></div>
            </div>
            <button type="submit" class="w-full bg-gradient-to-r from-brand to-orange-600 text-white font-extrabold py-4 rounded-xl hover:from-orange-600 hover:to-brand shadow-lg shadow-brand/30 transition mt-4">حفظ البيانات</button>
        </form>
    </div>
</div>
{% endblock %}
"""

APPROVALS_HTML = """
{% extends "base.html" %}
{% block title %}الاعتماد والسداد{% endblock %}
{% block content %}
<div class="glass-card rounded-3xl shadow-xl border border-white/50 p-8 animate-fade-in-up">
    <h3 class="text-xl font-extrabold text-gray-800 mb-6"><i class="fa-solid fa-clock text-brand ml-2"></i> طلبات بانتظار الاعتماد</h3>
    <div class="space-y-4">
        {% for exp in pending %}
        <div class="flex justify-between items-center bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-full bg-orange-50 text-brand flex items-center justify-center text-xl"><i class="fa-solid fa-file-invoice"></i></div>
                <div>
                    <h4 class="font-extrabold text-gray-800">{{ exp.item }}</h4>
                    <p class="text-sm text-gray-500">{{ exp.expense_number }} | {{ exp.date }}</p>
                </div>
            </div>
            <div class="flex items-center gap-6">
                <span class="font-extrabold text-lg text-gray-800">{{ exp.amount }} ر.س</span>
                <a href="/approve/{{ exp.id }}" class="bg-green-500 text-white px-6 py-2 rounded-xl font-bold hover:bg-green-600 transition shadow-lg shadow-green-500/30"><i class="fa-solid fa-check ml-1"></i> اعتماد</a>
            </div>
        </div>
        {% else %}
        <div class="text-center py-12">
            <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4"><i class="fa-solid fa-check-double text-4xl text-gray-300"></i></div>
            <p class="text-gray-500 font-bold text-lg">لا توجد طلبات معلقة حالياً.</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

CATEGORIES_HTML = """
{% extends "base.html" %}
{% block title %}بنود الصرف{% endblock %}
{% block content %}
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 animate-fade-in-up">
    {% for cat in categories %}
    <div class="glass-card p-8 rounded-3xl shadow-lg border border-white/60 hover:-translate-y-2 hover:shadow-2xl transition duration-300 text-center cursor-pointer group">
        <div class="w-20 h-20 mx-auto bg-gradient-to-br from-orange-50 to-orange-100 text-brand rounded-3xl flex items-center justify-center text-4xl mb-5 group-hover:scale-110 transition duration-300 shadow-inner">
            <i class="fa-solid {{ cat.icon }}"></i>
        </div>
        <h4 class="font-extrabold text-xl text-gray-800">{{ cat.name }}</h4>
        <p class="text-sm text-gray-500 mt-2">عرض التفاصيل</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

DATA_HTML = """
{% extends "base.html" %}
{% block title %}إدارة البيانات{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up">
    <div class="glass-card rounded-3xl shadow-xl p-8 border border-white/50">
        <h3 class="font-extrabold text-xl mb-6 text-gray-800"><i class="fa-solid fa-sitemap text-brand ml-2"></i> الهيكل التنظيمي</h3>
        <div class="space-y-3">
            {% for dept in departments %}
            <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-100">
                <span class="font-bold text-gray-700">{{ dept.name }}</span>
                <span class="badge badge-green">نشط</span>
            </div>
            {% endfor %}
        </div>
    </div>
    <div class="glass-card rounded-3xl shadow-xl p-8 border border-white/50">
        <h3 class="font-extrabold text-xl mb-6 text-gray-800"><i class="fa-solid fa-users text-brand ml-2"></i> المستخدمين</h3>
        <div class="space-y-3">
            <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-100">
                <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-full bg-brand text-white flex items-center justify-center font-bold">م</div><span class="font-bold">مدير النظام</span></div>
                <span class="text-xs font-bold text-gray-400">صلاحيات كاملة</span>
            </div>
            <div class="flex justify-between items-center bg-white p-4 rounded-xl border border-gray-100">
                <div class="flex items-center gap-3"><div class="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">أ</div><span class="font-bold">أحمد (محاسب)</span></div>
                <span class="text-xs font-bold text-gray-400">إدخال بيانات</span>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

REPORTS_HTML = """
{% extends "base.html" %}
{% block title %}التقارير{% endblock %}
{% block content %}
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fade-in-up">
    <div class="glass-card p-8 rounded-3xl shadow-xl border border-white/50">
        <h3 class="font-extrabold text-xl mb-6 text-gray-800">توزيع المصروفات</h3>
        <div class="h-64"><canvas id="pieChart"></canvas></div>
    </div>
    <div class="glass-card p-8 rounded-3xl shadow-xl border border-white/50">
        <h3 class="font-extrabold text-xl mb-6 text-gray-800">المصروفات حسب الإدارة</h3>
        <div class="h-64"><canvas id="barChart"></canvas></div>
    </div>
</div>
<script>
    new Chart(document.getElementById('pieChart'), {
        type: 'doughnut',
        data: { labels: ['مستلزمات', 'صيانة', 'خدمات', 'طباعة'], datasets: [{ data: [30000, 15000, 20000, 10000], backgroundColor: ['#ea580c', '#3b82f6', '#10b981', '#f59e0b'], borderWidth: 0 }] },
        options: { cutout: '70%', plugins: { legend: { position: 'bottom' } } }
    });
    new Chart(document.getElementById('barChart'), {
        type: 'bar',
        data: { labels: ['المالية', 'الموارد', 'تقنية', 'مشتريات'], datasets: [{ label: 'المصروفات', data: [45000, 25000, 30000, 15000], backgroundColor: '#1e293b', borderRadius: 8 }] },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { borderDash: [5, 5] } }, x: { grid: { display: false } } } }
    });
</script>
{% endblock %}
"""

SETTINGS_HTML = """
{% extends "base.html" %}
{% block title %}الإعدادات{% endblock %}
{% block content %}
<div class="glass-card p-8 rounded-3xl shadow-xl border border-white/50 max-w-2xl animate-fade-in-up">
    <h3 class="font-extrabold text-xl mb-6 text-gray-800">الإعدادات العامة</h3>
    <div class="space-y-5">
        <div><label class="block text-sm font-bold text-gray-700 mb-2">اسم الشركة</label><input type="text" value="شركة الدعم التقني" class="w-full border p-3 rounded-xl bg-gray-50 font-bold"></div>
        <div><label class="block text-sm font-bold text-gray-700 mb-2">العملة الافتراضية</label><select class="w-full border p-3 rounded-xl bg-gray-50 font-bold"><option>ريال سعودي (SAR)</option><option>دولار (USD)</option></select></div>
        <div class="flex items-center gap-3 bg-gray-50 p-4 rounded-xl border border-gray-100">
            <input type="checkbox" checked class="w-5 h-5 accent-brand cursor-pointer">
            <label class="font-bold text-gray-700 cursor-pointer">تفعيل الإشعارات الصوتية</label>
        </div>
        <button class="bg-brand text-white px-8 py-3 rounded-xl font-extrabold hover:bg-orange-700 shadow-lg shadow-brand/30 transition" onclick="speak('تم حفظ الإعدادات بنجاح')">حفظ التعديلات</button>
    </div>
</div>
{% endblock %}
"""

HELP_HTML = """
{% extends "base.html" %}
{% block title %}دليل الاستخدام{% endblock %}
{% block content %}
<div class="glass-card p-8 rounded-3xl shadow-xl border border-white/50 max-w-3xl animate-fade-in-up">
    <h3 class="font-extrabold text-2xl mb-6 text-gray-800">مرحباً بك في دليل الاستخدام</h3>
    <div class="space-y-6">
        <div class="flex gap-4">
            <div class="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-bold shrink-0">1</div>
            <div><h4 class="font-bold text-lg text-gray-800 mb-1">إضافة مصروف</h4><p class="text-gray-600">اذهب إلى "سجل المصروفات" واضغط على زر "مصروف جديد"، ثم املأ البيانات واضغط حفظ. ستسمع صوتاً تأكيدياً.</p></div>
        </div>
        <div class="flex gap-4">
            <div class="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-bold shrink-0">2</div>
            <div><h4 class="font-bold text-lg text-gray-800 mb-1">الاعتماد</h4><p class="text-gray-600">في قسم "الاعتماد والسداد" يمكنك مراجعة الطلبات المعلقة والموافقة عليها بضغطة زر.</p></div>
        </div>
        <div class="flex gap-4">
            <div class="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-bold shrink-0">3</div>
            <div><h4 class="font-bold text-lg text-gray-800 mb-1">التحكم بالصوت</h4><p class="text-gray-600">استخدم أيقونة مكبر الصوت في الأعلى لكتم أو تشغيل الأصوات في أي وقت.</p></div>
        </div>
    </div>
</div>
{% endblock %}
"""

# ==========================================
# 5. دالة البناء والتشغيل
# ==========================================
def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

def build_project():
    db_file = os.path.join(TARGET_DIR, "expenses.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        print("🗑️ تم حذف قاعدة البيانات القديمة لتحديث الهيكل.")

    if not os.path.exists(TARGET_DIR): os.makedirs(TARGET_DIR)
    templates_dir = os.path.join(TARGET_DIR, "templates")
    if not os.path.exists(templates_dir): os.makedirs(templates_dir)

    py_files = {
        "models.py": MODELS_CODE,
        "database.py": DATABASE_CODE,
        "app.py": APP_CODE
    }
    for filename, content in py_files.items():
        with open(os.path.join(TARGET_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {filename}")

    html_files = {
        "base.html": BASE_HTML,
        "dashboard.html": DASHBOARD_HTML,
        "expenses.html": EXPENSES_HTML,
        "approvals.html": APPROVALS_HTML,
        "categories.html": CATEGORIES_HTML,
        "data.html": DATA_HTML,
        "reports.html": REPORTS_HTML,
        "settings.html": SETTINGS_HTML,
        "help.html": HELP_HTML
    }
    for filename, content in html_files.items():
        with open(os.path.join(templates_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ templates/{filename}")

    print("⏳ جاري تثبيت المكتبات...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-sqlalchemy"])
    
    print("🚀 جاري تشغيل المنصة الصوتية...")
    threading.Thread(target=open_browser, daemon=True).start()
    os.chdir(TARGET_DIR)
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print("\n❌ حدث خطأ. تأكد من إغلاق أي نوافذ قديمة تعمل على المنفذ 5000.")
        print(e)

if __name__ == "__main__":
    build_project()