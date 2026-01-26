from dataclasses import dataclass
from typing import Dict, Tuple, Optional

@dataclass(frozen=True)
class ModelConfig:
    channels: int = 2

    clf_lr: float = 1e-4
    reg_lr: float = 3e-4

    clf_dropout: float = 0.3
    reg_dropout: float = 0.2

    huber_delta: float = 0.2

@dataclass
class BaseTrainConfig:
    # data
    h5_path: str
    appliance: str
    train_config: Dict[int, Tuple[str, str]]
    val_config: Dict[int, Tuple[str, str]]

    window_size: int = 301
    batch_size: int = 256
    sample_period: int = 30

    # fitting
    epochs: int = 10
    steps_per_epoch: Optional[int] = None
    validation_steps: Optional[int] = None

    # output
    save_path: str = "models/model.h5"

@dataclass
class ClassifierTrainConfig(BaseTrainConfig):
    # label / gate threshold for ON/OFF (Watts)
    threshold: float = 50.0

    # imbalance handling
    class_weight: Optional[dict] = None

@dataclass
class RegressorTrainConfig(BaseTrainConfig):
    # ON-only cutoff for regression training (Watts)
    on_threshold_w: float = 50.0
