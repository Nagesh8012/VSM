from django.contrib import admin as django_admin
from django.urls import include, path
from vehicle import views

urlpatterns = [
    path("admin/", django_admin.site.urls),
    path("", views.home_view, name=""),
    path("afterlogin", views.afterlogin_view, name="afterlogin"),
    path("logout/", views.logout_view, name="logout"),
    path("aboutus", views.aboutus_view),
    path("contactus", views.contactus_view),
    path("", include("customer.urls")),
    path("", include("staff.urls")),
    path("", include("admin.urls")),
    path("api/customer/", include("customer.api_urls")),
    path("api/staff/", include("staff.api_urls")),
    path("api/admin/", include("admin.api_urls")),
]

