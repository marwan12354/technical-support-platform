HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام المصروفات التشغيلية</title>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {
            theme: { extend: { fontFamily: { sans: ['Tajawal', 'sans-serif'] }, colors: { brand: '#ea580c', dark: '#1e293b', bg: '#f8fafc' } } }
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
        .modal { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 50; align-items: center; justify-content: center; }
        .modal.active { display: flex; }
    </style>
</head>
<body class="flex h-screen overflow-hidden text-gray-800">
    <aside class="w-[260px] bg-dark text-gray-300 flex flex-col h-full shrink-0 shadow-lg">
        <div class="p-6 flex flex-col items-center border-b border-gray-700">
            <div class="bg-white p-3 rounded-lg mb-3 shadow-md"><i class="fa-solid fa-file-invoice-dollar text-3xl text-dark"></i></div>
            <h1 class="text-white font-bold text-lg text-center leading-tight">المصروفات<br>التشغيلية</h1>
        </div>
        <nav class="flex-1 py-4 space-y-1 px-3 text-sm font-bold overflow-y-auto">
            <a href="/" class="{% if active_page == 'home' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-house w-5 text-center"></i> الرئيسية</a>
            <a href="/data" class="{% if active_page == 'data' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-database w-5 text-center"></i> إدارة البيانات</a>
            <a href="/expenses" class="{% if active_page == 'expenses' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-file-lines w-5 text-center"></i> سجل المصروفات</a>
            <a href="/approvals" class="{% if active_page == 'approvals' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-check-double w-5 text-center"></i> الاعتماد والسداد</a>
            <a href="/items" class="{% if active_page == 'items' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-layer-group w-5 text-center"></i> بنود الصرف</a>
            <a href="/reports" class="{% if active_page == 'reports' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-chart-pie w-5 text-center"></i> التقارير</a>
            <a href="/settings" class="{% if active_page == 'settings' %}nav-active{% else %}nav-item{% endif %} flex items-center gap-4 px-4 py-3 rounded-lg transition"><i class="fa-solid fa-gear w-5 text-center"></i> الإعدادات</a>
        </nav>
    </aside>
    
    <main class="flex-1 overflow-y-auto">
        <header class="bg-white px-6 py-4 flex justify-between items-center border-b sticky top-0 z-10 shadow-sm">
            <div>
                <h2 class="text-2xl font-extrabold text-gray-800">
                    {% if active_page == 'home' %}لوحة القيادة والمعلومات
                    {% elif active_page == 'data' %}مركز إدارة البيانات
                    {% elif active_page == 'expenses' %}سجل المصروفات
                    {% elif active_page == 'approvals' %}مركز الاعتماد والسداد
                    {% elif active_page == 'items' %}دليل بنود الصرف
                    {% elif active_page == 'reports' %}التقارير التحليلية
                    {% elif active_page == 'settings' %}إعدادات النظام
                    {% endif %}
                </h2>
                <p class="text-sm text-gray-500 mt-1 font-semibold">بيانات توضيحية | حتى 02/11/2026</p>
            </div>
            {% if active_page == 'expenses' %}
            <button onclick="document.getElementById('addModal').classList.add('active')" class="bg-brand text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-orange-700 shadow-sm transition"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
            {% endif %}
        </header>

        <div class="p-6 space-y-6 max-w-[1400px] mx-auto">
            {% if active_page == 'home' %}
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="bg-white p-4 rounded-xl shadow-sm border-r-4 border-brand">
                        <p class="text-gray-500 text-sm font-bold">إجمالي المصروفات المعتمدة</p>
                        <p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_approved) }}</p>
                    </div>
                    <div class="bg-white p-4 rounded-xl shadow-sm border-r-4 border-green-500">
                        <p class="text-gray-500 text-sm font-bold">المبلغ المدفوع</p>
                        <p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_paid) }}</p>
                    </div>
                    <div class="bg-white p-4 rounded-xl shadow-sm border-r-4 border-blue-500">
                        <p class="text-gray-500 text-sm font-bold">المتبقي للدفع</p>
                        <p class="text-3xl font-extrabold text-gray-800 mt-2">{{ "{:,.0f}".format(stats.total_remaining) }}</p>
                    </div>
                    <div class="bg-white p-4 rounded-xl shadow-sm border-r-4 border-red-500">
                        <p class="text-gray-500 text-sm font-bold">طلبات بانتظار الاعتماد</p>
                        <p class="text-3xl font-extrabold text-gray-800 mt-2">{{ stats.pending_approval }}</p>
                    </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 class="font-bold text-lg mb-4">نظرة عامة على الأداء المالي</h3>
                        <canvas id="mainChart"></canvas>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 class="font-bold text-lg mb-4">أحدث العمليات</h3>
                        <ul class="space-y-3">
                            {% for exp in expenses[:4] %}
                            <li class="flex justify-between items-center border-b pb-2">
                                <div><span class="font-bold block">{{ exp.item }}</span><span class="text-xs text-gray-500">{{ exp.date }}</span></div>
                                <span class="font-bold text-gray-700">{{ exp.amount }}</span>
                            </li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                <script>
                    new Chart(document.getElementById('mainChart'), {
                        type: 'bar',
                        data: { labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو'], datasets: [{ label: 'المصروفات', data: [12000, 19000, 15000, 22000, 24800], backgroundColor: '#ea580c' }] }
                    });
                </script>

            {% elif active_page == 'data' %}
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <h3 class="font-bold border-b pb-2 mb-4"><i class="fa-solid fa-sitemap text-brand"></i> الهيكل التنظيمي</h3>
                        <ul class="list-disc list-inside text-gray-600 space-y-2">
                            <li>الإدارة المالية العامة</li>
                            <li>إدارة الموارد البشرية</li>
                            <li>إدارة تقنية المعلومات</li>
                            <li>إدارة المشتريات</li>
                        </ul>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <h3 class="font-bold border-b pb-2 mb-4"><i class="fa-solid fa-user-shield text-brand"></i> الأدوار والصلاحيات</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between bg-gray-50 p-2 rounded"><span>مدير النظام</span><span class="text-green-600 font-bold">كامل</span></div>
                            <div class="flex justify-between bg-gray-50 p-2 rounded"><span>مدير مالي</span><span class="text-blue-600 font-bold">اعتماد</span></div>
                            <div class="flex justify-between bg-gray-50 p-2 rounded"><span>محاسب</span><span class="text-yellow-600 font-bold">إدخال</span></div>
                        </div>
                    </div>
                </div>

            {% elif active_page == 'expenses' %}
                <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
                    <table class="w-full text-right text-sm whitespace-nowrap">
                        <thead class="bg-gray-100 font-bold border-b">
                            <tr>
                                <th class="py-3 px-4 text-center">رقم</th>
                                <th class="py-3 px-4">التاريخ</th>
                                <th class="py-3 px-4">البند</th>
                                <th class="py-3 px-4">الإدارة</th>
                                <th class="py-3 px-4">المبلغ</th>
                                <th class="py-3 px-4 text-center">الاعتماد</th>
                                <th class="py-3 px-4 text-center">السداد</th>
                                <th class="py-3 px-4 text-center">المتبقي</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100">
                            {% for exp in expenses %}
                            <tr class="hover:bg-gray-50">
                                <td class="py-3 px-4 font-bold text-gray-800">{{ exp.expense_number }}</td>
                                <td class="py-3 px-4 text-gray-600">{{ exp.date }}</td>
                                <td class="py-3 px-4 font-bold">{{ exp.item }}</td>
                                <td class="py-3 px-4 text-gray-600">{{ exp.department }}</td>
                                <td class="py-3 px-4 font-bold text-gray-800">{{ exp.amount }}</td>
                                <td class="py-3 px-4 text-center"><span class="{{ 'badge-green' if exp.approval_status == 'معتمد' else 'badge-blue' }} px-2 py-1 rounded text-xs font-bold">{{ exp.approval_status }}</span></td>
                                <td class="py-3 px-4 text-center"><span class="{{ 'badge-yellow' if exp.payment_status == 'مدفوع جزئياً' else 'badge-red' }} px-2 py-1 rounded text-xs font-bold">{{ exp.payment_status }}</span></td>
                                <td class="py-3 px-4 text-center font-bold">{{ exp.remaining_amount }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

            {% elif active_page == 'approvals' %}
                <div class="bg-white rounded-xl shadow-sm border p-6">
                    <h3 class="font-bold text-lg mb-4 text-brand"><i class="fa-solid fa-clock"></i> بانتظار الاعتماد</h3>
                    <table class="w-full text-right text-sm">
                        <tbody>
                            {% for exp in expenses if exp.approval_status == 'بانتظار الاعتماد' %}
                            <tr class="border-b">
                                <td class="py-3 font-bold">{{ exp.expense_number }} - {{ exp.item }}</td>
                                <td class="py-3 font-bold text-red-500">{{ exp.amount }}</td>
                                <td class="py-3 text-left">
                                    <a href="/approve/{{ exp.id }}" class="bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600">اعتماد</a>
                                </td>
                            </tr>
                            {% else %}
                            <tr><td colspan="3" class="py-6 text-center text-gray-500 font-bold">لا توجد طلبات معلقة.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

            {% elif active_page == 'items' %}
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {% for cat in categories %}
                    <div class="bg-white p-6 rounded-xl shadow-sm border text-center hover:shadow-md cursor-pointer transition">
                        <i class="fa-solid {{ cat.icon }} text-4xl text-brand mb-3"></i>
                        <h4 class="font-bold">{{ cat.name }}</h4>
                    </div>
                    {% endfor %}
                </div>

            {% elif active_page == 'reports' %}
                <div class="bg-white p-6 rounded-xl shadow-sm border">
                    <h3 class="font-bold text-lg mb-4">توزيع المصروفات حسب الإدارة</h3>
                    <div class="w-1/2 mx-auto"><canvas id="reportChart"></canvas></div>
                </div>
                <script>
                    new Chart(document.getElementById('reportChart'), {
                        type: 'pie',
                        data: { labels: ['الإدارة المالية', 'الموارد البشرية', 'تقنية المعلومات'], datasets: [{ data: [30000, 15000, 20000], backgroundColor: ['#ea580c', '#3b82f6', '#10b981'] }] }
                    });
                </script>

            {% elif active_page == 'settings' %}
                <div class="bg-white p-8 rounded-xl shadow-sm border max-w-2xl">
                    <h3 class="font-bold text-xl mb-6 border-b pb-2">الإعدادات العامة</h3>
                    <div class="space-y-4">
                        <div><label class="block font-bold mb-1">اسم المؤسسة</label><input type="text" value="مؤسسة الدعم التقني" class="w-full border p-2 rounded bg-gray-50"></div>
                        <div><label class="block font-bold mb-1">العملة الأساسية</label><select class="w-full border p-2 rounded bg-gray-50"><option>ريال سعودي (SAR)</option><option>دولار (USD)</option></select></div>
                        <div><label class="block font-bold mb-1">البريد الإلكتروني للتنبيهات</label><input type="email" value="admin@support.com" class="w-full border p-2 rounded bg-gray-50"></div>
                        <button class="bg-brand text-white px-6 py-2 rounded font-bold mt-4">حفظ التغييرات</button>
                    </div>
                </div>
            {% endif %}
        </div>
    </main>

    {% if active_page == 'expenses' %}
    <div id="addModal" class="modal">
        <div class="bg-white rounded-xl shadow-2xl w-[500px] p-6 relative">
            <button onclick="document.getElementById('addModal').classList.remove('active')" class="absolute top-4 left-4 text-gray-500 hover:text-red-500"><i class="fa-solid fa-xmark text-xl"></i></button>
            <h3 class="text-xl font-bold mb-4 border-b pb-2">إضافة مصروف جديد</h3>
            <form action="/add" method="POST" class="space-y-4">
                <div><label class="block text-sm font-bold mb-1">البند</label><input type="text" name="item" required class="w-full border p-2 rounded"></div>
                <div class="grid grid-cols-2 gap-4">
                    <div><label class="block text-sm font-bold mb-1">المبلغ</label><input type="number" name="amount" required class="w-full border p-2 rounded"></div>
                    <div><label class="block text-sm font-bold mb-1">الإدارة</label><select name="department" class="w-full border p-2 rounded"><option>الإدارة المالية</option><option>الموارد البشرية</option><option>تقنية المعلومات</option></select></div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div><label class="block text-sm font-bold mb-1">الاعتماد</label><select name="approval_status" class="w-full border p-2 rounded"><option value="بانتظار الاعتماد">بانتظار الاعتماد</option><option value="معتمد">معتمد</option></select></div>
                    <div><label class="block text-sm font-bold mb-1">السداد</label><select name="payment_status" class="w-full border p-2 rounded"><option value="غير مدفوع">غير مدفوع</option><option value="مدفوع">مدفوع</option></select></div>
                </div>
                <button type="submit" class="w-full bg-brand text-white font-bold py-2 rounded mt-2">حفظ</button>
            </form>
        </div>
    </div>
    {% endif %}
</body>
</html>
'''
