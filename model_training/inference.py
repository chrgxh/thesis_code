import gc
import numpy as np
import pandas as pd
from nilmtk import DataSet
from tensorflow.keras.models import load_model
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    precision_score, recall_score, f1_score, accuracy_score
)

def rmse(y_true, y_pred):
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))

def build_aligned_df(h5_path, building, start, end, appliance, sample_period):
    gc.collect()
    ds = DataSet(h5_path)
    ds.set_window(start=start, end=end)
    elec = ds.buildings[int(building)].elec

    mains = next(elec.mains().load(sample_period=sample_period))
    appl = next(elec[appliance].load(sample_period=sample_period))

    mains.columns = ["mains"]
    appl.columns = ["appliance"]

    df = mains.join(appl, how="inner").dropna()
    return df

def make_windows_two_channel(mains_1d, window_size):
    W = int(window_size)
    half = W // 2
    n = len(mains_1d)
    if n < W:
        return None, None

    centers = np.arange(half, n - half)
    X = np.empty((len(centers), W, 2), dtype=np.float32)

    for j, c in enumerate(centers):
        w = mains_1d[c - half : c + half + 1]
        d = np.diff(w, prepend=w[0])
        X[j, :, 0] = w
        X[j, :, 1] = d

    return X, centers

def predict_regressor(regressor, X_on):
    """Supports regressor with 1 input (B,W,2) OR 2 inputs [mains(B,W,1), delta(B,W,1)]."""
    if X_on.size == 0:
        return np.array([], dtype=np.float32)

    n_inputs = len(regressor.inputs)
    if n_inputs == 1:
        return regressor.predict(X_on, verbose=0).reshape(-1).astype(np.float32)

    if n_inputs == 2:
        mains = X_on[:, :, 0:1]
        delta = X_on[:, :, 1:2]
        return regressor.predict([mains, delta], verbose=0).reshape(-1).astype(np.float32)

    raise ValueError(f"Unexpected regressor input count: {n_inputs}")

def compute_gate_metrics(labels, clf_pred):
    return {
        "acc": float(accuracy_score(labels, clf_pred)),
        "prec": float(precision_score(labels, clf_pred, zero_division=0)),
        "rec": float(recall_score(labels, clf_pred, zero_division=0)),
        "f1": float(f1_score(labels, clf_pred, zero_division=0)),
        "true_on_rate": float(np.mean(labels)),
        "pred_on_rate": float(np.mean(clf_pred)),
    }

def compute_total_metrics(y_true_w, y_pred_w):
    mae = float(mean_absolute_error(y_true_w, y_pred_w))
    r = rmse(y_true_w, y_pred_w)
    return {"mae_w": mae, "rmse_w": r}

def compute_on_only_metrics(y_true_w, y_pred_w, on_w=50.0):
    mask_on = y_true_w >= on_w
    if not np.any(mask_on):
        return {"mae_w": np.nan, "rmse_w": np.nan}
    mae = float(mean_absolute_error(y_true_w[mask_on], y_pred_w[mask_on]))
    r = rmse(y_true_w[mask_on], y_pred_w[mask_on])
    return {"mae_w": mae, "rmse_w": r}

def reconstruct_signal(
    h5_path: str,
    building: int,
    start: str,
    end: str,
    appliance: str,
    sample_period: int,
    window_size: int,
    classifier_path: str,
    clf_threshold: float = 0.5,
    on_w: float = 50.0,
    regressor_path: str | None = None,
    regressor_output_unit: str = "kw",  # your regressor outputs kW
    mean_w: float | None = None,
    max_appliance_w: float | None = None,
    max_mains_w: float | None = None,
    max_points: int | None = None,
):
    df_raw = build_aligned_df(h5_path, building, start, end, appliance, sample_period)

    # Sanity filters
    if max_appliance_w is not None:
        df_raw = df_raw[(df_raw["appliance"] >= 0) & (df_raw["appliance"] <= max_appliance_w)]
    if max_mains_w is not None:
        df_raw = df_raw[(df_raw["mains"] >= 0) & (df_raw["mains"] <= max_mains_w)]

    # Optional subsample for speed (keeps chronology)
    if max_points is not None and len(df_raw) > max_points:
        idx = np.linspace(0, len(df_raw) - 1, int(max_points)).astype(int)
        df_raw = df_raw.iloc[idx].copy()

    mains = df_raw["mains"].to_numpy(dtype=np.float32)
    gt = df_raw["appliance"].to_numpy(dtype=np.float32)
    ts = df_raw.index.to_numpy()

    X, centers = make_windows_two_channel(mains, window_size)
    if X is None:
        raise ValueError(f"Not enough points ({len(df_raw)}) for window_size={window_size}")

    gt_c = gt[centers]
    ts_c = ts[centers]

    classifier = load_model(classifier_path)
    probs = classifier.predict(X, verbose=0).reshape(-1)
    clf_pred = (probs >= clf_threshold).astype(np.int32)
    labels = (gt_c >= on_w).astype(np.int32)

    out = pd.DataFrame({
        "timestamp": pd.to_datetime(ts_c),
        "ground_truth": gt_c.astype(np.float32),
        "label": labels,
        "pred_label": clf_pred,
        "prob": probs.astype(np.float32),
    }).sort_values("timestamp")

    on_idx = np.where(clf_pred == 1)[0]

    # Gated regressor reconstruction
    gate_reg_metrics_total = None
    gate_reg_metrics_on = None

    if regressor_path is not None:
        regressor = load_model(regressor_path)
        pred_reg_w = np.zeros_like(gt_c, dtype=np.float32)

        if len(on_idx) > 0:
            X_on = X[on_idx].copy()

            # Your regressor expects kW inputs/outputs
            if regressor_output_unit.lower() == "kw":
                X_on /= 1000.0
                pr_kw = predict_regressor(regressor, X_on)
                pred_reg_w[on_idx] = pr_kw * 1000.0
            else:
                # if later your regressor uses Watts end-to-end
                pr = predict_regressor(regressor, X_on)
                pred_reg_w[on_idx] = pr

        out["pred_regressor"] = pred_reg_w
        gate_reg_metrics_total = compute_total_metrics(out["ground_truth"].values, out["pred_regressor"].values)
        gate_reg_metrics_on = compute_on_only_metrics(out["ground_truth"].values, out["pred_regressor"].values, on_w=on_w)

    # Gated mean reconstruction
    gate_mean_metrics_total = None
    gate_mean_metrics_on = None

    if mean_w is not None:
        pred_mean_w = np.zeros_like(gt_c, dtype=np.float32)
        pred_mean_w[on_idx] = float(mean_w)
        out["pred_mean"] = pred_mean_w
        gate_mean_metrics_total = compute_total_metrics(out["ground_truth"].values, out["pred_mean"].values)
        gate_mean_metrics_on = compute_on_only_metrics(out["ground_truth"].values, out["pred_mean"].values, on_w=on_w)

    gate_metrics = compute_gate_metrics(labels, clf_pred)

    return out, {
        "gate": gate_metrics,
        "regressor_total": gate_reg_metrics_total,
        "regressor_on": gate_reg_metrics_on,
        "mean_total": gate_mean_metrics_total,
        "mean_on": gate_mean_metrics_on,
    }
