# Equipment and Resource Management API

A Django REST Framework API for registering shared resources and handling booking requests. Employees request resources, while resource managers or admins approve and reject requests. Only approved bookings reserve inventory.

## Main features

- JWT login and refresh tokens
- Admin, Resource Manager, and Employee roles
- Category and resource management
- Multi-resource booking requests
- Date-range availability checks
- Approval checks inside a database transaction
- Search, filtering, ordering, and pagination
- OpenAPI schema and Swagger UI
- Automated API tests

## Technology

- Python 3.12
- Django and Django REST Framework
- PostgreSQL
- Simple JWT
- django-filter
- drf-spectacular

## Local setup

1. Create a PostgreSQL database:

   
   CREATE DATABASE management;
   

2. Create and activate a virtual environment:

   venv\Scripts\activate

3. Install dependencies:

   pip install -r requirements.txt
 

4. Copy `.env.example` to `.env` and change the database password and secret key.

5. Run migrations and create an admin:

   python manage.py migrate
   python manage.py createsuperuser
   

6. Start the server:

   python manage.py runserver
   



## Authentication

Register at `POST /api/users/register/`, then log in at `POST /api/users/login/` with `username` and `password`. Send the access token on protected requests:


Authorization: Bearer <access-token>


New registrations are Employees. Create Resource Manager accounts through Django admin, or change the role of an existing user there.

## Important endpoints

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/api/users/register/` | Public | Register an employee |
| POST | `/api/users/login/` | Public | Get access and refresh tokens |
| GET/PATCH | `/api/users/profile/` | Logged in | View or update own profile |
| GET/POST | `/api/categories/` | All / Manager | List or create categories |
| GET/POST | `/api/resources/` | All / Manager | List or create resources |
| GET | `/api/resources/{id}/` | Logged in | View resource details |
| GET/POST | `/api/bookings/` | Logged in / Employee | List or create bookings |
| POST | `/api/bookings/{id}/approve/` | Manager | Approve a pending booking |
| POST | `/api/bookings/{id}/reject/` | Manager | Reject with a reason |
| POST | `/api/bookings/{id}/cancel/` | Owner or Manager | Cancel pending/approved booking |
| POST | `/api/bookings/{id}/complete/` | Manager | Complete approved booking |

Admin users have the same management permissions as resource managers plus access to the user list and Django admin.

## Creating a booking

```json
{
  "start_date": "2030-11-10T08:00:00+03:00",
  "end_date": "2030-11-12T17:00:00+03:00",
  "items": [
    {"resource": 1, "quantity": 2},
    {"resource": 3, "quantity": 1}
  ]
}
```

To reject a booking, send `{"reason": "Resource is under maintenance"}` to its reject endpoint.

## Availability, search, and filtering

Pass both dates to calculate availability for a period:

```text
GET /api/resources/?start_date=2030-11-10T08:00:00Z&end_date=2030-11-12T17:00:00Z
```

Add `available_quantity=2` to return only active resources with at least two units free throughout that period. Resource filters include `category`, `location`, `active`, and `search`. Booking filters include `status`, `user`, `resource`, `start_date`, and `end_date`. Use `page` for pagination and `ordering` for sorting.

Intervals use an end-exclusive overlap rule: a booking ending at 10:00 does not conflict with one beginning at 10:00.

## Tests

Tests use the configured PostgreSQL server and create a temporary test database:

```powershell
python manage.py test
```

The PostgreSQL user must have permission to create a test database.

## Project structure

- `users/` - authentication, profile, roles, and user permissions
- `resource/` - categories, resources, availability query, and filters
- `booking/` - booking models, inventory calculation, workflow, and tests
- `config/` - Django settings and root URLs
- `LEARNING_GUIDE.md` - suggested order for studying this project
