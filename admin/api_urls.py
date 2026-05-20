from django.urls import path

from . import api


urlpatterns = [
    path("dashboard/", api.dashboard, name="api-admin-dashboard"),
    path("customers/", api.customers, name="api-admin-customers"),
    path("customers/<int:pk>/", api.customer_detail, name="api-admin-customer-detail"),
    path("staff/", api.staff_members, name="api-admin-staff"),
    path("staff/<int:pk>/", api.staff_detail, name="api-admin-staff-detail"),
    path("staff/<int:pk>/approve/", api.approve_staff, name="api-admin-approve-staff"),
    path("requests/", api.service_requests, name="api-admin-requests"),
    path("requests/<int:pk>/", api.service_request_detail, name="api-admin-request-detail"),
    path("attendance/", api.attendance, name="api-admin-attendance"),
    path("feedback/", api.feedback, name="api-admin-feedback"),
    path("reports/", api.reports, name="api-admin-reports"),
]

