from django.contrib import admin
from .models import Attendance, Customer, Feedback, Request, Staff

admin.site.register(Customer)
admin.site.register(Staff)
admin.site.register(Request)
admin.site.register(Attendance)
admin.site.register(Feedback)
