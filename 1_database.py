import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "expenses.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # استخدام ''' لجمل SQL آمنة
    cursor.execute('''
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
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            icon TEXT
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) FROM expenses")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('EX-0064', '29/10/2026', 'مستلزمات مكتبية', 'الإدارة المالية', 1200.0, 'معتمد', 'مدفوع جزئياً', 500.0),
            ('EX-0063', '28/10/2026', 'صيانة', 'الإدارة المالية', 800.0, 'معتمد', 'مدفوع جزئياً', 500.0),
            ('EX-0062', '27/10/2026', 'طباعة', 'الإدارة المالية', 450.0, 'بانتظار الاعتماد', 'غير مدفوع', 0.0),
            ('EX-0061', '25/10/2026', 'خدمات', 'الإدارة المالية', 4000.0, 'معتمد', 'مدفوع جزئياً', 1100.0),
            ('EX-0060', '26/10/2026', 'صيانة', 'الإدارة المالية', 7200.0, 'معتمد', 'مدفوع جزئياً', 1500.0),
            ('EX-0059', '20/10/2026', 'مستلزمات مكتبية', 'الإدارة المالية', 7800.0, 'معتمد', 'مدفوع جزئياً', 1500.0),
        ]
        cursor.executemany('''
            INSERT INTO expenses (expense_number, date, item, department, amount, approval_status, payment_status, remaining_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_data)
        
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cats = [
            ('مستلزمات مكتبية', 'fa-boxes-stacked'),
            ('صيانة', 'fa-screwdriver-wrench'),
            ('طباعة', 'fa-print'),
            ('خدمات', 'fa-network-wired'),
            ('سفر وانتقال', 'fa-plane'),
            ('ضيافة', 'fa-mug-hot')
        ]
        cursor.executemany("INSERT INTO categories (name, icon) VALUES (?, ?)", cats)
        
    conn.commit()
    conn.close()

def get_dashboard_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    expenses = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM categories")
    categories = [dict(row) for row in cursor.fetchall()]
    
    stats = {"total_approved": 0, "total_paid": 0, "total_remaining": 0, "pending_approval": 0, "overdue": 4}
    for e in expenses:
        if e['approval_status'] == 'معتمد':
            stats['total_approved'] += e['amount']
            stats['total_paid'] += (e['amount'] - e['remaining_amount'])
            stats['total_remaining'] += e['remaining_amount']
        if e['approval_status'] == 'بانتظار الاعتماد':
            stats['pending_approval'] += 1
            
    conn.close()
    return expenses, categories, stats

def add_expense(exp_num, date, item, dept, amount, app_status, pay_status, remaining):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (expense_number, date, item, department, amount, approval_status, payment_status, remaining_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exp_num, date, item, dept, amount, app_status, pay_status, remaining))
    conn.commit()
    conn.close()

def approve_expense(exp_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET approval_status = 'معتمد' WHERE id = ?", (exp_id,))
    conn.commit()
    conn.close()
