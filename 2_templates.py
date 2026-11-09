# القوالب المطورة باستخدام Jinja2 + Alpine.js

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
