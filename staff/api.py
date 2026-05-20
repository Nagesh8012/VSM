from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from vehicle import forms, models
from vehicle.api_utils import bad_request, form_errors, json_body, method_not_allowed
from vehicle.auth import is_staff
from vehicle.serializers import attendance_to_dict, feedback_to_dict, request_to_dict, staff_to_dict


@csrf_exempt
def signup(request):
    if request.method != "POST":
        return method_not_allowed(["POST"])

    data = json_body(request)
    user_form = forms.StaffUserForm(data)
    staff_form = forms.StaffForm(data)
    if not user_form.is_valid() or not staff_form.is_valid():
        return bad_request("Invalid staff signup data.", {"user": form_errors(user_form), "staff": form_errors(staff_form)})

    user = user_form.save()
    user.set_password(user.password)
    user.save()
    staff = staff_form.save(commit=False)
    staff.user = user
    staff.save()
    staff_group = Group.objects.get_or_create(name="STAFF")
    staff_group[0].user_set.add(user)
    return JsonResponse({"staff": staff_to_dict(staff, request)}, status=201)


@login_required
@user_passes_test(is_staff)
def dashboard(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    staff = models.Staff.objects.get(user_id=request.user.id)
    return JsonResponse({
        "staff": staff_to_dict(staff, request),
        "work_in_progress": models.Request.objects.filter(staff_id=staff.id, status="Repairing").count(),
        "work_completed": models.Request.objects.filter(staff_id=staff.id, status="Repairing Done").count(),
        "new_work_assigned": models.Request.objects.filter(staff_id=staff.id, status="Approved").count(),
        "salary": staff.salary,
    })


@csrf_exempt
@login_required
@user_passes_test(is_staff)
def profile(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    if request.method == "GET":
        return JsonResponse({"staff": staff_to_dict(staff, request)})
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed(["GET", "PUT", "PATCH"])

    data = json_body(request)
    user = staff.user
    for field in ["first_name", "last_name", "email"]:
        if field in data:
            setattr(user, field, data[field])
    user.save()
    for field in ["address", "mobile", "skill"]:
        if field in data:
            setattr(staff, field, data[field])
    staff.save()
    return JsonResponse({"staff": staff_to_dict(staff, request)})


@login_required
@user_passes_test(is_staff)
def work_assigned(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    staff = models.Staff.objects.get(user_id=request.user.id)
    works = models.Request.objects.filter(staff_id=staff.id).order_by("-id")
    return JsonResponse({"work": [request_to_dict(work, request) for work in works]})


@csrf_exempt
@login_required
@user_passes_test(is_staff)
def update_work_status(request, pk):
    if request.method not in ["PUT", "PATCH", "POST"]:
        return method_not_allowed(["PUT", "PATCH", "POST"])
    staff = models.Staff.objects.get(user_id=request.user.id)
    try:
        work = models.Request.objects.get(id=pk, staff=staff)
    except models.Request.DoesNotExist:
        return JsonResponse({"error": "Work request not found."}, status=404)

    form = forms.StaffUpdateStatusForm(json_body(request))
    if not form.is_valid():
        return bad_request("Invalid status data.", form_errors(form))
    work.status = form.cleaned_data["status"]
    work.save()
    return JsonResponse({"request": request_to_dict(work, request)})


@login_required
@user_passes_test(is_staff)
def attendance(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    staff = models.Staff.objects.get(user_id=request.user.id)
    entries = models.Attendance.objects.filter(staff=staff).order_by("-date")
    return JsonResponse({"attendance": [attendance_to_dict(entry, request) for entry in entries]})


@login_required
@user_passes_test(is_staff)
def salary(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    staff = models.Staff.objects.get(user_id=request.user.id)
    workdone = models.Request.objects.filter(staff_id=staff.id).filter(Q(status="Repairing Done") | Q(status="Released"))
    return JsonResponse({"salary": staff.salary, "completed_work": [request_to_dict(work, request) for work in workdone]})


@csrf_exempt
@login_required
@user_passes_test(is_staff)
def feedback(request):
    staff = models.Staff.objects.get(user_id=request.user.id)
    if request.method == "GET":
        entries = models.Feedback.objects.filter(by__icontains=staff.user.first_name).order_by("-id")
        return JsonResponse({"feedback": [feedback_to_dict(entry) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    form = forms.FeedbackForm(json_body(request))
    if not form.is_valid():
        return bad_request("Invalid feedback data.", form_errors(form))
    entry = form.save()
    return JsonResponse({"feedback": feedback_to_dict(entry)}, status=201)

