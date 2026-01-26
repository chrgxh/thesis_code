import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
)

def evaluate_classifier(model, eval_gen, threshold: float = 0.5, max_batches=None, return_arrays: bool = False):
    """
    Works with eval generators that yield:
      (X, y) OR (X, y, ts) OR (X, y, ...)
    """
    y_true_all = []
    y_pred_all = []

    n_total = len(eval_gen)
    n = n_total if max_batches is None else min(n_total, max_batches)

    for i in range(n):
        batch = eval_gen[i]
        X, y = batch[0], batch[1]  # ignore timestamps/extra outputs

        probs = model.predict(X, verbose=0).reshape(-1)
        preds = (probs >= threshold).astype(int)

        y_true_all.append(np.asarray(y).reshape(-1))
        y_pred_all.append(preds)

    y_true = np.concatenate(y_true_all) if y_true_all else np.array([], dtype=int)
    y_pred = np.concatenate(y_pred_all) if y_pred_all else np.array([], dtype=int)

    acc = accuracy_score(y_true, y_pred) if len(y_true) else 0.0
    prec = precision_score(y_true, y_pred, zero_division=0) if len(y_true) else 0.0
    rec = recall_score(y_true, y_pred, zero_division=0) if len(y_true) else 0.0
    f1 = f1_score(y_true, y_pred, zero_division=0) if len(y_true) else 0.0
    cm = confusion_matrix(y_true, y_pred) if len(y_true) else np.array([[0, 0], [0, 0]])

    print("\nEvaluation (Classifier)")
    print(f"Used batches: {n}/{n_total}")
    print(f"Threshold : {threshold:.2f}")
    print(f"Accuracy  : {acc:.4f}")
    print(f"Precision : {prec:.4f}")
    print(f"Recall    : {rec:.4f}")
    print(f"F1        : {f1:.4f}")
    print("Confusion matrix:\n", cm)

    if return_arrays:
        return (acc, prec, rec, f1, cm), (y_true, y_pred)

    return acc, prec, rec, f1, cm


def threshold_sweep(
    model,
    eval_gen,
    thresholds=np.linspace(0.1, 0.9, 17),
    max_batches=None,
    plot: bool = True,
):
    """
    Sweeps thresholds for a classifier and returns the best threshold by F1.
    """
    probs_all = []
    y_all = []

    n_total = len(eval_gen)
    n = n_total if max_batches is None else min(n_total, max_batches)

    for i in range(n):
        batch = eval_gen[i]
        X, y = batch[0], batch[1]
        probs = model.predict(X, verbose=0).reshape(-1)

        probs_all.append(probs)
        y_all.append(np.asarray(y).reshape(-1))

    probs_all = np.concatenate(probs_all) if probs_all else np.array([])
    y_all = np.concatenate(y_all) if y_all else np.array([])

    precisions, recalls, f1s = [], [], []
    for t in thresholds:
        pred = (probs_all >= t).astype(int)
        precisions.append(precision_score(y_all, pred, zero_division=0))
        recalls.append(recall_score(y_all, pred, zero_division=0))
        f1s.append(f1_score(y_all, pred, zero_division=0))

    best_i = int(np.argmax(f1s)) if len(f1s) else 0
    best_t = float(thresholds[best_i]) if len(thresholds) else 0.5

    if plot:
        plt.figure(figsize=(10, 5))
        plt.plot(thresholds, precisions, label="Precision")
        plt.plot(thresholds, recalls, label="Recall")
        plt.plot(thresholds, f1s, label="F1")
        plt.xlabel("Threshold")
        plt.ylabel("Score")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    print(f"\nBest threshold by F1: {best_t:.2f} (F1={f1s[best_i]:.4f})")
    return best_t

def evaluate_regressor_watts(model, eval_gen, max_batches=None):
    """
    Your ON-only regressor setup:
      - generator yields y in kW
      - model predicts in kW
    This function reports MAE/RMSE/MaxAE in Watts.
    """
    y_true_all = []
    y_pred_all = []

    n_total = len(eval_gen)
    n = n_total if max_batches is None else min(n_total, max_batches)

    for i in range(n):
        batch = eval_gen[i]
        X, y_kw = batch[0], batch[1]  # y is in kW
        pred_kw = model.predict(X, verbose=0).reshape(-1)

        y_true_all.append(np.asarray(y_kw).reshape(-1))
        y_pred_all.append(pred_kw)

    y_true_kw = np.concatenate(y_true_all) if y_true_all else np.array([], dtype=np.float64)
    y_pred_kw = np.concatenate(y_pred_all) if y_pred_all else np.array([], dtype=np.float64)

    # convert back to Watts for reporting
    y_true_w = np.asarray(y_true_kw, dtype=np.float64).ravel() * 1000.0
    y_pred_w = np.asarray(y_pred_kw, dtype=np.float64).ravel() * 1000.0

    if len(y_true_w):
        err = y_true_w - y_pred_w
        mae = float(np.mean(np.abs(err)))
        rmse = float(np.sqrt(np.mean(err ** 2)))
        maxae = float(np.max(np.abs(err)))
    else:
        mae, rmse, maxae = 0.0, 0.0, 0.0

    print("\nRegressor Evaluation (ON-only)")
    print(f"Used batches: {n}/{n_total}")
    print(f"MAE  : {mae:.2f} W")
    print(f"RMSE : {rmse:.2f} W")
    print(f"MaxAE: {maxae:.2f} W")
    return mae, rmse, maxae
