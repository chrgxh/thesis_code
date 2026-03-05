import os
from configs import ClassifierTrainConfig, RegressorTrainConfig, ModelConfig
from trainer import train_classifier, train_regressor

# -----------------------------
# Edit these for your experiment
# -----------------------------
H5_PATH = os.getenv("H5_PATH", "data/h5s/example.h5")
BUILDING = 2
APPLIANCE = "washer dryer"

# Train/val splits
TRAIN_START, TRAIN_END = "2021-11-09", "2024-01-31"
VAL_START, VAL_END     = "2024-02-01", "2024-06-30"

# Data params
WINDOW_SIZE = 181
BATCH_SIZE = 64
SAMPLE_PERIOD = 10

# Label cutoff for ON/OFF (Watts)
ON_W = 50.0

# Class imbalance for classifier (tune per appliance)
CLASS_WEIGHT = {0: 1, 1: 5}

# Output directory
SAVE_DIR = "models"
os.makedirs(SAVE_DIR, exist_ok=True)

# -----------------------------
# Model + training configuration
# -----------------------------
appl_slug = APPLIANCE.replace(" ", "_")
clf_path = f"{SAVE_DIR}/clf_{appl_slug}_b{BUILDING}.h5"
reg_path = f"{SAVE_DIR}/reg_ononly_{appl_slug}_b{BUILDING}.h5"

model_cfg = ModelConfig(
    channels=2,
    clf_lr=1e-4,
    reg_lr=1e-4,
    clf_dropout=0.3,
    reg_dropout=0.2,
    huber_delta=0.2,
)

clf_train_cfg = ClassifierTrainConfig(
    h5_path=H5_PATH,
    appliance=APPLIANCE,
    train_config={BUILDING: (TRAIN_START, TRAIN_END)},
    val_config={BUILDING: (VAL_START, VAL_END)},
    window_size=WINDOW_SIZE,
    batch_size=BATCH_SIZE,
    sample_period=SAMPLE_PERIOD,
    threshold=ON_W,
    epochs=3,
    steps_per_epoch=None,
    validation_steps=None,
    class_weight=CLASS_WEIGHT,
    save_path=clf_path,
)

reg_train_cfg = RegressorTrainConfig(
    h5_path=H5_PATH,
    appliance=APPLIANCE,
    train_config={BUILDING: (TRAIN_START, TRAIN_END)},
    val_config={BUILDING: (VAL_START, VAL_END)},
    window_size=WINDOW_SIZE,
    batch_size=BATCH_SIZE,
    sample_period=SAMPLE_PERIOD,
    on_threshold_w=ON_W,
    epochs=10,
    steps_per_epoch=None,
    validation_steps=None,
    save_path=reg_path,
)

# -----------------------------
# Train classifier
# -----------------------------
clf_out = train_classifier(
    train_cfg=clf_train_cfg,
    model_cfg=model_cfg,
    threshold_eval=0.5,
    sweep_thresholds=True,
    sweep_plot=True,
    save_config_json=True,
)

print("\nClassifier saved to:", clf_out["model_path"])
print("Classifier metadata:", clf_out["json_path"])
print("Best threshold:", clf_out["best_threshold"])

# -----------------------------
# Train regressor
# -----------------------------
reg_out = train_regressor(
    train_cfg=reg_train_cfg,
    model_cfg=model_cfg,
    save_config_json=True,
)

print("\nRegressor saved to:", reg_out["model_path"])
print("Regressor metadata:", reg_out["json_path"])
print("Regressor watts metrics (MAE, RMSE, MaxAE):", reg_out["metrics_watts"])