`dedalus_update` updates the Dedalus PostgreSQL database with new measurements fetched from the energy provider API (HERON).  
It downloads device measurements in time windows, converts them to CSV format, and uploads them to the database through the `db-access` API.

## What it does

- Reads pipeline configuration from `pipeline_config.yaml`:
  - `last_updated` – last successfully processed timestamp
  - `num_processes` – number of parallel workers
  - `relative_delta` – size of each processing window
- Retrieves device information from the HERON API.
- Iterates from `last_updated` until the current time in fixed windows.
- For each window:
  - Fetches measurements for all devices.
  - Converts the payload to CSV format.
  - Uploads the CSV to the Dedalus database through `db-access`.
- Updates `last_updated` after a successful window.

## Reliability

- Network operations use retry logic (Tenacity).
- Retries occur with increasing wait times.
- If payloads are too large, the time window is automatically split into smaller segments.

## Multiprocessing

Devices are processed in parallel using Python multiprocessing.  
The number of workers is controlled by `num_processes` in `pipeline_config.yaml`.

## Key Files

- `update_db_pipeline.py` – Main pipeline entry point.
- `pipeline_config.yaml` – Pipeline configuration (time window and workers).
- `pipeline_config_manager.py` – Reads and updates pipeline configuration.
- `heron_manager.py` / `heron_utils/` – HERON API integration.
- `processing.py` – Converts API responses into CSV buffers.
- `logger_config.py` – Logging configuration.
- `Dockerfile` – Container definition.

## Configuration

The pipeline requires environment variables for the database API and HERON credentials.

Create a `.env` file based on `.env.example`.

## Running the Pipeline

The pipeline can be executed in two ways.

### Run directly with Python

    python update_db_pipeline.py

### Run with Docker

    docker compose up