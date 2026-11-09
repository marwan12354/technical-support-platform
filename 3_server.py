import os
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
    content = templates.__dict__.get(content_block, "").replace("{% extends "base" %}", "")
    
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
            
    content = templates.HOME_HTML.replace("{% extends "base" %}", "").replace("{% block page_title %}لوحة القيادة{% endblock %}", "").replace("{% block content %}", "").replace("{% endblock %}", "")
    return render_template_string(templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", "لوحة القيادة").replace("{% block content %}{% endblock %}", content), expenses=expenses, latest_expenses=expenses[:4], stats=stats, active_page='home')

@app.route('/expenses')
def expenses_page():
    expenses = models.Expense.query.order_by(models.Expense.id.desc()).all()
    categories = models.Category.query.all()
    
    content = templates.EXPENSES_HTML.replace("{% extends "base" %}", "").replace("{% block page_title %}سجل المصروفات{% endblock %}", "").replace("{% block header_actions %}", "").replace("{% endblock %}", "")
    
    return render_template_string(templates.BASE_HTML.replace("{% block page_title %}{% endblock %}", "سجل المصروفات").replace("{% block header_actions %}{% endblock %}", "").replace("{% block content %}{% endblock %}", content), expenses=expenses, categories=categories, active_page='expenses')

@app.route('/categories')
def categories_page():
    categories = models.Category.query.all()
    content = templates.CATEGORIES_HTML.replace("{% extends "base" %}", "").replace("{% block page_title %}بنود الصرف{% endblock %}", "").replace("{% block content %}", "").replace("{% endblock %}", "")
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
