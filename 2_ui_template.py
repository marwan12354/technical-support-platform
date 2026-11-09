# 2_ui_template.py
HTML_TEMPLATE = """
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
            <a href="/" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-house w-5 text-center"></i> الرئيسية</a>
            <a href="/" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-database w-5 text-center"></i> إدارة البيانات</a>
            <a href="/" class="flex items-center gap-4 px-4 py-3 nav-active shadow-md"><i class="fa-solid fa-file-lines w-5 text-center"></i> سجل المصروفات</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-check-double w-5 text-center"></i> الاعتماد والسداد</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-layer-group w-5 text-center"></i> بنود الصرف</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-chart-pie w-5 text-center"></i> التقارير</a>
            <a href="#" class="flex items-center gap-4 px-4 py-3 nav-item rounded-lg transition"><i class="fa-solid fa-gear w-5 text-center"></i> الإعدادات</a>
        </nav>
    </aside>
    <main class="flex-1 overflow-y-auto">
        <header class="bg-white px-6 py-4 flex justify-between items-center border-b sticky top-0 z-10 shadow-sm">
            <div>
                <h2 class="text-2xl font-extrabold text-gray-800">سجل المصروفات</h2>
                <p class="text-sm text-gray-500 mt-1 font-semibold">بيانات توضيحية | حتى 02/11/2026</p>
            </div>
            <div class="flex items-center gap-3">
                <button onclick="document.getElementById('addModal').classList.add('active')" class="bg-brand text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 hover:bg-orange-700 shadow-sm transition"><i class="fa-solid fa-plus"></i> مصروف جديد</button>
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
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_remaining) }}</span></div>
                </div>
                <div class="kpi-dark rounded-xl p-4 flex flex-col justify-between shadow-md h-[160px]">
                    <div class="flex justify-between items-start"><span class="text-gray-300 text-sm font-bold">المدفوع</span><i class="fa-solid fa-hand-holding-dollar text-brand text-xl"></i></div>
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_paid) }}</span></div>
                </div>
                <div class="kpi-dark rounded-xl p-4 flex flex-col justify-between shadow-md h-[160px]">
                    <div class="flex justify-between items-start"><span class="text-gray-300 text-sm font-bold">المعتمد</span><i class="fa-solid fa-user-check text-brand text-xl"></i></div>
                    <div class="flex justify-between items-end mt-4"><span class="text-3xl font-extrabold">{{ "{:,.0f}".format(stats.total_approved) }}</span></div>
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
                                {% if exp.approval_status == 'معتمد' %}<span class="badge-green px-3 py-1.5 rounded-md text-xs font-bold">معتمد</span>
                                {% else %}<span class="badge-blue px-3 py-1.5 rounded-md text-xs font-bold">بانتظار الاعتماد</span>{% endif %}
                            </td>
                            <td class="py-3.5 px-4 text-center">
                                {% if exp.payment_status == 'مدفوع جزئياً' %}<span class="badge-yellow px-3 py-1.5 rounded-md text-xs font-bold">مدفوع جزئياً</span>
                                {% else %}<span class="badge-red px-3 py-1.5 rounded-md text-xs font-bold">غير مدفوع</span>{% endif %}
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
        </div>
    </main>
    <div id="addModal" class="modal">
        <div class="bg-white rounded-xl shadow-2xl w-[500px] p-6 relative">
            <button onclick="document.getElementById('addModal').classList.remove('active')" class="absolute top-4 left-4 text-gray-500 hover:text-red-500"><i class="fa-solid fa-xmark text-xl"></i></button>
            <h3 class="text-xl font-bold mb-4 text-gray-800 border-b pb-2">إضافة مصروف جديد</h3>
            <form action="/add" method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm font-bold text-gray-700 mb-1">رقم المصروف</label>
                    <input type="text" name="expense_number" value="EX-00{{ next_id }}" readonly class="w-full bg-gray-100 border rounded-lg p-2 font-bold text-gray-500">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div><label class="block text-sm font-bold text-gray-700 mb-1">البند</label><input type="text" name="item" required class="w-full border rounded-lg p-2 focus:border-brand outline-none"></div>
                    <div><label class="block text-sm font-bold text-gray-700 mb-1">المبلغ</label><input type="number" name="amount" required class="w-full border rounded-lg p-2 focus:border-brand outline-none"></div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div><label class="block text-sm font-bold text-gray-700 mb-1">حالة الاعتماد</label><select name="approval_status" class="w-full border rounded-lg p-2"><option value="معتمد">معتمد</option><option value="بانتظار الاعتماد">بانتظار الاعتماد</option></select></div>
                    <div><label class="block text-sm font-bold text-gray-700 mb-1">حالة السداد</label><select name="payment_status" class="w-full border rounded-lg p-2"><option value="مدفوع">مدفوع</option><option value="مدفوع جزئياً">مدفوع جزئياً</option><option value="غير مدفوع">غير مدفوع</option></select></div>
                </div>
                <div class="pt-4 flex gap-2"><button type="submit" class="flex-1 bg-brand text-white font-bold py-2 rounded-lg hover:bg-orange-700 transition">حفظ المصروف</button></div>
            </form>
        </div>
    </div>
</body>
</html>
"""