# QuickBite

## Run on Replit

- Stack: Python 3.12, Flask, Jinja HTML templates, and SQLite.
- Click Run to start the `Start application` workflow (`uv run python app.py`).
- The app listens on `0.0.0.0:5000` and appears in the web preview.
- Dependencies are recorded in `pyproject.toml` and `uv.lock`; `uv sync` installs the locked dependencies.
- No secrets or external services are required for the existing functionality.

## Pages and data

- `/`: food menu.
- `/order/<food_id>`: delivery details and payment-method selection.
- `/view_orders`: order dashboard.
- The included `food.db` is the existing SQLite database. Keep it intact.
- For a new, empty database only, run `uv run python db.py` to create tables and insert the ten menu items.
- Run commands from the repository root because database paths are relative to the working directory.

## Existing limitations

- The order dashboard has no authentication and exposes delivery contact details. Do not use real customer data or publish it publicly before adding access control.
- PhonePe is only a recorded payment-method choice; the app does not process or verify payments.
- The Flask development server is intended for development, not production hosting.
