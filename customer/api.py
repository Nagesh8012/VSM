from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from vehicle import forms, models
from vehicle.api_utils import bad_request, form_errors, json_body, method_not_allowed
from vehicle.auth import is_customer
from vehicle.serializers import customer_to_dict, feedback_to_dict, request_to_dict


@csrf_exempt
def signup(request):
    if request.method != "POST":
        return method_not_allowed(["POST"])

    data = json_body(request)
    user_form = forms.CustomerUserForm(data)
    customer_form = forms.CustomerForm(data)
    if not user_form.is_valid() or not customer_form.is_valid():
        return bad_request("Invalid customer signup data.", {"user": form_errors(user_form), "customer": form_errors(customer_form)})

    user = user_form.save()
    user.set_password(user.password)
    user.save()
    customer = customer_form.save(commit=False)
    customer.user = user
    customer.save()
    customer_group = Group.objects.get_or_create(name="CUSTOMER")
    customer_group[0].user_set.add(user)
    return JsonResponse({"customer": customer_to_dict(customer, request)}, status=201)


@login_required
@user_passes_test(is_customer)
def dashboard(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])

    customer = models.Customer.objects.get(user_id=request.user.id)
    completed_filter = Q(status="Repairing Done") | Q(status="Released")
    new_filter = Q(status="Pending") | Q(status="Approved")
    return JsonResponse({
        "customer": customer_to_dict(customer, request),
        "work_in_progress": models.Request.objects.filter(customer=customer, status="Repairing").count(),
        "work_completed": models.Request.objects.filter(customer=customer).filter(completed_filter).count(),
        "new_request_made": models.Request.objects.filter(customer=customer).filter(new_filter).count(),
        "bill": models.Request.objects.filter(customer=customer).filter(completed_filter).aggregate(Sum("cost"))["cost__sum"] or 0,
    })


@csrf_exempt
@login_required
@user_passes_test(is_customer)
def profile(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    if request.method == "GET":
        return JsonResponse({"customer": customer_to_dict(customer, request)})
    if request.method not in ["PUT", "PATCH"]:
        return method_not_allowed(["GET", "PUT", "PATCH"])

    data = json_body(request)
    user = customer.user
    for field in ["first_name", "last_name", "email"]:
        if field in data:
            setattr(user, field, data[field])
    user.save()
    for field in ["address", "mobile"]:
        if field in data:
            setattr(customer, field, data[field])
    customer.save()
    return JsonResponse({"customer": customer_to_dict(customer, request)})


@csrf_exempt
@login_required
@user_passes_test(is_customer)
def requests(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    if request.method == "GET":
        enquiries = models.Request.objects.filter(customer=customer).order_by("-id")
        return JsonResponse({"requests": [request_to_dict(enquiry, request) for enquiry in enquiries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    form = forms.RequestForm(json_body(request))
    if not form.is_valid():
        return bad_request("Invalid service request data.", form_errors(form))
    enquiry = form.save(commit=False)
    enquiry.customer = customer
    enquiry.save()
    return JsonResponse({"request": request_to_dict(enquiry, request)}, status=201)


@csrf_exempt
@login_required
@user_passes_test(is_customer)
def request_detail(request, pk):
    try:
        enquiry = models.Request.objects.get(id=pk, customer__user=request.user)
    except models.Request.DoesNotExist:
        return JsonResponse({"error": "Request not found."}, status=404)

    if request.method == "GET":
        return JsonResponse({"request": request_to_dict(enquiry, request)})
    if request.method == "DELETE":
        if enquiry.status != "Pending":
            return JsonResponse({"error": "Only pending requests can be deleted."}, status=400)
        enquiry.delete()
        return JsonResponse({}, status=204)
    return method_not_allowed(["GET", "DELETE"])


@login_required
@user_passes_test(is_customer)
def approved_requests(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer=customer).exclude(status="Pending").order_by("-id")
    return JsonResponse({"requests": [request_to_dict(enquiry, request) for enquiry in enquiries]})


@login_required
@user_passes_test(is_customer)
def invoices(request):
    if request.method != "GET":
        return method_not_allowed(["GET"])
    customer = models.Customer.objects.get(user_id=request.user.id)
    enquiries = models.Request.objects.filter(customer=customer).exclude(status="Pending").order_by("-id")
    return JsonResponse({"invoices": [request_to_dict(enquiry, request) for enquiry in enquiries]})


@csrf_exempt
@login_required
@user_passes_test(is_customer)
def feedback(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    if request.method == "GET":
        entries = models.Feedback.objects.filter(by__icontains=customer.user.first_name).order_by("-id")
        return JsonResponse({"feedback": [feedback_to_dict(entry) for entry in entries]})
    if request.method != "POST":
        return method_not_allowed(["GET", "POST"])

    form = forms.FeedbackForm(json_body(request))
    if not form.is_valid():
        return bad_request("Invalid feedback data.", form_errors(form))
    entry = form.save()
    return JsonResponse({"feedback": feedback_to_dict(entry)}, status=201)

