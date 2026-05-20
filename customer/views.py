import json
from io import BytesIO

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from vehicle import forms, models
from vehicle.auth import is_customer


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "customer/customerclick.html")


def customer_signup_view(request):
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
            return HttpResponseRedirect("customerlogin")
        context = {"userForm": userForm, "customerForm": customerForm}
    return render(request, "customer/customersignup.html", context=context)


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_dashboard_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    status_data = models.Request.objects.filter(customer=customer).values("status").annotate(count=Count("status"))
    status_labels = [entry["status"] for entry in status_data]
    status_counts = [entry["count"] for entry in status_data]
    monthly_data = models.Request.objects.filter(customer=customer).values_list("date__month").annotate(count=Count("id"))
    months = [entry[0] for entry in monthly_data]
    request_counts = [entry[1] for entry in monthly_data]
    cost_data = models.Request.objects.filter(customer=customer).values("status").annotate(total_cost=Sum("cost"))
    cost_labels = [entry["status"] for entry in cost_data]
    cost_values = [entry["total_cost"] for entry in cost_data]

    context = {
        "work_in_progress": models.Request.objects.filter(customer=customer, status="Repairing").count(),
        "work_completed": models.Request.objects.filter(customer=customer).filter(
            Q(status="Repairing Done") | Q(status="Released")
        ).count(),
        "new_request_made": models.Request.objects.filter(customer=customer).filter(
            Q(status="Pending") | Q(status="Approved")
        ).count(),
        "bill": models.Request.objects.filter(customer=customer)
        .filter(Q(status="Repairing Done") | Q(status="Released"))
        .aggregate(Sum("cost"))["cost__sum"],
        "customer": customer,
        "status_labels": json.dumps(status_labels),
        "status_counts": json.dumps(status_counts),
        "months": json.dumps(months),
        "request_counts": json.dumps(request_counts),
        "cost_labels": json.dumps(cost_labels),
        "cost_values": json.dumps(cost_values),
    }
    return render(request, "customer/customer_dashboard.html", context=context)


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, "customer/customer_request.html", {"customer": customer})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_view_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id, status="Pending")
    return render(request, "customer/customer_view_request.html", {"customer": customer, "enquiries": enquiries})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_delete_request_view(request, pk):
    enquiry = models.Request.objects.get(id=pk, customer__user=request.user)
    enquiry.delete()
    return redirect("customer-view-request")


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_view_approved_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id).exclude(status="Pending")
    return render(
        request,
        "customer/customer_view_approved_request.html",
        {"customer": customer, "enquiries": enquiries},
    )


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_view_approved_request_invoice_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id).exclude(status="Pending")
    return render(
        request,
        "customer/customer_view_approved_request_invoice.html",
        {"customer": customer, "enquiries": enquiries},
    )


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_add_request_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiry = forms.RequestForm()
    if request.method == "POST":
        enquiry = forms.RequestForm(request.POST)
        if enquiry.is_valid():
            enquiry_x = enquiry.save(commit=False)
            enquiry_x.customer = customer
            enquiry_x.save()
            return HttpResponseRedirect("customer-dashboard")
    return render(request, "customer/customer_add_request.html", {"enquiry": enquiry, "customer": customer})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, "customer/customer_profile.html", {"customer": customer})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def edit_customer_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(instance=customer)
    context = {"userForm": userForm, "customerForm": customerForm, "customer": customer}
    if request.method == "POST":
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect("customer-profile")
        context = {"userForm": userForm, "customerForm": customerForm, "customer": customer}
    return render(request, "customer/edit_customer_profile.html", context=context)


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_invoice_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer_id=customer.id).exclude(status="Pending")
    return render(request, "customer/customer_invoice.html", {"customer": customer, "enquiries": enquiries})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def customer_feedback_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    feedback = forms.FeedbackForm()
    if request.method == "POST":
        feedback = forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
            return render(request, "customer/feedback_sent_by_customer.html", {"customer": customer})
    return render(request, "customer/customer_feedback.html", {"feedback": feedback, "customer": customer})


@login_required(login_url="customerlogin")
@user_passes_test(is_customer)
def generate_invoice_pdf(request, request_id):
    try:
        enquiry = models.Request.objects.get(id=request_id, customer__user=request.user)
    except models.Request.DoesNotExist:
        return HttpResponse("Unauthorized")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=50, rightMargin=50, topMargin=60, bottomMargin=50)
    elements = []
    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#2E86C1")

    title = Paragraph("<b><font size=30 color='#2E86C1'>VEHICLE SERVICE INVOICE</font></b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 80))

    invoice_data = [["Invoice ID:", f"INV-{enquiry.id}", "Date:", enquiry.date.strftime("%d-%m-%Y")]]
    invoice_table = Table(invoice_data, colWidths=[60, 150, 30, 150])
    invoice_table.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (-1, -1), colors.black), ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold")]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 40))

    customer = enquiry.customer
    customer_data = [
        ["Customer Name:", customer.user.get_full_name()],
        ["Email:", customer.email],
        ["Phone:", customer.mobile],
        ["Address:", customer.address],
    ]
    customer_table = Table(customer_data, colWidths=[150, 300])
    customer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), primary_color),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 60))

    staff_name = enquiry.staff.user.get_full_name() if enquiry.staff else "Not Assigned"
    vehicle_data = [
        ["Vehicle Category:", enquiry.category],
        ["Vehicle Name:", enquiry.vehicle_name],
        ["Vehicle Number:", enquiry.vehicle_no],
        ["Vehicle Model:", enquiry.vehicle_model],
        ["Vehicle Brand:", enquiry.vehicle_brand],
        ["Problem Description:", enquiry.problem_description],
        ["Assigned Staff:", staff_name],
    ]
    vehicle_table = Table(vehicle_data, colWidths=[150, 300])
    vehicle_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), primary_color),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(vehicle_table)
    elements.append(Spacer(1, 20))

    cost_table = Table([["Service Cost:", f"Rs. {enquiry.cost or 0}"]], colWidths=[150, 300])
    cost_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.red),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(cost_table)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<font size=20 color='black'>Thank you for choosing our service !!</font>", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b><font size=15 color='#2E86C1'>For queries, contact us: support@vehicleserviceManagement.com</font></b>", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

