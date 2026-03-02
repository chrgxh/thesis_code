# Project Overview

This repository contains the full data ingestion, database update, and model training pipeline for the energy disaggregation system.  
The architecture is modular and containerised, allowing controlled data updates and reproducible model experimentation.

The main components are:

- csv_pipeline
- db-access
- dedalus_update
- model_training

Both pipelines and the database API are containerised using Docker.


# Components

## db-access

Provides an API layer to query the Dedalus database.

Purpose:

- Abstract database access
- Provide structured data retrieval for the CSV pipeline
- Decouple data access logic from processing logic

This component is containerised with Docker.

## csv_pipeline

Reads building energy data from the Dedalus database and generates or updates:

- Building-level CSV files  
- HDF5 (.h5) datasets  
- Building metadata  

The behaviour is controlled through buildings.json, which defines:

- home_id
- last_updated
- active_in_pipeline
- Device-level configuration (last_updated, active_in_pipeline, meter id, appliance name, time ranges, etc.)

The pipeline supports multiprocessing for efficient data processing.

This component is containerised with Docker.


## dedalus_update

Updates the Dedalus database using the external energy provider API.

Configuration is controlled via:

- pipeline_config.yaml
- settings.py

Example configuration parameters include:

- last_updated
- num_processes
- relative_delta
- API settings (start date, step size, nanosecond multiplier)
- Device metadata and measurement history

The update process supports multiprocessing.

This component is containerised with Docker.


## model_training

Contains the machine learning code for the gated architecture.

Provides:

- Classification model
- Regression model
- Training routines
- Model saving
- Experimentation utilities

Used to train and persist models for disaggregation experiments.


# Design Notes

- Modular separation between ingestion, database updates, and model training  
- Config-driven pipelines  
- Multiprocessing support  
- Docker-based containerisation for reproducibility and deployment  