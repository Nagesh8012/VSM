from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from vehicle import forms, models
from vehicle.api_utils import bad_request, form_errors, json_body, method_not_allowed
from vehicle.serializers import attendance_to_dict, customer_to_dict, feedback_to_dict, request_to_dict, staff_to_dict


def is_admin_user(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin_user)
def dashboard(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    return JsonResponse({
        "total_customer": models.Customer.objects.count(),
        "total_staff": models.Staff.objects.count(),
        "total_request": models.Request.objects.count(),
        "total_feedback": models.Feedback.objects.count(),
        "recent_requests": [request_to_dict(item, request) for item in models.Request.objects.order_by("-id")[:10]],
    })


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def customers(request):
    if request.method == "GET":
        entries = models.Customer.objects.all().order_by("-id")
        return JsonResponse({"customers": [customer_to_dict(entry, request) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    data = json_body(request)
    user_form = forms.CustomerUserForm(data)
    customer_form = forms.CustomerForm(data)
    if not user_form.is_valid() or not customer_form.is_valid():
        return bad_request("Invalid customer data.", {"user": form_errors(user_form), "customer": form_errors(customer_form)})

    user = user_form.save()
    user.set_password(user.password)
    user.save()
    customer = customer_form.save(commit=False)
    customer.user = user
    customer.save()
    group = Group.objects.get_or_create(name="CUSTOMER")
    group[0].user_set.add(user)
    return JsonResponse({"customer": customer_to_dict(customer, request)}, status=201)


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def customer_detail(request, pk):
    try:
        customer = models.Customer.objects.get(id=pk)
    except models.Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"customer": customer_to_dict(customer, request)})
    if request.method == "DELETE":
        customer.user.delete()
        return JsonResponse({}, status=204)
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed(["GET", "PUT", "PATCH", "DELETE"])

    data = json_body(request)
    user = customer.user
    for field in ["first_name", "last_name", "username", "email"]:
        if field in data:
            setattr(user, field, data[field])
    if data.get("password"):
        user.set_password(data["password"])
    user.save()
    for field in ["address", "mobile"]:
        if field in data:
            setattr(customer, field, data[field])
    customer.save()
    return JsonResponse({"customer": customer_to_dict(customer, request)})


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def staff_members(request):
    if request.method == "GET":
        entries = models.Staff.objects.all().order_by("-id")
        return JsonResponse({"staff": [staff_to_dict(entry, request) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    data = json_body(request)
    user_form = forms.StaffUserForm(data)
    staff_form = forms.StaffForm(data)
    salary_form = forms.StaffSalaryForm(data)
    if not user_form.is_valid() or not staff_form.is_valid() or not salary_form.is_valid():
        return bad_request(
            "Invalid staff data.",
            {"user": form_errors(user_form), "staff": form_errors(staff_form), "salary": form_errors(salary_form)},
        )

    user = user_form.save()
    user.set_password(user.password)
    user.save()
    staff = staff_form.save(commit=False)
    staff.user = user
    staff.status = True
    staff.salary = salary_form.cleaned_data["salary"]
    staff.save()
    group = Group.objects.get_or_create(name="STAFF")
    group[0].user_set.add(user)
    return JsonResponse({"staff": staff_to_dict(staff, request)}, status=201)


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def staff_detail(request, pk):
    try:
        staff = models.Staff.objects.get(id=pk)
    except models.Staff.DoesNotExist:
        return JsonResponse({"error": "Staff member not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"staff": staff_to_dict(staff, request)})
    if request.method == "DELETE":
        staff.user.delete()
        return JsonResponse({}, status=204)
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed(["GET", "PUT", "PATCH", "DELETE"])

    data = json_body(request)
    user = staff.user
    for field in ["first_name", "last_name", "username", "email"]:
        if field in data:
            setattr(user, field, data[field])
    if data.get("password"):
        user.set_password(data["password"])
    user.save()
    for field in ["address", "mobile", "skill", "salary", "status"]:
        if field in data:
            setattr(staff, field, data[field])
    staff.save()
    return JsonResponse({"staff": staff_to_dict(staff, request)})


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def approve_staff(request, pk):
    if request.method not in ["POST", "PUT", "PATCH"]:
        return method_not_allowed(["POST", "PUT", "PATCH"])
    try:
        staff = models.Staff.objects.get(id=pk)
    except models.Staff.DoesNotExist:
        return JsonResponse({"error": "Staff member not found."}, status=404)

    data = json_body(request)
    staff.salary = data.get("salary", staff.salary)
    staff.status = True
    staff.save()
    return JsonResponse({"staff": staff_to_dict(staff, request)})


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def service_requests(request):
    if request.method == "GET":
        entries = models.Request.objects.all().order_by("-id")
        return JsonResponse({"requests": [request_to_dict(entry, request) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    data = json_body(request)
    form = forms.RequestForm(data)
    if not form.is_valid():
        return bad_request("Invalid service request data.", form_errors(form))

    try:
        customer = models.Customer.objects.get(id=data.get("customer"))
    except models.Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found."}, status=404)
    staff_member = None
    if data.get("staff"):
        try:
            staff_member = models.Staff.objects.get(id=data.get("staff"))
        except models.Staff.DoesNotExist:
            return JsonResponse({"error": "Staff member not found."}, status=404)

    service_request = form.save(commit=False)
    service_request.customer = customer
    service_request.staff = staff_member
    service_request.cost = data.get("cost")
    service_request.status = data.get("status", "Approved")
    service_request.save()
    return JsonResponse({"request": request_to_dict(service_request, request)}, status=201)


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def service_request_detail(request, pk):
    try:
        service_request = models.Request.objects.get(id=pk)
    except models.Request.DoesNotExist:
        return JsonResponse({"error": "Service request not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"request": request_to_dict(service_request, request)})
    if request.method == "DELETE":
        service_request.delete()
        return JsonResponse({}, status=204)
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed(["GET", "PUT", "PATCH", "DELETE"])

    data = json_body(request)
    for field in ["category", "vehicle_no", "vehicle_name", "vehicle_model", "vehicle_brand", "problem_description", "cost", "status"]:
        if field in data:
            setattr(service_request, field, data[field])
    if "customer" in data:
        service_request.customer = models.Customer.objects.get(id=data["customer"])
    if "staff" in data:
        service_request.staff = models.Staff.objects.get(id=data["staff"]) if data["staff"] else None
    service_request.save()
    return JsonResponse({"request": request_to_dict(service_request, request)})


@csrf_exempt
@login_required
@user_passes_test(is_admin_user)
def attendance(request):
    if request.method == "GET":
        entries = models.Attendance.objects.all().order_by("-date", "-id")
        return JsonResponse({"attendance": [attendance_to_dict(entry, request) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    data = json_body(request)
    try:
        staff_member = models.Staff.objects.get(id=data.get("staff"))
    except models.Staff.DoesNotExist:
        return JsonResponse({"error": "Staff member not found."}, status=404)
    entry = models.Attendance.objects.create(
        staff=staff_member,
        date=data.get("date"),
        present_status=data.get("present_status", "Present"),
    )
    return JsonResponse({"attendance": attendance_to_dict(entry, request)}, status=201)


@login_required
@user_passes_test(is_admin_user)
def feedback(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    entries = models.Feedback.objects.all().order_by("-id")
    return JsonResponse({"feedback": [feedback_to_dict(entry) for entry in entries]})


@login_required
@user_passes_test(is_admin_user)
def reports(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    entries = models.Request.objects.filter(Q(status="Repairing Done") | Q(status="Released")).order_by("-id")
    return JsonResponse({
        "reports": [request_to_dict(entry, request) for entry in entries],
        "total_cost": entries.aggregate(Sum("cost"))["cost__sum"] or 0,
    })

