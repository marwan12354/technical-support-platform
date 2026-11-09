# install_and_run.py
import os
import subprocess
import sys

# المسار المحدد
TARGET_DIR = r"C:\Users\PC\Downloads\مشروع منصة الدعم التقني\itsupport\ghg"

# ==========================================
# 1. كود هيكل قاعدة البيانات (models.py)
# ==========================================
MODELS_CODE = """
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # علاقة: قسم واحد لديه مصروفات كثيرة
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
# 2. كود تعبئة قاعدة البيانات (database.py)
# ==========================================
DATABASE_CODE = """
from models import db, Department, Category, Expense

def init_database(app):
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إدخال الأقسام إذا كانت فارغة
        if Department.query.count() == 0:
            departments = [
                Department(name='الإدارة المالية'),
                Department(name='إدارة الموارد البشرية'),
                Department(name='إدارة تقنية المعلومات'),
                Department(name='إدارة المشتريات')
            ]
            db.session.add_all(departments)
            
        # إدخال البنود
        if Category.query.count() == 0:
            cats = [
                Category(name='مستلزمات مكتبية', icon='fa-boxes-stacked'),
                Category(name='صيانة', icon='fa-screwdriver-wrench'),
                Category(name='طباعة', icon='fa-print'),
                Category(name='خدمات', icon='fa-network-wired'),
                Category(name='سفر وانتقال', icon='fa-plane')
            ]
            db.session.add_all(cats)
        
        # إدخال بيانات المصروفات من الصورة
        if Expense.query.count() == 0:
            finance_dept = Department.query.filter_by(name='الإدارة المالية').first()
            expenses = [
                Expense(expense_number='EX-0064', date='29/10/2026', item='مستلزمات مكتبية', department_id=finance_dept.id, amount=1200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0063', date='28/10/2026', item='صيانة', department_id=finance_dept.id, amount=800.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0062', date='27/10/2026', item='طباعة', department_id=finance_dept.id, amount=450.0, approval_status='بانتظار الاعتماد', payment_status='غير مدفوع', remaining_amount=0.0),
                Expense(expense_number='EX-0061', date='25/10/2026', item='خدمات', department_id=finance_dept.id, amount=4000.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1100.0),
                Expense(expense_number='EX-0060', date='26/10/2026', item='صيانة', department_id=finance_dept.id, amount=7200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1500.0),
                Expense(expense_number='EX-0059', date='20/10/2026', item='مستلزمات مكتبية', department_id=finance_dept.id, amount=7800.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1500.0),
            ]
            db.session.add_all(expenses)
            
        db.session.commit()
        print("✅ تم تهيئة قاعدة البيانات وإدخال البيانات بنجاح!")
"""

# ==========================================
# 3. كود الخادم (app.py)
# ==========================================
APP_CODE = """
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Expense, Department, Category
from database import init_database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.context_processor
def inject_globals():
    return dict(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

@app.route('/')
def dashboard():
    expenses = Expense.query.order_by(Expense.id.desc()).all()
    # حساب الإحصائيات
    stats = {"total_approved": 0, "total_paid": 0, "total_remaining": 0, "pending_approval": 0, "overdue": 4}
    for e in expenses:
        if e.approval_status == 'معتمد':
            stats['total_approved'] += e.amount
            stats['total_paid'] += (e.amount - e.remaining_amount)
            stats['total_remaining'] += e.remaining_amount
        if e.approval_status == 'بانتظار الاعتماد':
            stats['pending_approval'] += 1
            
    return render_template('dashboard.html', expenses=expenses, stats=stats, active_page='home')

@app.route('/expenses')
def expenses_page():
    expenses = Expense.query.order_by(Expense.id.desc()).all()
    departments = Department.query.all()
    categories = Category.query.all()
    return render_template('expenses.html', expenses=expenses, departments=departments, categories=categories, active_page='expenses')

@app.route('/add', methods=['POST'])
def add_expense():
    item = request.form.get('item')
    dept_id = int(request.form.get('department_id'))
    amount = float(request.form.get('amount'))
    app_status = request.form.get('approval_status')
    pay_status = request.form.get('payment_status')
    
    # إنشاء رقم تسلسلي جديد
    last_exp = Expense.query.order_by(Expense.id.desc()).first()
    next_num = int(last_exp.expense_number.split('-')[1]) + 1 if last_exp else 1
    exp_num = f"EX-{str(next_num).zfill(4)}"
    
    remaining = 0.0 if pay_status == "مدفوع" else amount
    
    new_exp = Expense(
        expense_number=exp_num,
        date=datetime.now().strftime("%d/%m/%Y"),
        item=item,
        department_id=dept_id,
        amount=amount,
        approval_status=app_status,
        payment_status=pay_status,
        remaining_amount=remaining
    )
    
    try:
        db.session.add(new_exp)
        db.session.commit()
        flash('تم إضافة المصروف بنجاح!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'error')
        
    return redirect(url_for('expenses_page'))

@app.route('/categories')
def categories_page():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories, active_page='categories')

if __name__ == '__main__':
    # التحقق من وجود قاعدة البيانات، وإنشائها إذا لم تكن موجودة
    if not os.path.exists('expenses.db'):
        print("جاري إنشاء قاعدة البيانات...")
        init_database(app)
    
    print("=========================================")
    print("المنصة تعمل الآن! افتح المتصفح على: http://127.0.0.1:5000")
    print("=========================================")
    app.run(debug=True, port=5000)
"""

# ==========================================
# 4. ملفات الواجهة (Templates)
# ==========================================
BASE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl" x-data="{ sidebarOpen: false, modalOpen: false }">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة المصروفات</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = { theme: { extend: { fontFamily: { sans: ['Cairo', 'sans-serif'] }, colors: { brand: '#ea580c', dark: '#1e293b' } } } }
    </script>
    <style>
        body { font-family: 'Cairo', sans-serif; background-color: #f1f5f9; }
        [x-cloak] { display: none !important; }
        .nav-link { transition: all 0.3s ease; }
        .nav-link:hover { background-color: rgba(255,255,255,0.1); }
        .nav-active { background-color: #ea580c; color: white; border-radius: 8px; }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .badge { padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700; }
        .badge-green { background: #dcfce7; color: #166534; }
        .badge-yellow { background: #fef08a; color: #854d0e; }
        .badge-blue { background: #dbeafe; color: #1e40af; }
        .badge-red { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-gray-800">
    <div x-show="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black opacity-50 z-20 lg:hidden" x-cloak></div>
    
    <!-- القائمة الجانبية -->
    <aside :class="sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'" class="fixed lg:relative w-[260px] h-full bg-dark text-gray-300 flex flex-col shrink-0 shadow-xl z-30 transform transition-transform duration-300 ease-in-out">
        <div class="p-6 flex flex-col items-center border-b border-gray-700">
            <div class="bg-white p-3 rounded-xl mb-3 shadow-md"><i class="fa-solid fa-file-invoice-dollar text-3xl text-dark"></i></div>
            <h1 class="text-white font-bold text-lg text-center leading-tight">المصروفات<br>التشغيلية</h1>
        </div>
        <nav class="flex-1 py-4 space-y-1 px-3 text-sm font-bold overflow-y-auto">
            <a href="/" class="{% if active_page == 'home' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-house w-5 text-center"></i> لوحة القيادة</a>
            <a href="/expenses" class="{% if active_page == 'expenses' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-file-lines w-5 text-center"></i> سجل المصروفات</a>
            <a href="/categories" class="{% if active_page == 'categories' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-layer-group w-5 text-center"></i> بنود الصرف</a>
        </nav>
    </aside>
    
    <!-- المحتوى الرئيسي -->
    <main class="flex-1 flex flex-col h-full overflow-hidden relative w-full">
        <header class="bg-white px-6 py-4 flex justify-between items-center border-b sticky top-0 z-10 shadow-sm">
            <div class="flex items-center gap-4">
                <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden text-gray-600 hover:text-brand"><i class="fa-solid fa-bars text-2xl"></i></button>
                <div>
                    <h2 class="text-2xl font-extrabold text-gray-800">{% block title %}{% endblock %}</h2>
                    <p class="text-sm text-gray-500 font-semibold">بيانات توضيحية | {{ now }}</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                {% block header_actions %}{% endblock %}
            </div>
        </header>

        <!-- التنبيهات -->
        <div class="absolute top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4" x-data="{ show: true }" x-show="show" x-init="setTimeout(() => show = false, 4000)" x-cloak>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="mb-2 p-4 rounded-xl shadow-lg flex items-center justify-between font-bold text-sm {{ 'bg-green-100 text-green-800 border-r-4 border-green-500' if category == 'success' else 'bg-red-100 text-red-800 border-r-4 border-red-500' }}">
                            <span><i class="fa-solid {{ 'fa-check-circle' if category == 'success' else 'fa-exclamation-triangle' }} ml-2"></i> {{ message }}</span>
                            <button @click="show = false" class="text-gray-500"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>

        <div class="p-6 overflow-y-auto h-full">
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
<!-- البطاقات الإحصائية -->
<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-white rounded-xl p-4 flex items-center justify-between shadow-sm border border-gray-100 card-hover">
        <div><span class="block text-gray-500 font-bold text-sm mb-1">بانتظار الاعتماد</span><span class="text-2xl font-extrabold text-gray-800">{{ stats.pending_approval }}</span></div>
        <div class="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center text-brand text-xl"><i class="fa-solid fa-user-clock"></i></div>
    </div>
    <div class="bg-white rounded-xl p-4 flex items-center justify-between shadow-sm border border-gray-100 card-hover">
        <div><span class="block text-gray-500 font-bold text-sm mb-1">متأخرة في السداد</span><span class="text-2xl font-extrabold text-gray-800">{{ stats.overdue }}</span></div>
        <div class="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center text-red-500 text-xl"><i class="fa-solid fa-calendar-xmark"></i></div>
    </div>
    <div class="bg-[#2a3441] text-white rounded-xl p-4 flex flex-col justify-between shadow-md card-hover">
        <div class="flex justify-between items-start"><span class="text-gray-300 font-bold text-sm">المتبقي</span><i class="fa-solid fa-sack-dollar text-brand text-xl"></i></div>
        <div class="flex justify-between items-end mt-2"><span class="text-2xl font-extrabold">{{ "{:,.0f}".format(stats.total_remaining) }}</span></div>
    </div>
    <div class="bg-[#2a3441] text-white rounded-xl p-4 flex flex-col justify-between shadow-md card-hover">
        <div class="flex justify-between items-start"><span class="text-gray-300 font-bold text-sm">المدفوع</span><i class="fa-solid fa-hand-holding-dollar text-brand text-xl"></i></div>
        <div class="flex justify-between items-end mt-2"><span class="text-2xl font-extrabold">{{ "{:,.0f}".format(stats.total_paid) }}</span></div>
    </div>
</div>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 class="font-bold text-lg mb-4 text-gray-800"><i class="fa-solid fa-chart-line text-brand ml-2"></i> الأداء المالي</h3>
        <canvas id="dashChart"></canvas>
    </div>
    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 class="font-bold text-lg mb-4 text-gray-800"><i class="fa-solid fa-clock-rotate-left text-brand ml-2"></i> أحدث العمليات</h3>
        <div class="space-y-3">
            {% for exp in expenses[:4] %}
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                <div><p class="font-bold text-gray-800">{{ exp.item }}</p><p class="text-xs text-gray-500">{{ exp.date }} | {{ exp.department.name }}</p></div>
                <span class="font-extrabold text-brand">{{ exp.amount }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
<script>
    new Chart(document.getElementById('dashChart'), {
        type: 'line',
        data: { labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو'], datasets: [{ label: 'المصروفات', data: [12000, 19000, 15000, 22000, 24800], borderColor: '#ea580c', backgroundColor: 'rgba(234, 88, 12, 0.1)', fill: true, tension: 0.4 }] }
    });
</script>
{% endblock %}
"""

EXPENSES_HTML = """
{% extends "base.html" %}
{% block title %}سجل المصروفات{% endblock %}
{% block header_actions %}
<button @click="modalOpen = true" class="bg-brand text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-orange-700 shadow-sm transition"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
        <table class="w-full text-right text-sm whitespace-nowrap">
            <thead class="bg-gray-100 text-gray-600 font-extrabold border-b border-gray-200">
                <tr>
                    <th class="py-3 px-4">رقم المصروف</th><th class="py-3 px-4">التاريخ</th><th class="py-3 px-4">البند</th><th class="py-3 px-4">الإدارة</th><th class="py-3 px-4">المبلغ</th><th class="py-3 px-4 text-center">الاعتماد</th><th class="py-3 px-4 text-center">السداد</th><th class="py-3 px-4 text-center">المتبقي</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for exp in expenses %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="py-3 px-4 font-bold text-gray-800">{{ exp.expense_number }}</td>
                    <td class="py-3 px-4 text-gray-600">{{ exp.date }}</td>
                    <td class="py-3 px-4 font-bold">{{ exp.item }}</td>
                    <td class="py-3 px-4 text-gray-600">{{ exp.department.name }}</td>
                    <td class="py-3 px-4 font-extrabold text-gray-800">{{ exp.amount }}</td>
                    <td class="py-3 px-4 text-center"><span class="badge {{ 'badge-green' if exp.approval_status == 'معتمد' else 'badge-blue' }}">{{ exp.approval_status }}</span></td>
                    <td class="py-3 px-4 text-center"><span class="badge {{ 'badge-yellow' if exp.payment_status == 'مدفوع جزئياً' else 'badge-red' }}">{{ exp.payment_status }}</span></td>
                    <td class="py-3 px-4 text-center font-bold">{{ exp.remaining_amount }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Modal إضافة مصروف -->
<div x-show="modalOpen" x-cloak class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div @click.away="modalOpen = false" class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6" x-transition>
        <div class="flex justify-between items-center mb-4 border-b pb-3">
            <h3 class="text-xl font-extrabold text-gray-800">إضافة مصروف</h3>
            <button @click="modalOpen = false" class="text-gray-400 hover:text-red-500"><i class="fa-solid fa-xmark text-2xl"></i></button>
        </div>
        <form action="/add" method="POST" class="space-y-4">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">البند</label>
                <select name="item" class="w-full border p-2.5 rounded-lg bg-gray-50 focus:border-brand outline-none" required>
                    {% for cat in categories %}
                    <option value="{{ cat.name }}">{{ cat.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div><label class="block text-sm font-bold text-gray-700 mb-1">المبلغ</label><input type="number" name="amount" required class="w-full border p-2.5 rounded-lg bg-gray-50"></div>
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1">الإدارة</label>
                    <select name="department_id" class="w-full border p-2.5 rounded-lg bg-gray-50">
                        {% for dept in departments %}
                        <option value="{{ dept.id }}">{{ dept.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div><label class="block text-sm font-bold text-gray-700 mb-1">الاعتماد</label><select name="approval_status" class="w-full border p-2.5 rounded-lg bg-gray-50"><option value="بانتظار الاعتماد">بانتظار الاعتماد</option><option value="معتمد">معتمد</option></select></div>
                <div><label class="block text-sm font-bold text-gray-700 mb-1">السداد</label><select name="payment_status" class="w-full border p-2.5 rounded-lg bg-gray-50"><option value="غير مدفوع">غير مدفوع</option><option value="مدفوع">مدفوع</option></select></div>
            </div>
            <button type="submit" class="w-full bg-brand text-white font-extrabold py-3 rounded-xl hover:bg-orange-700 transition mt-2">حفظ البيانات</button>
        </form>
    </div>
</div>
{% endblock %}
"""

CATEGORIES_HTML = """
{% extends "base.html" %}
{% block title %}بنود الصرف{% endblock %}
{% block content %}
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
    {% for cat in categories %}
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 card-hover text-center cursor-pointer">
        <div class="w-16 h-16 mx-auto bg-orange-50 text-brand rounded-full flex items-center justify-center text-3xl mb-4">
            <i class="fa-solid {{ cat.icon }}"></i>
        </div>
        <h4 class="font-extrabold text-lg text-gray-800">{{ cat.name }}</h4>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

# ==========================================
# 5. دالة التثبيت والبناء
# ==========================================
def build_project():
    # 1. إنشاء المجلدات
    print("⏳ جاري إنشاء المجلدات...")
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    templates_dir = os.path.join(TARGET_DIR, "templates")
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)

    # 2. كتابة ملفات بايثون
    print("📝 جاري كتابة ملفات بايثون...")
    py_files = {
        "models.py": MODELS_CODE,
        "database.py": DATABASE_CODE,
        "app.py": APP_CODE
    }
    for filename, content in py_files.items():
        with open(os.path.join(TARGET_DIR, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {filename}")

    # 3. كتابة ملفات HTML
    print("🎨 جاري كتابة ملفات الواجهة...")
    html_files = {
        "base.html": BASE_HTML,
        "dashboard.html": DASHBOARD_HTML,
        "expenses.html": EXPENSES_HTML,
        "categories.html": CATEGORIES_HTML
    }
    for filename, content in html_files.items():
        with open(os.path.join(templates_dir, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ templates/{filename}")

    # 4. تثبيت المكتبات
    print("📦 جاري تثبيت المكتبات (Flask, SQLAlchemy)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-sqlalchemy"])
    
    # 5. تشغيل المنصة
    print("🚀 جاري تشغيل الخادم...")
    os.chdir(TARGET_DIR)
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    build_project()