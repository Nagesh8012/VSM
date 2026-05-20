from django.templatetags.static import static


def image_url(request, image_field):
    if not image_field:
        return None
    try:
        return request.build_absolute_uri(static(image_field.name))
    except ValueError:
        return None


def user_to_dict(user):
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.get_full_name(),
        "username": user.username,
        "email": user.email,
    }


def customer_to_dict(customer, request=None):
    return {
        "id": customer.id,
        "user": user_to_dict(customer.user),
        "name": customer.get_name,
        "mobile": customer.mobile,
        "email": customer.email,
        "address": customer.address,
        "profile_pic": image_url(request, customer.profile_pic) if request else None,
    }


def staff_to_dict(staff, request=None):
    return {
        "id": staff.id,
        "user": user_to_dict(staff.user),
        "name": staff.get_name,
        "mobile": staff.mobile,
        "email": staff.email,
        "address": staff.address,
        "skill": staff.skill,
        "salary": staff.salary,
        "status": staff.status,
        "profile_pic": image_url(request, staff.profile_pic) if request else None,
    }


def request_to_dict(service_request, request=None):
    return {
        "id": service_request.id,
        "category": service_request.category,
        "vehicle_no": service_request.vehicle_no,
        "vehicle_name": service_request.vehicle_name,
        "vehicle_model": service_request.vehicle_model,
        "vehicle_brand": service_request.vehicle_brand,
        "problem_description": service_request.problem_description,
        "date": service_request.date.isoformat() if service_request.date else None,
        "cost": service_request.cost,
        "status": service_request.status,
        "customer": customer_to_dict(service_request.customer, request) if service_request.customer else None,
        "staff": staff_to_dict(service_request.staff, request) if service_request.staff else None,
    }


def attendance_to_dict(attendance, request=None):
    return {
        "id": attendance.id,
        "staff": staff_to_dict(attendance.staff, request) if attendance.staff else None,
        "date": attendance.date.isoformat() if attendance.date else None,
        "present_status": attendance.present_status,
    }


def feedback_to_dict(feedback):
    return {
        "id": feedback.id,
        "date": feedback.date.isoformat() if feedback.date else None,
        "by": feedback.by,
        "message": feedback.message,
    }

