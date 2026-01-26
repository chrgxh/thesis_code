from typing import Dict, Tuple, List
from generators_clean import (
    GeneratorConfig,
    DualBinaryClassifierGenerator,
    DualBinaryEvalGenerator,
    DualOnOnlyRegressionGenerator,
    DualOnOnlyRegressionEvalGenerator,
)
from configs import ClassifierTrainConfig, RegressorTrainConfig

def dict_to_regions(d: Dict[int, Tuple[str, str]]) -> List[tuple]:
    """{building: (start, end)} -> [(building, start, end), ...]"""
    return [(b, s, e) for b, (s, e) in d.items()]

def build_classification_gens(cfg: ClassifierTrainConfig):
    """
    Classifier generators:
      - train_gen: shuffled
      - val_gen  : not shuffled
      - val_eval : eval Sequence (not shuffled)

    Uses cfg.threshold (Watts) for ON/OFF label generation.
    """
    train_regions = dict_to_regions(cfg.train_config)
    val_regions = dict_to_regions(cfg.val_config)

    train_gen_cfg = GeneratorConfig(
        h5_path=cfg.h5_path,
        regions=train_regions,
        appliance_name=cfg.appliance,
        window_size=cfg.window_size,
        batch_size=cfg.batch_size,
        sample_period=cfg.sample_period,
        threshold=cfg.threshold,
        shuffle=True,
    )

    val_gen_cfg = GeneratorConfig(
        h5_path=cfg.h5_path,
        regions=val_regions,
        appliance_name=cfg.appliance,
        window_size=cfg.window_size,
        batch_size=cfg.batch_size,
        sample_period=cfg.sample_period,
        threshold=cfg.threshold,
        shuffle=False,
    )

    train_gen = DualBinaryClassifierGenerator(train_gen_cfg)
    val_gen = DualBinaryClassifierGenerator(val_gen_cfg)
    val_eval = DualBinaryEvalGenerator(val_gen_cfg)

    return train_gen, val_gen, val_eval

def build_regression_gens(cfg: RegressorTrainConfig):
    """
    ON-only regressor generators:
      - train_gen: shuffled
      - val_gen  : not shuffled
      - val_eval : eval Sequence (not shuffled)

    Uses cfg.on_threshold_w (Watts) to filter ON-only samples.
    """
    train_regions = dict_to_regions(cfg.train_config)
    val_regions = dict_to_regions(cfg.val_config)

    train_gen_cfg = GeneratorConfig(
        h5_path=cfg.h5_path,
        regions=train_regions,
        appliance_name=cfg.appliance,
        window_size=cfg.window_size,
        batch_size=cfg.batch_size,
        sample_period=cfg.sample_period,
        threshold=cfg.on_threshold_w,   # ON-only cutoff in Watts
        shuffle=True,
    )

    val_gen_cfg = GeneratorConfig(
        h5_path=cfg.h5_path,
        regions=val_regions,
        appliance_name=cfg.appliance,
        window_size=cfg.window_size,
        batch_size=cfg.batch_size,
        sample_period=cfg.sample_period,
        threshold=cfg.on_threshold_w,
        shuffle=False,
    )

    train_gen = DualOnOnlyRegressionGenerator(train_gen_cfg)
    val_gen = DualOnOnlyRegressionGenerator(val_gen_cfg)
    val_eval = DualOnOnlyRegressionEvalGenerator(val_gen_cfg)

    return train_gen, val_gen, val_eval
