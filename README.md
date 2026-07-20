# Coderr Backend

The robust backend for Coderr – a Fiverr-style marketplace connecting developers with clients. Built with Python, Django, and the Django REST Framework (DRF).

The API covers user onboarding, business/customer profiles, service offers with tiered pricing packages, order handling with a snapshot-based workflow, a review system, and platform-wide statistics — all secured via Token Authentication.

## Features & Tech Stack

* **Framework:** Django & Django REST Framework (DRF)
* **Authentication:** Token-based Authentication (`rest_framework.authtoken`)
* **Custom User Model:** Profile fields live directly on the user, distinguishing between `customer` and `business` account types
* **Filtering & Search:** `django-filter`, DRF `SearchFilter` and `OrderingFilter` for offers and reviews
* **Pagination:** `PageNumberPagination` for offer listings
* **Image Uploads:** Pillow-backed `ImageField` for profile pictures and offer images
* **Snapshot Pattern:** Orders freeze offer data at purchase time, so later offer edits never affect existing orders
* **Testing:** `pytest` & `pytest-django`, run against an in-memory SQLite database with a fast password hasher
* **Database:** SQLite (Development) / Ready for PostgreSQL (Production)

---

## Local Development Setup

Follow these steps to get the development server running locally:

> Note: On macOS/Linux you may need to use `python3` and `pip3` instead of `python` and `pip`, depending on your setup.

### 1. Clone the repository & enter the directory
```bash
git clone <repo-url>

cd coderr_backend
```

### 2. Create the virtual environment
To avoid environment pollution and issues with specific Python versions, create the environment without pre-installed packages first:

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows (PowerShell)
```bash
.venv\Scripts\Activate.ps1
```

macOS / Linux
```bash
source .venv/bin/activate
```

Note for Windows users: If you get a script execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` in your terminal first, then try activating again.

### 4. Set up package manager & install dependencies

To ensure the packages are installed correctly inside the virtual environment, use the python module path:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment variables

The project requires a `.env` file for local configuration and secrets. Copy the provided template and fill in your local values:

Windows (PowerShell)
```bash
Copy-Item .template.env .env
```

macOS / Linux
```bash
cp .template.env .env
```
Open the newly created `.env` file and set the following variables:

* `SECRET_KEY` – a local development key (e.g., `SECRET_KEY=your-local-dev-key`)
* `DEBUG` – set to `True` for local development

### 6. Run database migrations

```bash
python manage.py migrate
```

### 7. Create an administrative Superuser

To access the Django Admin interface or manage initial data, create a superuser account by running:

```bash
python manage.py createsuperuser
```

Follow the interactive prompts in your terminal to set a username, email, and password.

### 8. Start the development server

```bash
python manage.py runserver
```
The server will be available locally at: http://127.0.0.1:8000/

---

## Running Tests

Tests run with **pytest** against an in-memory SQLite database (see `core/test_settings.py`).

```bash
pytest

pytest orders_app

pytest --cov

pytest --cov --cov-report html
```

---

## API Endpoints (Documentation)

All endpoints (except Registration, Login, Offer listing, and Base Info) require the following header:
`Authorization: Token <your_token>`

### Authentication
* `POST /api/registration/` – Registers a new user (customer or business).
* `POST /api/login/` – Returns an auth token upon valid credentials.

### Profiles
* `GET /api/profile/<int:pk>/` – Retrieves a single user's profile.
* `PATCH /api/profile/<int:pk>/` – Updates the requesting user's own profile.
* `GET /api/profiles/business/` – Lists all business profiles.
* `GET /api/profiles/customer/` – Lists all customer profiles.

### Offers
* `GET /api/offers/` – Lists offers with filtering (`creator_id`, `min_price`, `max_delivery_time`), search (`search`), ordering (`ordering`), and pagination (`page_size`). *Public.*
* `POST /api/offers/` – Creates a new offer with exactly three pricing tiers (basic/standard/premium). *Permission: Business users only.*
* `GET /api/offers/<int:id>/` – Retrieves a single offer's details.
* `PATCH /api/offers/<int:id>/` – Partially updates an offer and/or its tiers, matched by `offer_type`. *Permission: Owner only.*
* `DELETE /api/offers/<int:id>/` – Deletes an offer. *Permission: Owner only.*
* `GET /api/offerdetails/<int:id>/` – Retrieves a single offer detail (tier), including its features.

### Orders
* `GET /api/orders/` – Lists orders where the user is either the customer or the business.
* `POST /api/orders/` – Creates an order from an `offer_detail_id`, copying its data as a snapshot. *Permission: Customers only.*
* `PATCH /api/orders/<int:id>/` – Updates only the order's `status`. *Permission: Assigned business user only.*
* `DELETE /api/orders/<int:id>/` – Deletes an order. *Permission: Admin/Staff only.*
* `GET /api/order-count/<int:business_user_id>/` – Returns the number of in-progress orders for a business user.
* `GET /api/completed-order-count/<int:business_user_id>/` – Returns the number of completed orders for a business user.

### Reviews
* `GET /api/reviews/` – Lists reviews with filtering (`business_user_id`, `reviewer_id`) and ordering (`ordering`).
* `POST /api/reviews/` – Creates a review for a business user (one review per business user per customer). *Permission: Customers only.*
* `PATCH /api/reviews/<int:id>/` – Updates only `rating` and `description`. *Permission: Author only.*
* `DELETE /api/reviews/<int:id>/` – Deletes a review. *Permission: Author only.*

### Platform
* `GET /api/base-info/` – Returns aggregated platform statistics (review count, average rating, business profile count, offer count). *Public.*

---

## Permissions & Validation Matrix (Examples)

| Endpoint | Action | Allowed For | Expected Status Codes |
| :--- | :--- | :--- | :--- |
| `/api/offers/` | `POST` | Business users only | `201` (Created), `400` (Invalid/Incomplete Details), `403` (Not a Business User) |
| `/api/orders/` | `POST` | Customers only | `201` (Created), `400` (Missing offer_detail_id), `403` (Not a Customer), `404` (OfferDetail Not Found) |
| `/api/orders/<id>/` | `PATCH` | **Strictly** the assigned Business User | `200` (Updated), `403` (Forbidden/Not Business Owner), `404` (Not Found) |
| `/api/orders/<id>/` | `DELETE` | **Strictly** Admin/Staff | `204` (No Content), `403` (Forbidden/Not Admin), `404` (Not Found) |
| `/api/reviews/` | `POST` | Customers only, one review per business user | `201` (Created), `400` (Duplicate Review / Not a Business User), `403` (Not a Customer) |
| `/api/reviews/<id>/` | `PATCH` / `DELETE` | **Strictly** the Review Author | `200` / `204`, `403` (Forbidden/Not Author), `404` (Not Found) |

---

## Project Structure (Core Apps)
* `core/` – Project configuration: settings, root URLs, and shared permissions used across apps.
* `auth_app/` – Custom user model (with `customer`/`business` type), registration, and login.
* `profiles_app/` – Profile retrieval, updates, and business/customer listing endpoints.
* `offers_app/` – Offers and their pricing tiers (`OfferDetail`), including features.
* `orders_app/` – Order creation, status workflow, and order-count statistics.
* `reviews_app/` – Customer reviews of business users.
* `platform_app/` – Cross-app aggregated statistics (`base-info`).