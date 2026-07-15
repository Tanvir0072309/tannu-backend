# Tannu Backend

A Python backend for the Tannu project.

This repository contains the server-side code and configuration for the Tannu application.

## Features
- Python-based REST API
- Environment-config driven setup
- Easy local development and testing

## Requirements
- Python 3.8+
- pip
- (Optional) virtualenv or venv

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Tanvir0072309/tannu-backend.git
   cd tannu-backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment
Create a `.env` file in the project root (or set environment variables) with the following values:

```env
# Example .env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
PORT=8000
```

Adjust these variables according to your project's configuration.

## Running locally
Start the development server (example using Flask):

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=${PORT:-8000}
```

Or use the project's start script if provided:

```bash
./run.sh
# or
honcho start # if Procfile + honcho/foreman is used
```

## Database & Migrations
If your project uses a database and migrations (Alembic/Flask-Migrate/Django migrations), run the migration commands included in the repo. Example (Flask-Migrate):

```bash
flask db upgrade
```

## Tests
Run the test suite with:

```bash
pytest
```

## Contributing
Contributions are welcome. Please open an issue to discuss major changes and send a pull request with a clear description of your changes.

## License
Add the appropriate license for your project (e.g., MIT). If you don't have one yet, consider adding a LICENSE file.

---

Note: README ko Hindi mein chahiye tha toh bataiye; main Hindi mein bhi likh sakta hoon. 😊
