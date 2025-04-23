# Import all forms for easy access
from app.forms.auth_forms import LoginForm, PasswordChangeForm
from app.forms.super_admin_forms import SchoolForm, AdminUserForm
from app.forms.admin_forms import UserForm, SubjectForm, ScheduleForm, ScheduleItemForm
from app.forms.teacher_forms import AssignmentForm, TestForm, GradeForm, AttendanceForm
from app.forms.student_forms import AssignmentSubmissionForm