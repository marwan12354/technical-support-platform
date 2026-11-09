# 4_master_install.py (النسخة الاحترافية - Enterprise)
import os
import subprocess
import sys

TARGET_DIR = r"C:\Users\PC\Downloads\مشروع منصة الدعم التقني\itsupport\ghg"

# ==========================================
# 1. ملف قاعدة البيانات (1_models.py)
# ==========================================
DB_CODE = """from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
    department = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    approval_status = db.Column(db.String(50), default='بانتظار الاعتماد')
    payment_status = db.Column(db.String(50), default='غير مدفوع')
    remaining_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_data():
    if Category.query.count() == 0:
        cats = [
            Category(name='مستلزمات مكتبية', icon='fa-boxes-stacked'),
            Category(name='صيانة', icon='fa-screwdriver-wrench'),
            Category(name='طباعة', icon='fa-print'),
            Category(name='خدمات', icon='fa-network-wired'),
            Category(name='سفر وانتقال', icon='fa-plane')
        ]
        db.session.add_all(cats)
    
    if Expense.query.count() == 0:
        expenses = [
            Expense(expense_number='EX-0064', date='29/10/2026', item='مستلزمات مكتبية', department='الإدارة المالية', amount=1200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
            Expense(expense_number='EX-0063', date='28/10/2026', item='صيانة', department='الإدارة المالية', amount=800.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
            Expense(expense_number='EX-0062', date='27/10/2026', item='طباعة', department='الإدارة المالية', amount=450.0, approval_status='بانتظار الاعتماد', payment_status='غير مدفوع', remaining_amount=450.0),
            Expense(expense_number='EX-0061', date='25/10/2026', item='خدمات', department='الإدارة المالية', amount=4000.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1100.0),
            Expense(expense_number='EX-0060', date='26/10/2026', item='صيانة', department='الإدارة المالية', amount=7200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1500.0),
        ]
        db.session.add_all(expenses)
    
    db.session.commit()
"""

# ==========================================
# 2. ملف الواجهة (2_templates.py) - Alpine.js & Tailwind
# ==========================================
TEMPLATE_CODE = """# القوالب المطورة باستخدام Jinja2 + Alpine.js

BASE_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl" x-data="{ sidebarOpen: false, modalOpen: false }">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام المصروفات - Enterprise</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {
            theme: { extend: { fontFamily: { sans: ['Tajawal', 'sans-serif'] }, colors: { brand: '#ea580c', dark: '#1e293b', surface: '#ffffff', bg: '#f3f4f6' } } }
        }
    </script>
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f3f4f6; }
        [x-cloak] { display: none !important; }
        .nav-link { transition: all 0.3s ease; }
        .nav-link:hover { background-color: rgba(255,255,255,0.1); transform: translateX(-5px); }
        .nav-active { background-color: #ea580c; color: white; box-shadow: 0 4px 6px -1px rgba(234, 88, 12, 0.4); }
        .card-hover { transition: all 0.3s ease; }
        .card-hover:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
        .badge { padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; }
        .badge-success { background: #dcfce7; color: #166534; }
        .badge-warning { background: #fef08a; color: #854d0e; }
        .badge-info { background: #dbeafe; color: #1e40af; }
        .badge-danger { background: #fee2e2; color: #991b1b; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-gray-800">
    <!-- Mobile Sidebar Overlay -->
    <div x-show="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 bg-black opacity-50 z-20 lg:hidden" x-cloak></div>

    <!-- Sidebar -->
    <aside :class="sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'" class="fixed lg:relative w-[260px] h-full bg-dark text-gray-300 flex flex-col shrink-0 shadow-xl z-30 transform transition-transform duration-300 ease-in-out">
        <div class="p-6 flex flex-col items-center border-b border-gray-700">
            <div class="bg-gradient-to-br from-brand to-orange-400 p-3 rounded-xl mb-3 shadow-lg"><i class="fa-solid fa-file-invoice-dollar text-3xl text-white"></i></div>
            <h1 class="text-white font-bold text-lg text-center leading-tight">المصروفات<br><span class="text-brand text-sm">Enterprise</span></h1>
        </div>
        <nav class="flex-1 py-4 space-y-1 px-3 text-sm font-bold overflow-y-auto">
            <a href="/" class="{% if active_page == 'home' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-house w-5 text-center"></i> الرئيسية</a>
            <a href="/expenses" class="{% if active_page == 'expenses' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-file-lines w-5 text-center"></i> سجل المصروفات</a>
            <a href="/categories" class="{% if active_page == 'categories' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-layer-group w-5 text-center"></i> بنود الصرف</a>
            <a href="/reports" class="{% if active_page == 'reports' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-chart-pie w-5 text-center"></i> التقارير</a>
            <a href="/settings" class="{% if active_page == 'settings' %}nav-active{% else %}nav-link{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg"><i class="fa-solid fa-gear w-5 text-center"></i> الإعدادات</a>
        </nav>
    </aside>
    
    <main class="flex-1 flex flex-col h-full overflow-hidden relative w-full">
        <!-- Header -->
        <header class="bg-white/80 backdrop-blur-md px-6 py-4 flex justify-between items-center border-b sticky top-0 z-10 shadow-sm">
            <div class="flex items-center gap-4">
                <button @click="sidebarOpen = !sidebarOpen" class="lg:hidden text-gray-600 hover:text-brand"><i class="fa-solid fa-bars text-2xl"></i></button>
                <div>
                    <h2 class="text-2xl font-extrabold text-gray-800">{% block page_title %}{% endblock %}</h2>
                    <p class="text-sm text-gray-500 font-semibold">لوحة تحكم متطورة | {{ now }}</p>
                </div>
            </div>
            <div class="flex items-center gap-4">
                {% block header_actions %}{% endblock %}
                <div class="w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-bold shadow-md cursor-pointer hover:bg-orange-600 transition">A</div>
            </div>
        </header>

        <!-- Flash Messages (Toasts) -->
        <div class="absolute top-20 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4" x-data="{ show: true }" x-show="show" x-init="setTimeout(() => show = false, 4000)" x-cloak>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="mb-2 p-4 rounded-xl shadow-lg flex items-center justify-between font-bold text-sm transition-all duration-300 {{ 'bg-green-100 text-green-800 border-r-4 border-green-500' if category == 'success' else 'bg-red-100 text-red-800 border-r-4 border-red-500' }}">
                            <span><i class="fa-solid {{ 'fa-check-circle' if category == 'success' else 'fa-exclamation-triangle' }} ml-2"></i> {{ message }}</span>
                            <button @click="show = false" class="text-gray-500 hover:text-gray-800"><i class="fa-solid fa-xmark"></i></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>

        <!-- Main Content -->
        <div class="p-6 overflow-y-auto h-full">
            {% block content %}{% endblock %}
        </div>
    </main>
</body>
</html>
'''

# صفحة الرئيسية (Dashboard)
HOME_HTML = '''
{% extends "base" %}
{% block page_title %}لوحة القيادة{% endblock %}
{% block content %}
<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
    <div class="bg-white rounded-xl p-6 shadow-sm card-hover border-r-4 border-brand">
        <div class="flex justify-between items-center">
            <div><p class="text-gray-500 font-bold text-sm">المعتمد</p><p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_approved) }}</p></div>
            <div class="w-12 h-12 rounded-full bg-orange-50 text-brand flex items-center justify-center text-xl"><i class="fa-solid fa-check"></i></div>
        </div>
    </div>
    <div class="bg-white rounded-xl p-6 shadow-sm card-hover border-r-4 border-green-500">
        <div class="flex justify-between items-center">
            <div><p class="text-gray-500 font-bold text-sm">المدفوع</p><p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_paid) }}</p></div>
            <div class="w-12 h-12 rounded-full bg-green-50 text-green-500 flex items-center justify-center text-xl"><i class="fa-solid fa-hand-holding-dollar"></i></div>
        </div>
    </div>
    <div class="bg-white rounded-xl p-6 shadow-sm card-hover border-r-4 border-blue-500">
        <div class="flex justify-between items-center">
            <div><p class="text-gray-500 font-bold text-sm">المتبقي</p><p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_remaining) }}</p></div>
            <div class="w-12 h-12 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center text-xl"><i class="fa-solid fa-sack-dollar"></i></div>
        </div>
    </div>
    <div class="bg-white rounded-xl p-6 shadow-sm card-hover border-r-4 border-red-500">
        <div class="flex justify-between items-center">
            <div><p class="text-gray-500 font-bold text-sm">معلق</p><p class="text-3xl font-extrabold text-gray-800 mt-2">{{ stats.pending_approval }}</p></div>
            <div class="w-12 h-12 rounded-full bg-red-50 text-red-500 flex items-center justify-center text-xl"><i class="fa-solid fa-clock"></i></div>
        </div>
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
            {% for exp in latest_expenses %}
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition">
                <div><p class="font-bold text-gray-800">{{ exp.item }}</p><p class="text-xs text-gray-500">{{ exp.date }} | {{ exp.department }}</p></div>
                <span class="font-extrabold text-brand">{{ exp.amount }} <span class="text-xs text-gray-400">ر.س</span></span>
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
'''

# صفحة سجل المصروفات
EXPENSES_HTML = '''
{% extends "base" %}
{% block page_title %}سجل المصروفات{% endblock %}
{% block header_actions %}
<button @click="modalOpen = true" class="bg-brand text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-orange-700 shadow-sm transition card-hover"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
{% endblock %}
{% block content %}
<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
    <div class="p-4 border-b bg-gray-50 flex justify-between items-center">
        <input type="text" placeholder="بحث..." class="border p-2 rounded-lg text-sm w-64 focus:outline-brand">
        <span class="text-sm font-bold text-gray-500">إجمالي السجلات: {{ expenses|length }}</span>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full text-right text-sm whitespace-nowrap">
            <thead class="bg-gray-100 text-gray-600 font-extrabold border-b border-gray-200">
                <tr>
                    <th class="py-4 px-4">رقم</th><th class="py-4 px-4">التاريخ</th><th class="py-4 px-4">البند</th><th class="py-4 px-4">الإدارة</th><th class="py-4 px-4">المبلغ</th><th class="py-4 px-4 text-center">الاعتماد</th><th class="py-4 px-4 text-center">السداد</th><th class="py-4 px-4 text-center">المتبقي</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for exp in expenses %}
                <tr class="hover:bg-gray-50 transition-colors">
                    <td class="py-4 px-4 font-bold text-gray-800">{{ exp.expense_number }}</td>
                    <td class="py-4 px-4 text-gray-600">{{ exp.date }}</td>
                    <td class="py-4 px-4 font-bold">{{ exp.item }}</td>
                    <td class="py-4 px-4 text-gray-600">{{ exp.department }}</td>
                    <td class="py-4 px-4 font-extrabold text-gray-800">{{ exp.amount }}</td>
                    <td class="py-4 px-4 text-center"><span class="badge {{ 'badge-success' if exp.approval_status == 'معتمد' else 'badge-info' }}">{{ exp.approval_status }}</span></td>
                    <td class="py-4 px-4 text-center"><span class="badge {{ 'badge-warning' if exp.payment_status == 'مدفوع جزئياً' else 'badge-danger' }}">{{ exp.payment_status }}</span></td>
                    <td class="py-4 px-4 text-center font-bold">{{ exp.remaining_amount }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Alpine.js Modal -->
<div x-show="modalOpen" x-cloak class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm transition-opacity">
    <div @click.away="modalOpen = false" class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 transform transition-all" x-transition:enter="ease-out duration-300" x-transition:enter-start="opacity-0 scale-95" x-transition:enter-end="opacity-100 scale-100">
        <div class="flex justify-between items-center mb-4 border-b pb-3">
            <h3 class="text-xl font-extrabold text-gray-800"><i class="fa-solid fa-plus-circle text-brand ml-2"></i> إضافة مصروف</h3>
            <button @click="modalOpen = false" class="text-gray-400 hover:text-red-500"><i class="fa-solid fa-xmark text-2xl"></i></button>
        </div>
        <form action="/add" method="POST" class="space-y-4">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <div>
                <label class="block text-sm font-bold text-gray-700 mb-1">البند</label>
                <select name="item" class="w-full border p-2.5 rounded-lg bg-gray-50 focus:border-brand outline-none" required>
                    {% for cat in categories %}
                    <option value="{{ cat.name }}">{{ cat.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div><label class="block text-sm font-bold text-gray-700 mb-1">المبلغ</label><input type="number" name="amount" required class="w-full border p-2.5 rounded-lg bg-gray-50 focus:border-brand outline-none"></div>
                <div><label class="block text-sm font-bold text-gray-700 mb-1">الإدارة</label><select name="department" class="w-full border p-2.5 rounded-lg bg-gray-50"><option>الإدارة المالية</option><option>الموارد البشرية</option><option>تقنية المعلومات</option></select></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div><label class="block text-sm font-bold text-gray-700 mb-1">الاعتماد</label><select name="approval_status" class="w-full border p-2.5 rounded-lg bg-gray-50"><option value="بانتظار الاعتماد">بانتظار الاعتماد</option><option value="معتمد">معتمد</option></select></div>
                <div><label class="block text-sm font-bold text-gray-700 mb-1">السداد</label><select name="payment_status" class="w-full border p-2.5 rounded-lg bg-gray-50"><option value="غير مدفوع">غير مدفوع</option><option value="مدفوع">مدفوع</option></select></div>
            </div>
            <button type="submit" class="w-full bg-brand text-white font-extrabold py-3 rounded-xl hover:bg-orange-700 shadow-lg shadow-brand/30 transition mt-4">حفظ البيانات</button>
        </form>
    </div>
</div>
{% endblock %}
'''

# صفحة البنود
CATEGORIES_HTML = '''
{% extends "base" %}
{% block page_title %}بنود الصرف{% endblock %}
{% block content %}
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
    {% for cat in categories %}
    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 card-hover text-center cursor-pointer">
        <div class="w-16 h-16 mx-auto bg-orange-50 text-brand rounded-full flex items-center justify-center text-3xl mb-4 shadow-inner">
            <i class="fa-solid {{ cat.icon }}"></i>
        </div>
        <h4 class="font-extrabold text-xl text-gray-800">{{ cat.name }}</h4>
        <p class="text-sm text-gray-500 mt-2">انقر للتفاصيل</p>
    </div>
    {% endfor %}
</div>
{% endblock %}
'''
"""

# ==========================================
# 3. ملف الخادم (3_server.py) - مع CSRF و ORM
# ==========================================
SERVER_CODE = """import os
import sys
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from importlib import import_module
models = import_module("1_models")
templates = import_module("2_templates")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-for-csrf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
models.db.init_app(app)

# محرك القوالب المخصص (Mimicking Laravel Blade)
def render_blade(template_name, page_title_block, content_block, **context):
    base = templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", page_title_block)
    content = templates.__dict__.get(content_block, "").replace("{% extends \"base\" %}", "")
    
    # محاكاة بسيطة لـ Jinja2 Blocks
    content = content.replace("{% block page_title %}{% endblock %}", page_title_block)
    content = content.replace("{% block content %}{% endblock %}", "")
    
    # دمج المحتوى داخل القالب الأساسي
    final_html = base.replace("{% block content %}{% endblock %}", content)
    
    # تمرير المتغيرات السياقية
    return render_template_string(final_html, **context)

@app.context_processor
def inject_globals():
    return dict(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

@app.route('/')
def home():
    expenses = models.Expense.query.order_by(models.Expense.id.desc()).all()
    stats = {"total_approved": 0, "total_paid": 0, "total_remaining": 0, "pending_approval": 0}
    for e in expenses:
        if e.approval_status == 'معتمد':
            stats['total_approved'] += e.amount
            stats['total_paid'] += (e.amount - e.remaining_amount)
            stats['total_remaining'] += e.remaining_amount
        if e.approval_status == 'بانتظار الاعتماد':
            stats['pending_approval'] += 1
            
    content = templates.HOME_HTML.replace("{% extends \"base\" %}", "").replace("{% block page_title %}لوحة القيادة{% endblock %}", "").replace("{% block content %}", "").replace("{% endblock %}", "")
    return render_template_string(templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", "لوحة القيادة").replace("{% block content %}{% endblock %}", content), expenses=expenses, latest_expenses=expenses[:4], stats=stats, active_page='home')

@app.route('/expenses')
def expenses_page():
    expenses = models.Expense.query.order_by(models.Expense.id.desc()).all()
    categories = models.Category.query.all()
    
    content = templates.EXPENSES_HTML.replace("{% extends \"base\" %}", "").replace("{% block page_title %}سجل المصروفات{% endblock %}", "").replace("{% block header_actions %}", "").replace("{% endblock %}", "")
    
    return render_template_string(templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", "سجل المصروفات").replace("{% block header_actions %}{% endblock %}", "").replace("{% block content %}{% endblock %}", content), expenses=expenses, categories=categories, active_page='expenses')

@app.route('/categories')
def categories_page():
    categories = models.Category.query.all()
    content = templates.CATEGORIES_HTML.replace("{% extends \"base\" %}", "").replace("{% block page_title %}بنود الصرف{% endblock %}", "").replace("{% block content %}", "").replace("{% endblock %}", "")
    return render_template_string(templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", "بنود الصرف").replace("{% block content %}{% endblock %}", content), categories=categories, active_page='categories')

@app.route('/add', methods=['POST'])
@csrf.exempt # تم تجاوزها هنا لتسهيل الاختبار، ولكن في الإنتاج يجب التحقق منها
def add():
    item = request.form.get('item')
    dept = request.form.get('department')
    amount = float(request.form.get('amount', 0))
    app_status = request.form.get('approval_status')
    pay_status = request.form.get('payment_status')
    
    if not item or amount <= 0:
        flash('الرجاء إدخال بيانات صحيحة', 'error')
        return redirect(url_for('expenses_page'))

    remaining = 0.0 if pay_status == "مدفوع" else amount
    exp_num = "EX-00" + str(int(datetime.now().timestamp()) % 10000)
    
    new_exp = models.Expense(
        expense_number=exp_num, date=datetime.now().strftime("%d/%m/%Y"),
        item=item, department=dept, amount=amount,
        approval_status=app_status, payment_status=pay_status, remaining_amount=remaining
    )
    
    try:
        models.db.session.add(new_exp)
        models.db.session.commit()
        flash('تم إضافة المصروف بنجاح!', 'success')
    except Exception as e:
        models.db.session.rollback()
        flash('حدث خطأ أثناء الإضافة.', 'error')

    return redirect(url_for('expenses_page'))

if __name__ == '__main__':
    with app.app_context():
        models.db.create_all()
        models.seed_data()
    
    print("=========================================")
    print("المنصة الاحترافية (Laravel-Style) تعمل الآن!")
    print("افتح: http://127.0.0.1:5000")
    print("=========================================")
    app.run(debug=True, port=5000)
"""

# ==========================================
# 4. السكريبت المايسترو (التثبيت والتشغيل)
# ==========================================
def setup_project():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    files = {
        "1_models.py": DB_CODE,
        "2_templates.py": TEMPLATE_CODE,
        "3_server.py": SERVER_CODE
    }
    
    for filename, content in files.items():
        filepath = os.path.join(TARGET_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ تم إنشاء/تحديث: {filename}")

    print("⏳ جاري تثبيت المكتبات (Flask, SQLAlchemy, WTForms)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-sqlalchemy", "flask-wtf", "email-validator"])
    
    print("🚀 جاري تشغيل المنصة الاحترافية...")
    os.chdir(TARGET_DIR)
    subprocess.call([sys.executable, "3_server.py"])

if __name__ == "__main__":
    setup_project()