`model_training` contains the code used to train, evaluate, and run inference for the energy disaggregation models.

The module is organized so that reusable functionality is implemented in Python utility modules, while model training and experimentation are performed in Jupyter notebooks.

## Structure

### Python modules

All `.py` files provide reusable utilities used by the notebooks:

- `configs.py` – configuration parameters for experiments.
- `data.py` – dataset loading and preprocessing utilities.
- `generators_clean.py` – data generators used during training.
- `models.py` – neural network model definitions.
- `trainer.py` – training routines and helper functions.
- `eval.py` – evaluation metrics and model assessment utilities.
- `inference.py` – inference utilities for applying trained models.

These modules are imported by the notebooks to keep experiment code organized and reusable.

## Notebooks

The `.ipynb` notebooks contain the actual experiments and model training workflows.

Typical tasks performed in the notebooks include:

- Training classification and regression models
- Running experiments for different appliances
- Evaluating model performance
- Reconstructing appliance power signals using the gated architecture

Note: notebooks are not tracked in the repository and are excluded from version control.

## Saved Models

Trained models are stored in the `models/` directory.

These saved models can later be loaded for inference or evaluation.

## Dependencies

Python dependencies are listed in `requirements.txt`.