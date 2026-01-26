from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, GlobalAveragePooling1D, Dense, BatchNormalization, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import Huber
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall
from configs import ModelConfig

def create_classification_model(window_size: int, cfg: ModelConfig):
    model = Sequential([
        Conv1D(20, 10, activation="relu",
               input_shape=(window_size, cfg.channels), padding="same"),
        BatchNormalization(),

        Conv1D(30, 8, activation="relu", padding="same"),
        BatchNormalization(),

        Conv1D(40, 6, activation="relu", padding="same"),
        BatchNormalization(),

        Conv1D(40, 5, activation="relu", padding="same"),
        BatchNormalization(),

        GlobalAveragePooling1D(),
        Dropout(cfg.clf_dropout),
        Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer=Adam(learning_rate=cfg.clf_lr),
        loss="binary_crossentropy",
        metrics=[
            BinaryAccuracy(name="acc"),
            Precision(name="prec"),
            Recall(name="rec"),
        ],
    )
    return model

def create_regression_model(window_size: int, cfg: ModelConfig):
    model = Sequential([
        Conv1D(32, 10, activation="relu",
               input_shape=(window_size, cfg.channels), padding="same"),
        BatchNormalization(),

        Conv1D(48, 8, activation="relu", padding="same"),
        BatchNormalization(),

        Conv1D(64, 6, activation="relu", padding="same"),
        BatchNormalization(),

        GlobalAveragePooling1D(),
        Dropout(cfg.reg_dropout),
        Dense(1, activation="linear"),
    ])

    model.compile(
        optimizer=Adam(learning_rate=cfg.reg_lr),
        loss=Huber(delta=cfg.huber_delta),
        metrics=["mae"],
    )
    return model
