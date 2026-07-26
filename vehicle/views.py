import random

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
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


def forgot_password_view(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            context["error"] = "No account found with this registered email."
            return render(request, "core/forgot_password.html", context)

        otp = f"{random.randint(100000, 999999)}"
        request.session["reset_user_id"] = user.id
        request.session["reset_email"] = user.email
        request.session["reset_otp"] = otp
        request.session["reset_otp_verified"] = False

        subject = "NRE-Fix Password Reset OTP"
        message = f"Your NRE-Fix password reset OTP is {otp}. Do not share this code with anyone."
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
        except Exception as exc:
            context["error"] = "OTP could not be sent. Please check email settings and try again."
            context["debug_error"] = str(exc) if settings.DEBUG else ""
            return render(request, "core/forgot_password.html", context)

        return redirect("verify-reset-otp")

    return render(request, "core/forgot_password.html", context)


def verify_reset_otp_view(request):
    if not request.session.get("reset_user_id"):
        return redirect("forgot-password")

    context = {"email": request.session.get("reset_email")}
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        if entered_otp == request.session.get("reset_otp"):
            request.session["reset_otp_verified"] = True
            return redirect("set-new-password")
        context["error"] = "Invalid OTP. Please enter the code sent to your email."

    return render(request, "core/verify_reset_otp.html", context)


def set_new_password_view(request):
    user_id = request.session.get("reset_user_id")
    if not user_id:
        return redirect("forgot-password")
    if not request.session.get("reset_otp_verified"):
        return redirect("verify-reset-otp")

    context = {}
    if request.method == "POST":
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        if password1 != password2:
            context["error"] = "Passwords do not match."
            return render(request, "core/set_new_password.html", context)

        user = User.objects.get(id=user_id)
        try:
            password_validation.validate_password(password1, user)
        except ValidationError as exc:
            context["error"] = " ".join(exc.messages)
            return render(request, "core/set_new_password.html", context)

        user.set_password(password1)
        user.save()
        for key in ["reset_user_id", "reset_email", "reset_otp", "reset_otp_verified"]:
            request.session.pop(key, None)
        return render(request, "core/password_reset_success.html")

    return render(request, "core/set_new_password.html", context)

def logout_view(request):
    logout(request)
    return redirect("/")



