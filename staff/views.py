import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Count, Q
from django.db.models.functions import ExtractMonth
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from vehicle import forms, models
from vehicle.auth import is_staff


def staffclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "staff/staffclick.html")


def staff_signup_view(request):
    userForm = forms.StaffUserForm()
    staffForm = forms.StaffForm()
    context = {"userForm": userForm, "staffForm": staffForm}
    if request.method == "POST":
        userForm = forms.StaffUserForm(request.POST)
        staffForm = forms.StaffForm(request.POST, request.FILES)
        if userForm.is_valid() and staffForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            staff = staffForm.save(commit=False)
            staff.user = user
            staff.save()
            staff_group = Group.objects.get_or_create(name="STAFF")
            staff_group[0].user_set.add(user)
            return HttpResponseRedirect("stafflogin")
        context = {"userForm": userForm, "staffForm": staffForm}
    return render(request, "staff/staffsignup.html", context=context)


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_dashboard_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    work_in_progress = models.Request.objects.filter(staff_id=staff.id, status="Repairing").count()
    work_completed = models.Request.objects.filter(staff_id=staff.id, status="Repairing Done").count()
    new_work_assigned = models.Request.objects.filter(staff_id=staff.id, status="Approved").count()
    monthly_repair_data = (
        models.Request.objects.filter(staff_id=staff.id)
        .annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    context = {
        "work_in_progress": work_in_progress,
        "work_completed": work_completed,
        "new_work_assigned": new_work_assigned,
        "salary": staff.salary,
        "staff": staff,
        "status_labels": json.dumps(["New Assigned", "In Progress", "Completed"]),
        "status_counts": json.dumps([new_work_assigned, work_in_progress, work_completed]),
        "months": json.dumps([entry["month"] for entry in monthly_repair_data]),
        "request_counts": json.dumps([entry["count"] for entry in monthly_repair_data]),
        "salary_labels": json.dumps(["Current Salary"]),
        "salary_values": json.dumps([staff.salary]),
    }
    return render(request, "staff/staff_dashboard.html", context)


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_work_assigned_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    works = models.Request.objects.filter(staff_id=staff.id)
    return render(request, "staff/staff_work_assigned.html", {"works": works, "staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_update_status_view(request, pk):
    staff = models.Staff.objects.get(user_id=request.user.id)
    updateStatus = forms.StaffUpdateStatusForm()
    if request.method == "POST":
        updateStatus = forms.StaffUpdateStatusForm(request.POST)
        if updateStatus.is_valid():
            enquiry = models.Request.objects.get(id=pk, staff=staff)
            enquiry.status = updateStatus.cleaned_data["status"]
            enquiry.save()
            return HttpResponseRedirect("/staff-work-assigned")
    return render(request, "staff/staff_update_status.html", {"updateStatus": updateStatus, "staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_attendance_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    attendaces = models.Attendance.objects.filter(staff=staff)
    return render(request, "staff/staff_view_attendance.html", {"attendaces": attendaces, "staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_feedback_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    feedback = forms.FeedbackForm()
    if request.method == "POST":
        feedback = forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
            return render(request, "staff/feedback_sent.html", {"staff": staff})
    return render(request, "staff/staff_feedback.html", {"feedback": feedback, "staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_salary_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    workdone = models.Request.objects.filter(staff_id=staff.id).filter(Q(status="Repairing Done") | Q(status="Released"))
    return render(request, "staff/staff_salary.html", {"workdone": workdone, "staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def staff_profile_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    return render(request, "staff/staff_profile.html", {"staff": staff})


@login_required(login_url="stafflogin")
@user_passes_test(is_staff)
def edit_staff_profile_view(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    user = User.objects.get(id=staff.user_id)
    userForm = forms.StaffUserForm(instance=user)
    staffForm = forms.StaffForm(instance=staff)
    context = {"userForm": userForm, "staffForm": staffForm, "staff": staff}
    if request.method == "POST":
        userForm = forms.StaffUserForm(request.POST, instance=user)
        staffForm = forms.StaffForm(request.POST, request.FILES, instance=staff)
        if userForm.is_valid() and staffForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            staffForm.save()
            return redirect("staff-profile")
        context = {"userForm": userForm, "staffForm": staffForm, "staff": staff}
    return render(request, "staff/edit_staff_profile.html", context=context)

