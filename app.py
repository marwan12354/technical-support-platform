import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Expense, Department, Category
from database import init_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-here'
# استخدام متغير البيئة DATABASE_URL إذا وجد (للاستضافة)، وإلا استخدام SQLite المحلي
db_path = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'expenses.db'))
if db_path.startswith("postgres://"):
    db_path = db_path.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# [هام جداً] تهيئة قاعدة البيانات هنا لتعمل مع Gunicorn على Render
with app.app_context():
    init_database(app)

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
    app.run(debug=True, use_reloader=False, port=5000)
