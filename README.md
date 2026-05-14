# 🏨 HostelHub — Hostel Management System

A full-featured, production-ready **Hostel Management System** built with Flask. HostelHub streamlines hostel operations with digital leave management, QR-based gate passes, real-time attendance tracking, and role-based dashboards for administrators, wardens, and students.

---

## ✨ Features

### 🔐 Authentication & Authorization
- Secure role-based authentication (Admin, Warden, Student)
- Case-insensitive email login with automatic normalization
- Password hashing with Werkzeug security
- Session management via Flask-Login
- Password reset via email

### 📋 Leave Management
- Students can submit leave requests with reason and date range
- Wardens can approve or reject requests with remarks
- Automatic QR code generation upon approval
- Printable PDF leave passes via `wkhtmltopdf`
- Complete leave history with status tracking

### 📱 QR Code Gate Pass
- Auto-generated QR codes for approved leaves
- Warden QR scanner for gate verification
- Download & print QR codes
- Real-time attendance logging on scan (entry/exit)

### 📊 Dashboards
- **Admin Dashboard** — System-wide stats, leave trend charts, status distribution, user management
- **Warden Dashboard** — Pending approvals, today's scans, student status overview
- **Student Dashboard** — Leave stats, quick actions, recent request history

### 🔔 Notifications
- Email notifications on leave approval/rejection (Gmail SMTP)
- SMS notifications via Twilio (optional)
- Configurable notification preferences

### ⚙️ Admin Panel
- User management (create, activate/deactivate, delete users)
- System settings (hostel name, max leave days, advance request period)
- Notification settings
- QR code configuration
- Reports with charts (leave trends, attendance data)
- Database backup & cleanup tools

---

## 🛠️ Tech Stack

| Layer        | Technology                                              |
| ------------ | ------------------------------------------------------- |
| **Backend**  | Flask 2.3, SQLAlchemy, Flask-Migrate, Flask-Login        |
| **Database** | PostgreSQL (with SQLite fallback)                        |
| **Frontend** | Custom CSS Design System (Inter font, no Bootstrap)      |
| **Icons**    | Hugeicons                                               |
| **Charts**   | Chart.js                                                |
| **QR Codes** | `qrcode` + Pillow                                       |
| **PDF**      | pdfkit + wkhtmltopdf                                    |
| **Email**    | Flask-Mail (Gmail SMTP)                                 |
| **SMS**      | Twilio                                                  |

---

## 📁 Project Structure

```
hostel-management-flask/
├── app.py                     # Application entry point
├── config.py                  # Configuration (env-based)
├── requirements.txt           # Python dependencies
├── scripts/
│   └── seed_db.py             # Database seeder with sample data
├── app/
│   ├── __init__.py            # App factory & extensions
│   ├── models/
│   │   ├── user.py            # User model (roles, auth)
│   │   ├── leave.py           # LeaveRequest model
│   │   ├── attendance.py      # Attendance/scan model
│   │   ├── notification.py    # Notification log model
│   │   └── settings.py        # System settings model
│   ├── routes/
│   │   ├── auth.py            # Login, register, password reset
│   │   ├── admin.py           # Admin dashboard, users, reports, settings
│   │   ├── warden.py          # Warden dashboard, approvals, attendance
│   │   ├── student.py         # Student dashboard, profile
│   │   ├── leave.py           # Leave request, history, print
│   │   ├── qr.py              # QR generation & scanning
│   │   └── main.py            # Landing page, public routes
│   ├── services/
│   │   ├── auth_service.py    # User creation & validation
│   │   ├── leave_service.py   # Leave approval logic + QR generation
│   │   ├── email_service.py   # Email notifications
│   │   ├── sms_service.py     # Twilio SMS notifications
│   │   ├── qr_service.py      # QR code utilities
│   │   └── dashboard_service.py # Dashboard data aggregation
│   ├── forms/                 # WTForms form classes
│   ├── templates/
│   │   ├── base.html          # Master layout (navbar + sidebar)
│   │   ├── landing.html       # Public landing page
│   │   ├── admin/             # Admin templates
│   │   ├── warden/            # Warden templates
│   │   ├── student/           # Student templates
│   │   ├── auth/              # Login, register, reset
│   │   ├── components/        # Reusable sidebar, etc.
│   │   └── errors/            # 404, 500 error pages
│   ├── static/
│   │   └── css/style.css      # Complete custom design system
│   └── utils/
│       └── decorators.py      # @role_required decorator
├── migrations/                # Flask-Migrate database migrations
└── tests/                     # Test directory
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** (or SQLite for quick testing)
- **wkhtmltopdf** — [Download here](https://wkhtmltopdf.org/downloads.html) (required for PDF leave passes)

### 1. Clone the Repository

```bash
git clone https://github.com/hemasp4/hostel_system.git
cd hostel_system
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/hostelhub

# Email (Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Twilio SMS (optional)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE=+1234567890
```

> **Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your account password.

### 5. Initialize the Database

```bash
# Create the PostgreSQL database first
# Then seed it with sample data:
python scripts/seed_db.py
```

### 6. Run the Application

```bash
python app.py
```

The app will be available at **http://localhost:5000**

---

## 🔑 Default Login Credentials

| Role       | Email                     | Password     |
| ---------- | ------------------------- | ------------ |
| **Admin**  | `admin@hostel.com`        | `admin123`   |
| **Warden** | `warden1@hostel.com`      | `warden123`  |
| **Warden** | `warden2@hostel.com`      | `warden123`  |
| **Student**| `hemabala492@gmail.com`   | `student123` |

> ⚠️ **Change these credentials immediately in production.**

---

## 📸 Screenshots

### Landing Page
Professional landing page with feature highlights and system statistics.

### Admin Dashboard
System-wide analytics with leave trend charts, status distribution, and recent activity table.

### Warden Dashboard
Pending approval queue, QR scanner access, and attendance overview.

### Student Dashboard
Leave statistics, quick actions, and request history with QR code download.

---

## 🔧 Configuration

### wkhtmltopdf Path

If PDF generation fails, update the binary path in `app/routes/leave.py`:

```python
# Windows
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# Linux
config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
```

### Database

The system supports both PostgreSQL and SQLite:

```env
# PostgreSQL (recommended)
DATABASE_URL=postgresql://user:pass@localhost/hostelhub

# SQLite (fallback)
# Simply remove DATABASE_URL from .env
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

