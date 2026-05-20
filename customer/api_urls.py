from django.urls import path

from . import api


urlpatterns = [
    path("signup/", api.signup, name="api-customer-signup"),
    path("dashboard/", api.dashboard, name="api-customer-dashboard"),
    path("profile/", api.profile, name="api-customer-profile"),
    path("requests/", api.requests, name="api-customer-requests"),
    path("requests/<int:pk>/", api.request_detail, name="api-customer-request-detail"),
    path("approved-requests/", api.approved_requests, name="api-customer-approved-requests"),
    path("invoices/", api.invoices, name="api-customer-invoices"),
    path("feedback/", api.feedback, name="api-customer-feedback"),
]

