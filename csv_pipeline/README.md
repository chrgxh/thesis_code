`csv_pipeline` reads building/device power measurements from the Dedalus PostgreSQL database (via the `db-access` API) and incrementally builds structured building datasets.

It is configuration-driven through `buildings.json` and supports multiprocessing.

## What it does

For each active building defined in `buildings.json`:

- Reads `home_id`, device mappings and `last_updated`.
- Queries `device_measurements_30` through the `db-access` API.
- Pulls data in fixed time batches (e.g., ~6-day windows).
- Applies transformations:
  - Timestamp normalization
  - Device ID mapping
  - Power aggregation
  - Reshaping per device/phase
- Appends results to a building-level CSV file.
- Updates `last_updated` after successful processing.

If no new data exists, the building is skipped.

## Outputs

- Building CSV files (combined mains + meters, appended incrementally).
- Updated `buildings.json` with latest processed timestamps.
- Metadata files (stored in the metadata directory).

Paths (data, metadata, etc.) are defined in the pipeline configuration / shared constants.

## HDF5 Creation

HDF5 (`.h5`) files are created separately from the generated building CSV files.

The utility responsible for this conversion:
- Reads the building CSV files
- Creates structured `.h5` datasets
- Stores them at the configured output path

This step is not part of the incremental DB ingestion loop.

## Multiprocessing

Buildings are processed in parallel using Python multiprocessing (`mp.Pool`).

The number of parallel workers is defined in `common.py` via `MAX_PROCESSES`.

## Key Files

- `run_pipeline.py` – Entry point that orchestrates building processing.
- `buildings.json` – Configuration file defining buildings, devices, and progress tracking.
- `buildings_json_handler.py` – Reads and updates building metadata.
- `query_db_access_api.py` – Executes SQL queries via the `db-access` API.
- `transformations.py` – Data cleaning and aggregation logic.
- `device_and_building.py` – Device/building-level handling.
- `convert_greek.py` – Converts building CSV files into structured HDF5 datasets.
- `common.py` – Shared constants and settings (including `MAX_PROCESSES`).
- `Dockerfile` – Container definition for running the pipeline.

## Design Notes

- Incremental updates based on `last_updated`.
- Config-driven building/device control.
- Parallel processing across buildings.
- Separation between ingestion (CSV generation) and dataset packaging (HDF5 conversion).
- Designed to run containerised with Docker.