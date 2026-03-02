`db-access` is a Flask-based API that provides controlled access to the Dedalus PostgreSQL database.  
It acts as the database access layer for the system, isolating database logic behind an HTTP interface.

## What it does

- Executes SQL queries against a PostgreSQL database.
- Accepts CSV uploads and inserts their contents into a target table.
- Uses environment variables for configuration.
- Runs containerised with Docker.

## Key Files

- db_access.py – Main Flask application exposing API endpoints.
- csv_loader.py – Helper for loading CSV streams into PostgreSQL.
- requirements.txt – Python dependencies.
- Dockerfile – Container build definition.
- docker-compose.yml – Service orchestration.
- .env – Runtime configuration (API port and DB credentials).

## API Endpoints

### GET /

Basic health/info endpoint.

### POST /query

Executes a SQL query and returns results as JSON.

Request body example:

    {
      "query": "SELECT * FROM some_table LIMIT 10;"
    }

Response:
- success: true and data: [...] on success
- success: false and error: "..." on failure

### POST /upload_csv

Uploads a CSV file (multipart form-data) and inserts its contents into PostgreSQL.

Form-data:
- file – CSV file

Notes:
- The CSV is read as UTF-8 text and processed as a stream.
- The target table (currently device_measurements_30) is defined in code.

## Configuration

Environment variables (via .env):

Database:
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

API:
- PORT (currently set to 5000)

Copy `.env.example` to `.env` and replace the placeholder values with your actual configuration before running the service.

Example:
cp .env.example .env

## Deployment

The service is containerised using Docker and typically run via docker-compose.

## Security Note

The /query endpoint executes raw SQL and is intended for internal or controlled use only.