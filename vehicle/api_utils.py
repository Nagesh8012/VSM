import json

from django.http import JsonResponse


def json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def bad_request(message, errors=None):
    payload = {"error": message}
    if errors:
        payload["errors"] = errors
    return JsonResponse(payload, status=400)


def method_not_allowed(allowed_methods):
    response = JsonResponse({"error": "Method not allowed."}, status=405)
    response["Allow"] = ", ".join(allowed_methods)
    return response


def form_errors(form):
    return {field: [str(error) for error in errors] for field, errors in form.errors.items()}
