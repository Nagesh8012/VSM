from django.urls import path

from . import api


urlpatterns = [
    path("signup/", api.signup, name="api-staff-signup"),
    path("dashboard/", api.dashboard, name="api-staff-dashboard"),
    path("profile/", api.profile, name="api-staff-profile"),
    path("work/", api.work_assigned, name="api-staff-work"),
    path("work/<int:pk>/status/", api.update_work_status, name="api-staff-work-status"),
    path("attendance/", api.attendance, name="api-staff-attendance"),
    path("salary/", api.salary, name="api-staff-salary"),
    path("feedback/", api.feedback, name="api-staff-feedback"),
]

