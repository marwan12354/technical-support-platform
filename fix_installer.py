import os
import subprocess
import sys

# المسار الدقيق الذي طلبته لإنشاء المنصة بداخله
TARGET_DIR = r"C:\Users\PC\Downloads\مشروع منصة الدعم التقني\itsupport\ghg"

DB_CODE = '''import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "expenses.db")

def init_db():
    print("[DB] جاري الاتصال بقاعدة البيانات...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_number TEXT UNIQUE,
            date TEXT,
            item TEXT,
            department TEXT,
            amount REAL,
            approval_status TEXT,
            payment_status TEXT,
            remaining_amount REAL
        )
    """)
    cursor.execute("DELETE FROM expenses")
    
    sample_data = [
        ("EX-0064", "29/10/2026", "مستلزمات مكتبية", "الإدارة المالية", 1200.0, "معتمد", "مدفوع جزئياً", 500.0),
        ("EX-0063", "28/10/2026", "صيانة", "الإدارة المالية", 800.0, "معتمد", "مدفوع جزئياً", 500.0),
        ("EX-0062", "27/10/2026", "طباعة", "الإدارة المالية", 450.0, "بانتظار الاعتماد", "غير مدفوع", 0.0),
        ("EX-0061", "25/10/2026", "خدمات", "الإدارة المالية", 4000.0, "معتمد", "مدفوع جزئياً", 1100.0),
        ("EX-0060", "26/10/2026", "صيانة", "الإدارة المالية", 7200.0, "معتمد", "مدفوع جزئياً", 1500.0),
        ("EX-0059", "20/10/2026", "مستلزمات مكتبية", "الإدارة المالية", 7800.0, "معتمد", "مدفوع جزئياً", 1500.0),
    ]
    
    cursor.executemany("""
        INSERT INTO expenses (expense_number, date, item, department, amount, approval_status, payment_status, remaining_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)
    conn.commit()
    print(f"[DB] ✅ تم إدخال {len(sample_data)} سجلات بنجاح في: {DB_NAME}")
    conn.close()

def get_dashboard_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY id ASC")
    expenses = [dict(row) for row in cursor.fetchall()]
    print(f"[SERVER] تم جلب {len(expenses)} سجلات لعرضها في الواجهة.")
    stats = {
        "total_approved": 24800,
        "total_paid": 18600,
        "total_remaining": 6200,
        "pending_approval": 8,
        "overdue": 4
    }
    conn.close()
    return expenses, stats
'''

TEMPLATE_CODE = '''HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سجل المصروفات التشغيلية</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Tajawal', 'sans-serif'] },
                    colors: { brand: '#ea580c', dark: '#1e293b', bg: '#f8fafc' }
                }
            }
        }
    </script>
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f1f5f9; }
        .nav-item:hover { background-color: #334155; }
        .nav-active { background-color: #ea580c; color: white; border-radius: 8px; }
        .badge-green { background-color: #dcfce7; color: #166534; }
        .badge-yellow { background-color: #fef08a; color: #854d0e; }
        .badge-blue { background-color: #dbeafe; color: #1e40af; }
        .badge-red { background-color: #fee2e2; color: #991b1b; }
        .kpi-dark { background-color: #2a3441; color: white; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-gray-800">
    <aside class="w-[260px] bg-dark text-gray-300 flex flex-col h-full shrink-0 shadow-lg">
        <div class="p-6 flex flex-col items-center border-b border-gray-700">
            <div class="bg-white p-3 rounded-lg mb-3 shadow-md"><i class="fa-solid fa-file-invoice-dollar text-3xl text-dark"></i></div>
            <h1 class="text-white font-bold text-lg text-center leading-tight">المصروفات<br>التشغيلية</h1>
        </div>
        <nav class="flex-1 py-4 space-y-1 px-3 text-sm font-bold overflow-y-auto">
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-house w-5 text-center"></i> الرئيسية</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-database w-5 text-center"></i> إدارة البيانات</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-active shadow-md"><i class="fa-solid fa-file-lines w-5 text-center"></i> سجل المصروفات</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-check-double w-5 text-center"></i> الاعتماد والسداد</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-layer-group w-5 text-center"></i> بنود الصرف</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-chart-pie w-5 text-center"></i> التقارير</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-gear w-5 text-center"></i> الإعدادات</a>
            <div class="border-t border-gray-600 my-3"></div>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-book-open w-5 text-center"></i> دليل الاستخدام</a>
        </nav>
    </aside>
    <main class="flex-1 overflow-y-auto">
        <header class="bg-white px-6 py-4 flex justify-between items-center border-b sticky top-0 z-10 shadow-sm">
            <div>
                <h2 class="text-2xl font-extrabold text-gray-800">سجل المصروفات</h2>
                <p class="text-sm text-gray-500 mt-1 font-semibold">بيانات توضيحية | حتى 02/11/2026</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="flex border rounded-lg overflow-hidden text-sm font-bold bg-gray-50">
                    <button class="px-4 py-2.5 hover:bg-gray-100 border-l text-gray-700"><i class="fa-solid fa-print text-gray-500 ml-1"></i> طباعة الكشف</button>
                    <button class="px-4 py-2.5 hover:bg-gray-100 text-gray-700"><i class="fa-solid fa-arrow-up-from-bracket text-gray-500 ml-1"></i> تصدير الكشف</button>
                </div>
                <div class="flex items-center border rounded-lg bg-gray-50 px-3 py-2 text-sm font-bold text-gray-700 cursor-pointer"><i class="fa-solid fa-folder-open text-gray-500 ml-2"></i> إدارة السجل المحدد EX-0064</div>
                <button class="bg-brand text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-orange-700 shadow-sm transition"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
            </div>
        </header>
        <div class="p-6 space-y-4 max-w-[1400px] mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
                <div class="flex flex-col gap-4">
                    <div class="bg-white rounded-xl p-3 flex items-center justify-between shadow-sm border border-gray-200 h-[72px]">
                        <div><span class="block text-gray-600 text-sm font-bold mb-1">بانتظار الاعتماد</span><span class="text-xl font-extrabold text-gray-800">{{ stats.pending_approval }}</span></div>
                        <div class="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center text-brand text-xl"><i class="fa-solid fa-user-clock"></i></div>
                    </div>
                    <div class="bg-white rounded-xl p-3 flex items-center justify-between shadow-sm border border-gray-200 h-[72px]">
                        <div><span class="block text-gray-600 text-sm font-bold mb-1">متأخرة في السداد</span><span class="text-xl font-extrabold text-gray-800">{{ stats.overdue }}</span></div>
                        <div class="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center text-red-500 text-xl"><i class="fa-solid fa-calendar-xmark"></i></div>
                    </div>
                </div>
                <div class="kpi-dark rounded-xl p-4 flex flex-col justify-between shadow-md h-[160px]">
                    <div class="flex justify-between items-start"><span class="text-gray-300 text-sm font-bold">المتبقي</span><i class="fa-solid fa-sack-dollar text-brand text-xl"></i></div>
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_remaining) }}</span><span class="text-xs font-semibold bg-gray-700 px-2 py-1 rounded text-gray-300"><i class="fa-solid fa-coins ml-1"></i> عملة توضيحية</span></div>
                </div>
                <div class="kpi-dark rounded-xl p-4 flex flex-col justify-between shadow-md h-[160px]">
                    <div class="flex justify-between items-start"><span class="text-gray-300 text-sm font-bold">المدفوع</span><i class="fa-solid fa-hand-holding-dollar text-brand text-xl"></i></div>
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_paid) }}</span><i class="fa-solid fa-check-circle text-brand text-xl"></i></div>
                </div>
                <div class="kpi-dark rounded-xl p-4 flex flex-col justify-between shadow-md h-[160px]">
                    <div class="flex justify-between items-start"><span class="text-gray-300 text-sm font-bold">المعتمد</span><i class="fa-solid fa-user-check text-brand text-xl"></i></div>
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_approved) }}</span><i class="fa-solid fa-check-circle text-brand text-xl"></i></div>
                </div>
            </div>
            <div class="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                <div class="flex flex-wrap gap-3 items-end">
                    <div class="flex-1 min-w-[250px]"><div class="relative"><i class="fa-solid fa-magnifying-glass absolute right-3 top-3 text-gray-400"></i><input type="text" placeholder="بحث برقم المصروف أو البند أو المورد ..." class="w-full border border-gray-300 rounded-lg py-2.5 pr-10 pl-3 text-sm font-semibold focus:outline-none focus:border-brand"></div></div>
                    <div class="flex gap-2">
                        <button class="bg-brand text-white px-6 py-2.5 rounded-lg font-bold text-sm flex items-center gap-2 shadow-sm"><i class="fa-solid fa-filter"></i> تطبيق</button>
                        <button class="bg-white border border-gray-300 px-4 py-2.5 rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-gray-50"><i class="fa-solid fa-broom text-gray-500"></i> مسح الفلتر</button>
                    </div>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mt-3">
                    <select class="border border-gray-300 rounded-lg py-2.5 px-3 text-sm font-bold text-gray-700 bg-gray-50"><option>حالة الاعتماد: الكل</option></select>
                    <select class="border border-gray-300 rounded-lg py-2.5 px-3 text-sm font-bold text-gray-700 bg-gray-50"><option>حالة السداد: الكل</option></select>
                    <select class="border border-gray-300 rounded-lg py-2.5 px-3 text-sm font-bold text-gray-700 bg-gray-50"><option>العملة: عملة توضيحية</option></select>
                    <select class="border border-gray-300 rounded-lg py-2.5 px-3 text-sm font-bold text-gray-700 bg-gray-50"><option>الفترة: أكتوبر 2026</option></select>
                    <select class="border border-gray-300 rounded-lg py-2.5 px-3 text-sm font-bold text-gray-700 bg-gray-50"><option>الإدارة: الكل</option></select>
                </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table class="w-full text-right text-sm whitespace-nowrap">
                    <thead class="bg-gray-100 text-gray-600 font-extrabold border-b border-gray-200">
                        <tr>
                            <th class="py-3.5 px-4 w-12 text-center"><i class="fa-solid fa-list-ul"></i></th>
                            <th class="py-3.5 px-4">رقم المصروف</th><th class="py-3.5 px-4">التاريخ</th><th class="py-3.5 px-4">البند</th><th class="py-3.5 px-4">الإدارة</th><th class="py-3.5 px-4">المبلغ</th><th class="py-3.5 px-4 text-center">الاعتماد</th><th class="py-3.5 px-4 text-center">السداد</th><th class="py-3.5 px-4 text-center">المتبقي</th><th class="py-3.5 px-4 text-center">عرض</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                        {% for exp in expenses %}
                        <tr class="hover:bg-gray-50 transition-colors">
                            <td class="py-3.5 px-4 text-center"><i class="fa-regular fa-eye text-gray-400 hover:text-brand cursor-pointer text-lg"></i></td>
                            <td class="py-3.5 px-4 font-extrabold text-gray-800">{{ exp.expense_number }}</td>
                            <td class="py-3.5 px-4 text-gray-600 font-semibold">{{ exp.date }}</td>
                            <td class="py-3.5 px-4 text-gray-800 font-bold">{{ exp.item }}</td>
                            <td class="py-3.5 px-4 text-gray-600 font-semibold">{{ exp.department }}</td>
                            <td class="py-3.5 px-4 font-extrabold text-gray-800">{{ "{:,.0f}".format(exp.amount) }}</td>
                            <td class="py-3.5 px-4 text-center">
                                {% if exp.approval_status == 'معتمد' %}<span class="badge-green px-3 py-1.5 rounded-md text-xs font-bold">{{ exp.approval_status }}</span>
                                {% else %}<span class="badge-blue px-3 py-1.5 rounded-md text-xs font-bold">{{ exp.approval_status }}</span>{% endif %}
                            </td>
                            <td class="py-3.5 px-4 text-center">
                                {% if exp.payment_status == 'مدفوع جزئياً' %}<span class="badge-yellow px-3 py-1.5 rounded-md text-xs font-bold">{{ exp.payment_status }}</span>
                                {% else %}<span class="badge-red px-3 py-1.5 rounded-md text-xs font-bold">{{ exp.payment_status }}</span>{% endif %}
                            </td>
                            <td class="py-3.5 px-4 text-center font-extrabold text-gray-800">
                                {% if exp.remaining_amount > 0 %}{{ "{:,.0f}".format(exp.remaining_amount) }}{% else %}<span class="text-gray-400">—</span>{% endif %}
                            </td>
                            <td class="py-3.5 px-4 text-center"><button class="w-8 h-8 rounded-full bg-gray-100 text-gray-500 hover:bg-brand hover:text-white flex items-center justify-center mx-auto transition"><i class="fa-solid fa-eye"></i></button></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <div class="flex flex-col lg:flex-row justify-between items-center text-sm text-gray-600 py-2 font-bold gap-4">
                <div>عرض 6 من 16 مصروفاً <span class="mx-2 text-gray-300">|</span> عملة توضيحية <span class="mx-2 text-gray-300">|</span> دون تصفية</div>
                <div class="flex gap-1 bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
                    <button class="px-4 py-2 hover:bg-gray-50 border-l text-gray-600">&lt; السابق</button><button class="bg-brand text-white px-4 py-2">1</button><button class="px-4 py-2 hover:bg-gray-50 text-gray-600">التالي &gt;</button>
                </div>
            </div>
            <div class="bg-gray-200 border border-gray-300 p-3 rounded-lg text-sm font-bold text-gray-700 flex items-center justify-center gap-2"><i class="fa-solid fa-circle-info text-gray-500 text-lg"></i> جميع التعديلات من إدارة البيانات.</div>
        </div>
    </main>
</body>
</html>
"""'''

SERVER_CODE = '''import os
import sys
from flask import Flask, render_template_string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from importlib import import_module
db_module = import_module("1_database")
template_module = import_module("2_template")

app = Flask(__name__)

@app.route('/')
def index():
    expenses, stats = db_module.get_dashboard_data()
    return render_template_string(template_module.HTML_TEMPLATE, expenses=expenses, stats=stats)

if __name__ == '__main__':
    db_module.init_db()
    
    print("=========================================")
    print("المنصة جاهزة وتعمل الآن! افتح المتصفح على: http://127.0.0.1:5000")
    print("=========================================")
    app.run(debug=True, port=5000)
'''

def setup_project():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
        print(f"✅ تم إنشاء المجلد: {TARGET_DIR}")
    
    files = {
        "1_database.py": DB_CODE,
        "2_template.py": TEMPLATE_CODE,
        "3_server.py": SERVER_CODE
    }
    
    for filename, content in files.items():
        filepath = os.path.join(TARGET_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ تم إنشاء الملف: {filename}")

    print("⏳ جاري تثبيت مكتبة Flask...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    
    print("🚀 جاري تشغيل المنصة...")
    os.chdir(TARGET_DIR)
    subprocess.call([sys.executable, "3_server.py"])

if __name__ == "__main__":
    setup_project()