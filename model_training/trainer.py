import os
import json
from dataclasses import asdict
from typing import Any, Dict, Optional

from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from configs import ClassifierTrainConfig, RegressorTrainConfig, ModelConfig
from data import build_classification_gens, build_regression_gens
from eval import evaluate_classifier, threshold_sweep, evaluate_regressor_watts
from models import create_classification_model, create_regression_model


# -------------------------
# Callbacks
# -------------------------
def _make_classifier_callbacks():
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        min_delta=1e-4,
        restore_best_weights=True,
        verbose=1,
    )
    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=4,
        min_lr=1e-5,
        cooldown=1,
        verbose=1,
    )
    return [early_stop, reduce_lr]


def _make_regressor_callbacks():
    # Matches your regressor notebook intent
    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=5,
        min_delta=0.02,
        restore_best_weights=True,
        verbose=1,
    )
    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=4,
        min_lr=1e-5,
        cooldown=1,
        verbose=1,
    )
    return [early_stop, reduce_lr]


def _ensure_save_dir(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def _save_run_metadata_json(path_no_ext: str, payload: Dict[str, Any]) -> str:
    json_path = path_no_ext + ".json"
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    return json_path


# -------------------------
# Train classifier
# -------------------------
def train_classifier(
    train_cfg: ClassifierTrainConfig,
    model_cfg: ModelConfig,
    threshold_eval: float = 0.5,
    sweep_thresholds: bool = True,
    sweep_plot: bool = True,
    save_config_json: bool = True,
) -> Dict[str, Any]:
    """
    Trains the ON/OFF classifier.

    - Uses train_cfg.threshold to create labels in the generators.
    - threshold_eval is the probability threshold used for evaluation.
    - If sweep_thresholds=True, chooses best threshold by F1 on val_eval.
    """
    _ensure_save_dir(train_cfg.save_path)

    train_gen, val_gen, val_eval = build_classification_gens(train_cfg)
    model = create_classification_model(train_cfg.window_size, model_cfg)

    fit_kwargs: Dict[str, Any] = dict(
        epochs=train_cfg.epochs,
        callbacks=_make_classifier_callbacks(),
        verbose=1,
    )

    if train_cfg.class_weight is not None:
        fit_kwargs["class_weight"] = train_cfg.class_weight
    if train_cfg.steps_per_epoch is not None:
        fit_kwargs["steps_per_epoch"] = train_cfg.steps_per_epoch
    if train_cfg.validation_steps is not None:
        fit_kwargs["validation_steps"] = train_cfg.validation_steps

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        **fit_kwargs,
    )

    base_metrics = evaluate_classifier(model, val_eval, threshold=threshold_eval)

    best_t: Optional[float] = None
    best_metrics = None
    if sweep_thresholds:
        best_t = threshold_sweep(model, val_eval, plot=sweep_plot)
        best_metrics = evaluate_classifier(model, val_eval, threshold=best_t)

    model.save(train_cfg.save_path)
    print(f"\nSaved classifier to: {train_cfg.save_path}")

    json_path = None
    if save_config_json:
        path_no_ext = train_cfg.save_path.rsplit(".", 1)[0]
        payload: Dict[str, Any] = {
            "task": "classifier",
            "train_config": asdict(train_cfg),
            "model_config": asdict(model_cfg),
            "threshold_eval": threshold_eval,
            "best_threshold": best_t,
            "base_metrics": {
                "acc": float(base_metrics[0]),
                "prec": float(base_metrics[1]),
                "rec": float(base_metrics[2]),
                "f1": float(base_metrics[3]),
                "cm": base_metrics[4].tolist(),
            },
        }
        if best_metrics is not None:
            payload["best_metrics"] = {
                "acc": float(best_metrics[0]),
                "prec": float(best_metrics[1]),
                "rec": float(best_metrics[2]),
                "f1": float(best_metrics[3]),
                "cm": best_metrics[4].tolist(),
            }

        json_path = _save_run_metadata_json(path_no_ext, payload)
        print(f"Saved run metadata to: {json_path}")

    return {
        "model": model,
        "history": history.history,
        "base_metrics": base_metrics,
        "best_threshold": best_t,
        "best_metrics": best_metrics,
        "model_path": train_cfg.save_path,
        "json_path": json_path,
    }


# -------------------------
# Train regressor (ON-only)
# -------------------------
def train_regressor(
    train_cfg: RegressorTrainConfig,
    model_cfg: ModelConfig,
    save_config_json: bool = True,
) -> Dict[str, Any]:
    """
    Trains the ON-only regressor.

    Your ON-only regression generator yields targets in kW.
    evaluate_regressor_watts converts predictions/targets back to Watts for reporting.
    """
    _ensure_save_dir(train_cfg.save_path)

    train_gen, val_gen, val_eval = build_regression_gens(train_cfg)
    model = create_regression_model(train_cfg.window_size, model_cfg)

    fit_kwargs: Dict[str, Any] = dict(
        epochs=train_cfg.epochs,
        callbacks=_make_regressor_callbacks(),
        verbose=1,
    )
    if train_cfg.steps_per_epoch is not None:
        fit_kwargs["steps_per_epoch"] = train_cfg.steps_per_epoch
    if train_cfg.validation_steps is not None:
        fit_kwargs["validation_steps"] = train_cfg.validation_steps

    history = model.fit(
        train_gen,
        validation_data=val_gen,
        **fit_kwargs,
    )

    mae_w, rmse_w, maxae_w = evaluate_regressor_watts(model, val_eval)

    model.save(train_cfg.save_path)
    print(f"\nSaved regressor to: {train_cfg.save_path}")

    json_path = None
    if save_config_json:
        path_no_ext = train_cfg.save_path.rsplit(".", 1)[0]
        payload: Dict[str, Any] = {
            "task": "regressor_ononly",
            "train_config": asdict(train_cfg),
            "model_config": asdict(model_cfg),
            "metrics_watts": {
                "mae_w": float(mae_w),
                "rmse_w": float(rmse_w),
                "maxae_w": float(maxae_w),
            },
        }
        json_path = _save_run_metadata_json(path_no_ext, payload)
        print(f"Saved run metadata to: {json_path}")

    return {
        "model": model,
        "history": history.history,
        "metrics_watts": (mae_w, rmse_w, maxae_w),
        "model_path": train_cfg.save_path,
        "json_path": json_path,
    }
