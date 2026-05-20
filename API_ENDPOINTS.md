# API Endpoints

The backend uses Django `JsonResponse` endpoints and session authentication.

## Customer

- `POST /api/customer/signup/`
- `GET /api/customer/dashboard/`
- `GET|PUT|PATCH /api/customer/profile/`
- `GET|POST /api/customer/requests/`
- `GET|DELETE /api/customer/requests/<id>/`
- `GET /api/customer/approved-requests/`
- `GET /api/customer/invoices/`
- `GET|POST /api/customer/feedback/`

## Staff

- `POST /api/staff/signup/`
- `GET /api/staff/dashboard/`
- `GET|PUT|PATCH /api/staff/profile/`
- `GET /api/staff/work/`
- `POST|PUT|PATCH /api/staff/work/<id>/status/`
- `GET /api/staff/attendance/`
- `GET /api/staff/salary/`
- `GET|POST /api/staff/feedback/`

## Admin

- `GET /api/admin/dashboard/`
- `GET|POST /api/admin/customers/`
- `GET|PUT|PATCH|DELETE /api/admin/customers/<id>/`
- `GET|POST /api/admin/staff/`
- `GET|PUT|PATCH|DELETE /api/admin/staff/<id>/`
- `POST|PUT|PATCH /api/admin/staff/<id>/approve/`
- `GET|POST /api/admin/requests/`
- `GET|PUT|PATCH|DELETE /api/admin/requests/<id>/`
- `GET|POST /api/admin/attendance/`
- `GET /api/admin/feedback/`
- `GET /api/admin/reports/`

