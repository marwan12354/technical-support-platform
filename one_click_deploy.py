# one_click_deploy.py (النسخة النهائية - Force Push)
import os
import subprocess
import sys
import webbrowser
import time

PROJECT_DIR = r"C:\Users\PC\Downloads\مشروع منصة الدعم التقني\itsupport\ghg"
GITHUB_REPO = "https://github.com/marwan12354/technical-support-platform"

REQUIREMENTS = """Flask==3.0.3
Flask-SQLAlchemy==3.1.1
gunicorn==22.0.0
"""

RENDER_YAML = """services:
  - type: web
    name: technical-support-platform
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    plan: free
"""

PROCFILE = "web: gunicorn app:app"

GITIGNORE = """__pycache__/
*.pyc
*.db
expenses.db
.venv/
venv/
.env
"""

def create_deployment_files():
    print("⏳ 1. جاري إنشاء ملفات النشر...")
    files = {
        "requirements.txt": REQUIREMENTS,
        "render.yaml": RENDER_YAML,
        "Procfile": PROCFILE,
        ".gitignore": GITIGNORE
    }
    for filename, content in files.items():
        filepath = os.path.join(PROJECT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"   ✅ تم إنشاء/تحديث: {filename}")

def push_to_github():
    print("\n⏳ 2. جاري تهيئة Git ورفع التحديثات إلى GitHub...")
    os.chdir(PROJECT_DIR)
    
    try:
        # 1. تعريف هوية Git محلياً
        subprocess.run(["git", "config", "user.email", "marwan12354@users.noreply.github.com"], check=True)
        subprocess.run(["git", "config", "user.name", "marwan12354"], check=True)

        # 2. تهيئة المستودع إذا لم يكن موجوداً
        if not os.path.exists(os.path.join(PROJECT_DIR, ".git")):
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            subprocess.run(["git", "remote", "add", "origin", GITHUB_REPO], check=True)
        else:
            subprocess.run(["git", "remote", "set-url", "origin", GITHUB_REPO], check=True)

        # 3. إضافة الملفات وعمل Commit
        subprocess.run(["git", "add", "."], check=True)
        # استخدام check=False للـ commit لتجنب الخطأ إذا لم تكن هناك تغييرات
        subprocess.run(["git", "commit", "-m", "Auto-configured for deployment on Render"], check=False)
        
        # 4. الرفع باستخدام --force لتجاوز اختلاف الملفات (History Mismatch)
        print("   ⏳ جاري الدفع (Force Push) إلى GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
        
        print("   ✅ تم رفع الملفات بنجاح إلى GitHub!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ حدث خطأ أثناء الرفع: {e}")
        return False

def open_render():
    print("\n🚀 3. جاري فتح منصة Render لإنشاء الخدمة...")
    render_url = "https://dashboard.render.com/select-repo?type=web"
    webbrowser.open(render_url)
    
    print("\n" + "="*60)
    print("🎉 اكتمل التجهيز! اتبع الخطوات الأخيرة في المتصفح:")
    print("1. اختر مستودعك: technical-support-platform")
    print("2. سيكتشف Render إعداداتك تلقائياً من ملف render.yaml.")
    print("3. اضغط على زر (Create Web Service).")
    print("4. انتظر دقيقتين، وسيظهر لك رابط المنصة (xxxx.onrender.com).")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("🌟 المايسترو: نشر المنصة على الإنترنت (Render)")
    print("="*60)
    
    if not os.path.exists(PROJECT_DIR):
        print(f"❌ خطأ: المسار غير موجود: {PROJECT_DIR}")
        sys.exit(1)
        
    create_deployment_files()
    success = push_to_github()
    
    if success:
        time.sleep(1)
        open_render()
    else:
        print("\n❌ لم يتم فتح Render بسبب فشل عملية الرفع.")