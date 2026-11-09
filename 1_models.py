from flask_sqlalchemy import SQLAlchemy
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
