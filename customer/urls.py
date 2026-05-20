from django.contrib.auth.views import LoginView
from django.urls import path

from . import views


urlpatterns = [
    path("customerclick", views.customerclick_view),
    path("customersignup", views.customer_signup_view, name="customersignup"),
    path("customerlogin", LoginView.as_view(template_name="customer/customerlogin.html"), name="customerlogin"),
    path("customer-dashboard", views.customer_dashboard_view, name="customer-dashboard"),
    path("customer-request", views.customer_request_view, name="customer-request"),
    path("customer-add-request", views.customer_add_request_view, name="customer-add-request"),
    path("customer-profile", views.customer_profile_view, name="customer-profile"),
    path("edit-customer-profile", views.edit_customer_profile_view, name="edit-customer-profile"),
    path("customer-feedback", views.customer_feedback_view, name="customer-feedback"),
    path("customer-invoice", views.customer_invoice_view, name="customer-invoice"),
    path("customer-view-request", views.customer_view_request_view, name="customer-view-request"),
    path("customer-delete-request/<int:pk>", views.customer_delete_request_view, name="customer-delete-request"),
    path("customer-view-approved-request", views.customer_view_approved_request_view, name="customer-view-approved-request"),
    path(
        "customer-view-approved-request-invoice",
        views.customer_view_approved_request_invoice_view,
        name="customer-view-approved-request-invoice",
    ),
    path("generate-invoice-pdf/<int:request_id>/", views.generate_invoice_pdf, name="generate-invoice-pdf"),
]

