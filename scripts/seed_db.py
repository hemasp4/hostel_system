import sys
import os

# Add the project root to sys.path so 'app' module can be found
# Works whether you run from project root OR from scripts/ subfolder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.leave import LeaveRequest
from datetime import datetime, timedelta

app = create_app()

def seed_database():
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating tables...")
        db.create_all()

        # ── Admin ──────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@hostel.com",
            phone="1234567890",
            role="admin",
            is_active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        print("  [+] Admin created: admin@hostel.com / admin123")

        # ── Wardens ────────────────────────────────────────
        warden1 = User(
            name="John Warden",
            email="warden1@hostel.com",
            phone="1234567891",
            role="warden",
            is_active=True
        )
        warden1.set_password("warden123")
        db.session.add(warden1)
        print("  [+] Warden created: warden1@hostel.com / warden123")

        warden2 = User(
            name="Jane Warden",
            email="warden2@hostel.com",
            phone="1234567892",
            role="warden",
            is_active=True
        )
        warden2.set_password("warden123")
        db.session.add(warden2)
        print("  [+] Warden created: warden2@hostel.com / warden123")

        # ── Students ───────────────────────────────────────
        student = User(
            name="Hemabala",
            email="hemabala492@gmail.com",
            phone="7339660663",
            role="student",
            is_active=True
        )
        student.set_password("student123")
        db.session.add(student)
        print("  [+] Student created: Hemabala492@gmail.com / student123")

        db.session.commit()
        print("\nUsers committed.")

        # ── Sample Leave Requests ──────────────────────────
        leave = LeaveRequest(
            student_id=student.id,
            reason="Family function - need to attend sister's wedding",
            start_date=datetime.today().date() + timedelta(days=1),
            end_date=datetime.today().date() + timedelta(days=3),
            status="pending"
        )
        db.session.add(leave)
        db.session.commit()
        print("  [+] Sample leave request created for Hemabala")

        print("\n✅ Database seeded successfully!")
        print("\n──────────────── LOGIN CREDENTIALS ─────────────────")
        print("  ADMIN  : admin@hostel.com      / admin123")
        print("  WARDEN : warden1@hostel.com    / warden123")
        print("  WARDEN : warden2@hostel.com    / warden123")
        print("  STUDENT: hemabala492@gmail.com / student123")
        print("─────────────────────────────────────────────────────")

if __name__ == "__main__":
    seed_database()
