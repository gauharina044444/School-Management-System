from app.models.user import User, Role
from app.models.school import School
from app.models.subject import Subject
from app.models.schedule import Schedule, ScheduleItem
from app.models.assignment import Assignment, AssignmentSubmission
from app.models.test import Test
from app.models.grade import Grade
from app.models.attendance import Attendance

# Import association tables for reference
from app.models.user import user_roles, parent_student, teacher_subject, subject_enrollment