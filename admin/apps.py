from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    label = "admin_panel"
    name = "admin"
    verbose_name = "Admin Panel"

