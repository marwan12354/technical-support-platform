from models import db, Department, Category, Expense

def init_database(app):
    with app.app_context():
        # إنشاء الجداول إذا لم تكن موجودة (بدون حذف البيانات)
        db.create_all()
        
        if Department.query.count() == 0:
            db.session.add_all([
                Department(name='الإدارة المالية'),
                Department(name='الموارد البشرية'),
                Department(name='تقنية المعلومات'),
                Department(name='المشتريات')
            ])
            db.session.commit()
            
        if Category.query.count() == 0:
            db.session.add_all([
                Category(name='مستلزمات مكتبية', icon='fa-boxes-stacked'),
                Category(name='صيانة', icon='fa-screwdriver-wrench'),
                Category(name='طباعة', icon='fa-print'),
                Category(name='خدمات', icon='fa-network-wired'),
                Category(name='سفر وانتقال', icon='fa-plane')
            ])
            db.session.commit()
        
        if Expense.query.count() == 0:
            dept = Department.query.filter_by(name='الإدارة المالية').first()
            db.session.add_all([
                Expense(expense_number='EX-0064', date='29/10/2026', item='مستلزمات مكتبية', department_id=dept.id, amount=1200.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0063', date='28/10/2026', item='صيانة', department_id=dept.id, amount=800.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=500.0),
                Expense(expense_number='EX-0062', date='27/10/2026', item='طباعة', department_id=dept.id, amount=450.0, approval_status='بانتظار الاعتماد', payment_status='غير مدفوع', remaining_amount=0.0),
                Expense(expense_number='EX-0061', date='25/10/2026', item='خدمات', department_id=dept.id, amount=4000.0, approval_status='معتمد', payment_status='مدفوع جزئياً', remaining_amount=1100.0),
            ])
            db.session.commit()
