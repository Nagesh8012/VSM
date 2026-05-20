from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from vehicle import forms, models


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return HttpResponseRedirect("adminlogin")


@login_required(login_url="adminlogin")
def admin_dashboard_view(request):
    enquiry = models.Request.objects.all().order_by("-id")
    customers = [models.Customer.objects.get(id=enq.customer_id) for enq in enquiry if enq.customer_id]
    context = {
        "total_customer": models.Customer.objects.count(),
        "total_staff": models.Staff.objects.count(),
        "total_request": models.Request.objects.count(),
        "total_feedback": models.Feedback.objects.count(),
        "data": zip(customers, enquiry),
    }
    return render(request, "admin/admin_dashboard.html", context=context)


@login_required(login_url="adminlogin")
def admin_customer_view(request):
    return render(request, "admin/admin_customer.html")


@login_required(login_url="adminlogin")
def admin_view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, "admin/admin_view_customer.html", {"customers": customers})


@login_required(login_url="adminlogin")
def delete_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect("admin-view-customer")


@login_required(login_url="adminlogin")
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(instance=customer)
    context = {"userForm": userForm, "customerForm": customerForm}
    if request.method == "POST":
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect("admin-view-customer")
        context = {"userForm": userForm, "customerForm": customerForm}
    return render(request, "admin/update_customer.html", context=context)


@login_required(login_url="adminlogin")
def admin_add_customer_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    context = {"userForm": userForm, "customerForm": customerForm}
    if request.method == "POST":
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            customer_group = Group.objects.get_or_create(name="CUSTOMER")
            customer_group[0].user_set.add(user)
            return HttpResponseRedirect("/admin-view-customer")
        context = {"userForm": userForm, "customerForm": customerForm}
    return render(request, "admin/admin_add_customer.html", context=context)


@login_required(login_url="adminlogin")
def admin_view_customer_enquiry_view(request):
    enquiry = models.Request.objects.all().order_by("-id")
    customers = [models.Customer.objects.get(id=enq.customer_id) for enq in enquiry if enq.customer_id]
    return render(request, "admin/admin_view_customer_enquiry.html", {"data": zip(customers, enquiry)})


@login_required(login_url="adminlogin")
def admin_view_customer_invoice_view(request):
    enquiry = models.Request.objects.values("customer_id").annotate(Sum("cost"))
    customers = [models.Customer.objects.get(id=enq["customer_id"]) for enq in enquiry if enq["customer_id"]]
    return render(request, "admin/admin_view_customer_invoice.html", {"data": zip(customers, enquiry)})


@login_required(login_url="adminlogin")
def admin_staff_view(request):
    return render(request, "admin/admin_staff.html")


@login_required(login_url="adminlogin")
def admin_approve_staff_view(request):
    staff = models.Staff.objects.filter(status=False)
    return render(request, "admin/admin_approve_staff.html", {"staff": staff})


@login_required(login_url="adminlogin")
def approve_staff_view(request, pk):
    staffSalary = forms.StaffSalaryForm()
    if request.method == "POST":
        staffSalary = forms.StaffSalaryForm(request.POST)
        if staffSalary.is_valid():
            staff = models.Staff.objects.get(id=pk)
            staff.salary = staffSalary.cleaned_data["salary"]
            staff.status = True
            staff.save()
            return HttpResponseRedirect("/admin-approve-staff")
    return render(request, "admin/admin_approve_staff_details.html", {"staffSalary": staffSalary})


@login_required(login_url="adminlogin")
def admin_add_staff_view(request):
    userForm = forms.StaffUserForm()
    staffForm = forms.StaffForm()
    staffSalary = forms.StaffSalaryForm()
    context = {"userForm": userForm, "staffForm": staffForm, "staffSalary": staffSalary}
    if request.method == "POST":
        userForm = forms.StaffUserForm(request.POST)
        staffForm = forms.StaffForm(request.POST, request.FILES)
        staffSalary = forms.StaffSalaryForm(request.POST)
        if userForm.is_valid() and staffForm.is_valid() and staffSalary.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            staff = staffForm.save(commit=False)
            staff.user = user
            staff.status = True
            staff.salary = staffSalary.cleaned_data["salary"]
            staff.save()
            staff_group = Group.objects.get_or_create(name="STAFF")
            staff_group[0].user_set.add(user)
            return HttpResponseRedirect("admin-view-staff")
        context = {"userForm": userForm, "staffForm": staffForm, "staffSalary": staffSalary}
    return render(request, "admin/admin_add_staff.html", context=context)


@login_required(login_url="adminlogin")
def admin_view_staff_view(request):
    staff = models.Staff.objects.all()
    return render(request, "admin/admin_view_staff.html", {"staff": staff})


@login_required(login_url="adminlogin")
def delete_staff_view(request, pk):
    staff = models.Staff.objects.get(id=pk)
    user = User.objects.get(id=staff.user_id)
    user.delete()
    staff.delete()
    return redirect("admin-view-staff")


@login_required(login_url="adminlogin")
def update_staff_view(request, pk):
    staff = models.Staff.objects.get(id=pk)
    user = User.objects.get(id=staff.user_id)
    userForm = forms.StaffUserForm(instance=user)
    staffForm = forms.StaffForm(instance=staff)
    context = {"userForm": userForm, "staffForm": staffForm}
    if request.method == "POST":
        userForm = forms.StaffUserForm(request.POST, instance=user)
        staffForm = forms.StaffForm(request.POST, request.FILES, instance=staff)
        if userForm.is_valid() and staffForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            staffForm.save()
            return redirect("admin-view-staff")
        context = {"userForm": userForm, "staffForm": staffForm}
    return render(request, "admin/update_staff.html", context=context)


@login_required(login_url="adminlogin")
def admin_view_staff_salary_view(request):
    staff = models.Staff.objects.all()
    return render(request, "admin/admin_view_staff_salary.html", {"staff": staff})


@login_required(login_url="adminlogin")
def update_salary_view(request, pk):
    staffSalary = forms.StaffSalaryForm()
    if request.method == "POST":
        staffSalary = forms.StaffSalaryForm(request.POST)
        if staffSalary.is_valid():
            staff = models.Staff.objects.get(id=pk)
            staff.salary = staffSalary.cleaned_data["salary"]
            staff.save()
            return HttpResponseRedirect("/admin-view-staff-salary")
    return render(request, "admin/admin_approve_staff_details.html", {"staffSalary": staffSalary})


@login_required(login_url="adminlogin")
def admin_request_view(request):
    return render(request, "admin/admin_request.html")


@login_required(login_url="adminlogin")
def admin_view_request_view(request):
    enquiry = models.Request.objects.all().order_by("-id")
    customers = [models.Customer.objects.get(id=enq.customer_id) for enq in enquiry if enq.customer_id]
    return render(request, "admin/admin_view_request.html", {"data": zip(customers, enquiry)})


@login_required(login_url="adminlogin")
def change_status_view(request, pk):
    adminenquiry = forms.AdminApproveRequestForm()
    if request.method == "POST":
        adminenquiry = forms.AdminApproveRequestForm(request.POST)
        if adminenquiry.is_valid():
            enquiry = models.Request.objects.get(id=pk)
            enquiry.staff = adminenquiry.cleaned_data["staff"]
            enquiry.cost = adminenquiry.cleaned_data["cost"]
            enquiry.status = adminenquiry.cleaned_data["status"]
            enquiry.save()
            return HttpResponseRedirect("/admin-view-request")
    return render(request, "admin/admin_approve_request_details.html", {"adminenquiry": adminenquiry})


@login_required(login_url="adminlogin")
def admin_delete_request_view(request, pk):
    service_request = models.Request.objects.get(id=pk)
    service_request.delete()
    return redirect("admin-view-request")


@login_required(login_url="adminlogin")
def admin_add_request_view(request):
    enquiry = forms.RequestForm()
    adminenquiry = forms.AdminRequestForm()
    context = {"enquiry": enquiry, "adminenquiry": adminenquiry}
    if request.method == "POST":
        enquiry = forms.RequestForm(request.POST)
        adminenquiry = forms.AdminRequestForm(request.POST)
        if enquiry.is_valid() and adminenquiry.is_valid():
            enquiry_x = enquiry.save(commit=False)
            enquiry_x.customer = adminenquiry.cleaned_data["customer"]
            enquiry_x.staff = adminenquiry.cleaned_data["staff"]
            enquiry_x.cost = adminenquiry.cleaned_data["cost"]
            enquiry_x.status = "Approved"
            enquiry_x.save()
            return HttpResponseRedirect("admin-view-request")
        context = {"enquiry": enquiry, "adminenquiry": adminenquiry}
    return render(request, "admin/admin_add_request.html", context=context)


@login_required(login_url="adminlogin")
def admin_approve_request_view(request):
    enquiry = models.Request.objects.filter(status="Pending")
    return render(request, "admin/admin_approve_request.html", {"enquiry": enquiry})


@login_required(login_url="adminlogin")
def approve_request_view(request, pk):
    adminenquiry = forms.AdminApproveRequestForm()
    if request.method == "POST":
        adminenquiry = forms.AdminApproveRequestForm(request.POST)
        if adminenquiry.is_valid():
            enquiry = models.Request.objects.get(id=pk)
            enquiry.staff = adminenquiry.cleaned_data["staff"]
            enquiry.cost = adminenquiry.cleaned_data["cost"]
            enquiry.status = adminenquiry.cleaned_data["status"]
            enquiry.save()
            return HttpResponseRedirect("/admin-approve-request")
    return render(request, "admin/admin_approve_request_details.html", {"adminenquiry": adminenquiry})


@login_required(login_url="adminlogin")
def admin_view_service_cost_view(request):
    enquiry = models.Request.objects.all().order_by("-id")
    customers = [models.Customer.objects.get(id=enq.customer_id) for enq in enquiry if enq.customer_id]
    return render(request, "admin/admin_view_service_cost.html", {"data": zip(customers, enquiry)})


@login_required(login_url="adminlogin")
def update_cost_view(request, pk):
    updateCostForm = forms.UpdateCostForm()
    if request.method == "POST":
        updateCostForm = forms.UpdateCostForm(request.POST)
        if updateCostForm.is_valid():
            enquiry = models.Request.objects.get(id=pk)
            enquiry.cost = updateCostForm.cleaned_data["cost"]
            enquiry.save()
            return HttpResponseRedirect("/admin-view-service-cost")
    return render(request, "admin/update_cost.html", {"updateCostForm": updateCostForm})


@login_required(login_url="adminlogin")
def admin_staff_attendance_view(request):
    return render(request, "admin/admin_staff_attendance.html")


@login_required(login_url="adminlogin")
def admin_take_attendance_view(request):
    staff = list(models.Staff.objects.filter(status=True))
    aform = forms.AttendanceForm()
    if request.method == "POST":
        form = forms.AttendanceForm(request.POST)
        if form.is_valid():
            attendances = request.POST.getlist("present_status")
            date = form.cleaned_data["date"]
            for index, present_status in enumerate(attendances):
                if index < len(staff):
                    models.Attendance.objects.create(date=date, present_status=present_status, staff=staff[index])
            return redirect("admin-view-attendance")
    return render(request, "admin/admin_take_attendance.html", {"staff": staff, "aform": aform})


@login_required(login_url="adminlogin")
def admin_view_attendance_view(request):
    form = forms.AskDateForm()
    if request.method == "POST":
        form = forms.AskDateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date"]
            attendancedata = models.Attendance.objects.filter(date=date)
            staffdata = models.Staff.objects.filter(status=True)
            return render(request, "admin/admin_view_attendance_page.html", {"mylist": zip(attendancedata, staffdata), "date": date})
    return render(request, "admin/admin_view_attendance_ask_date.html", {"form": form})


@login_required(login_url="adminlogin")
def admin_report_view(request):
    reports = models.Request.objects.filter(Q(status="Repairing Done") | Q(status="Released"))
    return render(request, "admin/admin_report.html", {"reports": reports})


@login_required(login_url="adminlogin")
def admin_feedback_view(request):
    feedback = models.Feedback.objects.all().order_by("-id")
    return render(request, "admin/admin_feedback.html", {"feedback": feedback})

