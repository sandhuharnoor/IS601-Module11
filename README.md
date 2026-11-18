# IS601 Module 11 - PostgreSQL Calculation Persistence

## Project Overview

This project extends a FastAPI calculator application with SQLAlchemy calculation models, PostgreSQL persistence, automated testing, Docker containerization, and GitHub Actions CI/CD.

The calculation model uses SQLAlchemy polymorphic inheritance to support addition, subtraction, multiplication, and division. Calculations are associated with users and can be stored and retrieved from PostgreSQL.

## Technology Stack

- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL 17
- Pydantic
- Pytest and pytest-cov
- Playwright
- Docker and Docker Compose
- GitHub Actions
- Trivy

## Project Features

- SQLAlchemy calculation models for four arithmetic operations
- User-to-calculation relationships
- Pydantic calculation schemas and validation
- PostgreSQL integration tests
- Browser-based end-to-end calculator tests
- Docker health endpoint at `/health`
- CI/CD workflow for testing, security scanning, and Docker Hub publication

The calculator's existing FastAPI endpoints are separate from the calculation persistence layer. CRUD API endpoints for persisted calculations are not implemented in this module.

## Local Setup

Clone the repository:

```bash
git clone https://github.com/sandhuharnoor/IS601-Module11.git
cd IS601-Module11
```

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Start PostgreSQL:

```powershell
docker compose up -d
```

Create the dedicated integration test database if it does not exist:

```powershell
docker exec postgres_db psql -U postgres -d postgres -c "CREATE DATABASE module11_test;"
```

The database creation command should only be run once. If the database already exists, PostgreSQL will report that it exists.

## Running Tests

Set the dedicated integration test database URL in PowerShell:

```powershell
$env:TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/module11_test"
```

Run all automated tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/e2e -q --tb=short
```

Latest verified local result:

- 110 tests passed
- 100% coverage

Integration tests create and drop SQLAlchemy tables in the dedicated `module11_test` database. Do not point these tests at a database containing important data.

## Running the Application

Start the FastAPI application locally:

```powershell
.\.venv\Scripts\python.exe main.py
```

Open:

- http://localhost:8000
- http://localhost:8000/health

## Docker

Build the image:

```powershell
docker build -t hsandhu24/is601-module11:local .
```

Run the container:

```powershell
docker run --rm -p 8001:8000 hsandhu24/is601-module11:local
```

Open http://localhost:8001/health to verify the health endpoint.

## CI/CD

The GitHub Actions workflow is configured to:

1. Start a PostgreSQL 17 service.
2. Install Python dependencies and Playwright Chromium.
3. Run unit and integration tests.
4. Run browser E2E tests.
5. Build and scan the Docker image with Trivy.
6. Publish the image to Docker Hub after successful checks on the main branch.

Docker Hub publishing uses GitHub Actions secrets named `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.

Docker Hub image:
`hsandhu24/is601-module11`

The remote workflow and published image still require verification.

## Reflection

This module helped me understand how SQLAlchemy models connect application logic to a PostgreSQL database. I worked with polymorphic calculation models, user relationships, and integration tests that verify data persistence.

One challenge was configuring PostgreSQL for testing without interfering with other project databases. I addressed this by creating a dedicated test database and adding a database-name guard to the integration test fixture.

I also worked through an E2E testing issue where the FastAPI subprocess used a different Python interpreter from pytest. Updating the fixture to use `sys.executable` resolved the issue.

Finally, I improved the Docker build by excluding unnecessary files through `.dockerignore` and verified the application's health endpoint inside a running container.

The biggest takeaway was that passing unit tests alone is not enough. Integration tests, browser tests, container checks, and CI/CD verification each test a different part of the application.
