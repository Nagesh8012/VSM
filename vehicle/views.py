from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from vehicle import forms, models
from vehicle.auth import is_customer, is_staff


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "core/index.html")


def afterlogin_view(request):
    if is_customer(request.user):
        return redirect("customer-dashboard")
    if is_staff(request.user):
        accountapproval = models.Staff.objects.filter(user_id=request.user.id, status=True)
        if accountapproval:
            return redirect("staff-dashboard")
        return render(request, "staff/staff_wait_for_approval.html")
    return redirect("admin-dashboard")


def aboutus_view(request):
    return render(request, "core/aboutus.html")


def contactus_view(request):
    form = forms.ContactusForm()
    if request.method == "POST":
        form = forms.ContactusForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["Email"]
            name = form.cleaned_data["Name"]
            message = form.cleaned_data["Message"]
            send_mail(str(name) + " || " + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently=False)
            return render(request, "core/contactussuccess.html")
    return render(request, "core/contactus.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("/")




