from app import create_app, db
from app.models.user import User
import getpass

app = create_app()

def create_admin():
    with app.app_context():
        print("Create Admin User")
        print("-" * 30)
        
        name = input("Enter admin name: ")
        email = input("Enter admin email: ")
        phone = input("Enter admin phone: ")
        password = getpass.getpass("Enter admin password: ")
        
        # Check if admin already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            print(f"User with email {email} already exists!")
            return
        
        # Create admin user
        admin = User(
            name=name,
            email=email,
            phone=phone,
            role="admin"
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user '{name}' created successfully!")

if __name__ == "__main__":
    create_admin()
