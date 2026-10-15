# QuickBite QA

This folder contains regression tests and a Postman collection for the existing
Flask application. It does not replace or restructure the app. Test dependencies,
browser automation, collection, and test documentation are kept here, separate
from the application source.

## Existing application inspected

- **Stack:** Python 3.12, Flask, Jinja templates, SQLite, and static HTML/CSS/images.
- **Main files:** `app.py`, `db.py`, `food.db`, `templates/`, and `static/`.
- **Menu flow:** `GET /` reads menu items from SQLite and renders `templates/index.html`.
- **Order form flow:** `GET /order/<food_id>` renders `templates/order.html`.
- **Submission flow:** `POST /submit_order` accepts URL-encoded form fields `name`,
  `phone`, `address`, `food_id`, and `payment`, inserts an order, and renders a
  confirmation.
- **Dashboard flow:** `GET /view_orders` joins orders to menu items and renders
  `templates/view_orders.html`.
- **API format:** There are no JSON API endpoints in the current app. These are
  HTML and form-submission routes; the Postman collection represents those exact
  routes and does not invent an API.

## Setup and run the browser tests

From the repository root, with the app's existing Python/`uv` setup available:

```sh
uv sync --project qa
uv run --project qa playwright install chromium
uv run --project qa pytest -c qa/pyproject.toml
```

If Chromium reports missing operating-system libraries, install Playwright's
required browser dependencies for your environment before rerunning the tests.

The test fixture copies the app code, templates, and static files to a temporary
directory, seeds a new SQLite database there using `db.py`, and starts the copy on
a temporary local port. It does not write test orders to the repository's
`food.db`. The temporary server and database are removed after the test session.

## Postman collection

Import `postman/QuickBite.postman_collection.json` into Postman. Set `baseUrl` to
the base address of the app instance you intend to test (the default is
`http://127.0.0.1:5000` for a locally accessible server).

The collection contains:

- `GET /`
- `GET /order/1`
- `POST /submit_order`
- `GET /view_orders`

**Use a disposable development database and fake data only.** `POST /submit_order`
persists an order. `GET /view_orders` currently exposes delivery names, phone
numbers, and addresses and has no authentication. Do not run those requests
against real customer data or expose the dashboard publicly.

## Test results

Most recent run: **3 passed** with Playwright Chromium and pytest.

- Menu renders all ten seeded items and their local images.
- A browser user can open an order form, submit a fake test order, and see it in
  the dashboard.
- The Postman collection is valid JSON and its four method/path pairs match the
  existing Flask routes.
- The suite runs against copied application files and a temporary database; the
  repository's `food.db` is not used for test writes.
