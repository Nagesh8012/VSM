from django.contrib.auth.views import LoginView
from django.urls import path

from . import views


urlpatterns = [
    path("staffclick", views.staffclick_view),
    path("staffsignup", views.staff_signup_view, name="staffsignup"),
    path("stafflogin", LoginView.as_view(template_name="staff/stafflogin.html"), name="stafflogin"),
    path("staff-dashboard", views.staff_dashboard_view, name="staff-dashboard"),
    path("staff-work-assigned", views.staff_work_assigned_view, name="staff-work-assigned"),
    path("staff-update-status/<int:pk>", views.staff_update_status_view, name="staff-update-status"),
    path("staff-feedback", views.staff_feedback_view, name="staff-feedback"),
    path("staff-salary", views.staff_salary_view, name="staff-salary"),
    path("staff-profile", views.staff_profile_view, name="staff-profile"),
    path("edit-staff-profile", views.edit_staff_profile_view, name="edit-staff-profile"),
    path("staff-attendance", views.staff_attendance_view, name="staff-attendance"),
]

