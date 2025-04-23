# School Management System

A comprehensive web-based School Management System built with Flask and SQLAlchemy that serves as a platform for schools to manage their administrative tasks and academic activities.

## Features

- Multi-school support
- Role-based access control (Super Admin, Admin, Teacher, Student, Parent)
- User management
- Subject and enrollment management
- Assignment and test creation
- Grade tracking
- Attendance tracking
- Schedule management
- Performance analytics

## Technical Stack

- **Backend Framework**: Flask (Python)
- **Database ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Password Hashing**: Bcrypt
- **Frontend**: HTML, CSS, JavaScript
- **Template Engine**: Jinja2
- **Database**: SQLite (for development), can be configured for PostgreSQL or MySQL

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/school-management-system.git
cd school-management-system
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set environment variables (optional):
```
export SECRET_KEY=your_secret_key
export SUPER_ADMIN_EMAIL=admin@example.com
export SUPER_ADMIN_PASSWORD=your_password
```

5. Run the application:
```
python run.py
```

6. Access the application at http://localhost:5007

## Default Super Admin Credentials

- Email: admin@schoolsystem.com
- Password: Admin123!

## Project Structure

- **/app**: Main application package
- **/app/models**: Database models
- **/app/views**: Blueprint-based route handlers
- **/app/templates**: HTML templates
- **/app/static**: CSS, JavaScript, and image assets
- **/app/utils**: Helper functions and decorators

## User Roles

1. **Super Admin**:
   - Creates and manages schools
   - Creates and manages school administrators
   - Views system-wide analytics

2. **Admin**:
   - School-specific administrator
   - Manages teachers, students, and parents
   - Creates and manages subjects and schedules
   - School-level reporting

3. **Teacher**:
   - Manages assignments and tests
   - Records grades
   - Takes attendance
   - Views student performance

4. **Student**:
   - Views enrolled subjects
   - Submits assignments
   - Takes tests
   - Views grades and attendance

5. **Parent**:
   - Links to children
   - Views children's academic information
   - Monitors grades and attendance

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name - Initial work