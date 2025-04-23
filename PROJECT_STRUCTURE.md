# Project Structure

```
School Management System/
│
├── app/                            # Main application package
│   ├── __init__.py                 # App initialization and config
│   │
│   ├── models/                     # Database models
│   │   ├── __init__.py
│   │   ├── user.py                 # User and Role models
│   │   ├── school.py               # School model
│   │   ├── subject.py              # Subject model
│   │   ├── schedule.py             # Schedule models
│   │   ├── assignment.py           # Assignment models
│   │   ├── test.py                 # Test model
│   │   ├── grade.py                # Grade model
│   │   └── attendance.py           # Attendance model
│   │
│   ├── views/                      # Blueprint-based route handlers
│   │   ├── __init__.py
│   │   ├── main.py                 # Public routes
│   │   ├── auth.py                 # Authentication routes
│   │   ├── super_admin.py          # Super admin routes
│   │   ├── admin.py                # Admin routes
│   │   ├── teacher.py              # Teacher routes
│   │   ├── student.py              # Student routes
│   │   └── parent.py               # Parent routes
│   │
│   ├── templates/                  # HTML templates
│   │   ├── base.html               # Base template
│   │   ├── errors/                 # Error templates
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   ├── main/                   # Main public templates
│   │   │   ├── index.html
│   │   │   ├── about.html
│   │   │   └── contact.html
│   │   ├── auth/                   # Authentication templates
│   │   │   ├── login.html
│   │   │   └── change_password.html
│   │   ├── super_admin/            # Super admin templates
│   │   │   ├── dashboard.html
│   │   │   ├── schools/
│   │   │   └── admins/
│   │   ├── admin/                  # Admin templates
│   │   │   ├── dashboard.html
│   │   │   ├── teachers/
│   │   │   ├── students/
│   │   │   ├── subjects/
│   │   │   └── schedules/
│   │   ├── teacher/                # Teacher templates
│   │   │   ├── dashboard.html
│   │   │   ├── subjects/
│   │   │   ├── assignments/
│   │   │   ├── tests/
│   │   │   ├── grades/
│   │   │   └── attendance/
│   │   ├── student/                # Student templates
│   │   │   ├── dashboard.html
│   │   │   ├── subjects/
│   │   │   ├── assignments/
│   │   │   ├── tests/
│   │   │   ├── grades/
│   │   │   └── attendance/
│   │   └── parent/                 # Parent templates
│   │       ├── dashboard.html
│   │       └── children/
│   │
│   ├── static/                     # Static assets
│   │   ├── css/
│   │   │   └── style.css           # Custom CSS
│   │   ├── js/
│   │   │   └── main.js             # Custom JS
│   │   └── img/
│   │       └── hero-image.svg      # Images
│   │
│   ├── forms/                      # WTForms
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── super_admin_forms.py
│   │   ├── admin_forms.py
│   │   ├── teacher_forms.py
│   │   └── student_forms.py
│   │
│   └── utils/                      # Helper functions and decorators
│       ├── __init__.py
│       ├── access_control.py       # Role-based access control
│       └── seeder.py               # Database seeding
│
├── run.py                          # Application entry point
├── requirements.txt                # Dependencies
├── README.md                       # Project documentation
└── PROJECT_STRUCTURE.md            # This file
```