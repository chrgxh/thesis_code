# generators_clean.py
import gc
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

from tensorflow.keras.utils import Sequence
from nilmtk import DataSet


Region = Tuple[int, str, str]  # (building, start_date, end_date)


@dataclass
class GeneratorConfig:
    h5_path: str
    regions: List[Region]
    appliance_name: str
    window_size: int = 301
    batch_size: int = 32
    sample_period: int = 6          # <-- BIG SPEED KNOB (try 30 or 60)
    threshold: float = 50.0         # label ON if appliance_power >= threshold
    shuffle: bool = True
    cache_in_memory: bool = True    # keep df chunks in RAM once loaded


class _MultiRegionBase(Sequence):
    """
    Loads multiple regions from NILMTK dataset into memory as joined (mains, appliance) dataframes,
    builds a list of valid center indices, and serves batches of windows.
    """

    def __init__(self, cfg: GeneratorConfig):
        self.cfg = cfg
        self.half = cfg.window_size // 2

        self._chunks = []   # list of joined DataFrames (mains/appliance)
        self._indices = []  # list of (chunk_id, center_idx)

        self._prepare()

        if self.cfg.shuffle:
            np.random.shuffle(self._indices)

    def _prepare(self):
        self._chunks.clear()
        self._indices.clear()

        for building, start, end in self.cfg.regions:
            gc.collect()
            ds = DataSet(self.cfg.h5_path)
            ds.set_window(start=start, end=end)

            elec = ds.buildings[building].elec

            mains = next(elec.mains().load(sample_period=self.cfg.sample_period))
            appl  = next(elec[self.cfg.appliance_name].load(sample_period=self.cfg.sample_period))

            mains.columns = ["mains"]
            appl.columns = ["appliance"]

            df = mains.join(appl, how="inner").dropna()
            if len(df) < self.cfg.window_size:
                continue

            chunk_id = len(self._chunks)
            centers = np.arange(self.half, len(df) - self.half)
            self._indices.extend([(chunk_id, i) for i in centers])

            if self.cfg.cache_in_memory:
                self._chunks.append(df)
            else:
                # If you ever want stream-from-disk later, you'd store region metadata instead.
                # Keeping it simple here: cache_in_memory=True is assumed for now.
                self._chunks.append(df)

    def __len__(self):
        return int(np.ceil(len(self._indices) / self.cfg.batch_size))

    def on_epoch_end(self):
        if self.cfg.shuffle:
            np.random.shuffle(self._indices)

    # Helpers
    def _get_batch_indices(self, batch_idx: int):
        bs = self.cfg.batch_size
        return self._indices[batch_idx * bs:(batch_idx + 1) * bs]


class DeltaBinaryClassifierGenerator(_MultiRegionBase):
    """
    Minimal generator for training a classifier on delta_mains only.

    Returns:
      X: (batch, window_size, 1)   where X is delta(mains_window)
      y: (batch,)                 binary label: 1 if appliance_power >= threshold else 0
    """

    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)

        X_delta = np.empty((len(batch), self.cfg.window_size), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.int32)

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window = df["mains"].iloc[center - self.half:center + self.half + 1].to_numpy()
            # delta with prepend so length stays window_size
            delta = np.diff(mains_window, prepend=mains_window[0])

            appl_power = df["appliance"].iloc[center]
            label = 1 if appl_power >= self.cfg.threshold else 0

            X_delta[j] = delta
            y[j] = label

        return X_delta[..., np.newaxis], y


class DeltaBinaryEvalGenerator(_MultiRegionBase):
    """
    Same as training generator but also returns timestamps for analysis.

    Returns:
      X_delta, y, ts
    """

    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)

        X_delta = np.empty((len(batch), self.cfg.window_size), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.int32)
        ts = []

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window = df["mains"].iloc[center - self.half:center + self.half + 1].to_numpy()
            delta = np.diff(mains_window, prepend=mains_window[0])

            appl_power = df["appliance"].iloc[center]
            label = 1 if appl_power >= self.cfg.threshold else 0

            X_delta[j] = delta
            y[j] = label
            ts.append(df.index[center])

        return X_delta[..., np.newaxis], y, ts
    
class DualBinaryClassifierGenerator(_MultiRegionBase):
    """
    Dual-input generator for training a classifier on BOTH mains and delta_mains.

    Returns:
      X: (batch, window_size, 2)  channels = [mains, delta]
      y: (batch,)
    """

    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)
        W = self.cfg.window_size

        X_mains = np.empty((len(batch), W), dtype=np.float32)
        X_delta = np.empty((len(batch), W), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.int32)

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window = df["mains"].iloc[
                center - self.half : center + self.half + 1
            ].to_numpy()

            delta = np.diff(mains_window, prepend=mains_window[0])

            appl_power = df["appliance"].iloc[center]
            y[j] = 1 if appl_power >= self.cfg.threshold else 0

            X_mains[j] = mains_window
            X_delta[j] = delta

        # (B, W, 1) + (B, W, 1) -> (B, W, 2)
        X = np.concatenate(
            [X_mains[..., np.newaxis], X_delta[..., np.newaxis]],
            axis=-1
        )
        return X, y


class DualBinaryEvalGenerator(_MultiRegionBase):
    """
    Dual-input eval generator that also returns timestamps.

    Returns:
      X: (batch, window_size, 2), y, ts
    """

    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)
        W = self.cfg.window_size

        X_mains = np.empty((len(batch), W), dtype=np.float32)
        X_delta = np.empty((len(batch), W), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.int32)
        ts = []

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window = df["mains"].iloc[
                center - self.half : center + self.half + 1
            ].to_numpy()

            delta = np.diff(mains_window, prepend=mains_window[0])

            appl_power = df["appliance"].iloc[center]
            y[j] = 1 if appl_power >= self.cfg.threshold else 0

            X_mains[j] = mains_window
            X_delta[j] = delta
            ts.append(df.index[center])

        X = np.concatenate(
            [X_mains[..., np.newaxis], X_delta[..., np.newaxis]],
            axis=-1
        )
        return X, y, ts

class DualOnOnlyRegressionGenerator(_MultiRegionBase):
    """
    Dual-input regression generator trained ONLY on ON states.

    ON definition: appliance_power >= cfg.threshold (use 50W)
    Returns:
      X: (batch, window_size, 2)  channels = [mains, delta]
      y: (batch,)                 appliance power at center (float)
    """

    def _prepare(self):
        # override to build indices ONLY where appliance is ON
        self._chunks.clear()
        self._indices.clear()

        for building, start, end in self.cfg.regions:
            gc.collect()
            ds = DataSet(self.cfg.h5_path)
            ds.set_window(start=start, end=end)

            elec = ds.buildings[building].elec
            mains = next(elec.mains().load(sample_period=self.cfg.sample_period))
            appl  = next(elec[self.cfg.appliance_name].load(sample_period=self.cfg.sample_period))

            mains.columns = ["mains"]
            appl.columns = ["appliance"]

            df = mains.join(appl, how="inner").dropna()
            df = df[(df["appliance"] >= 0) & (df["appliance"] <= 5000.0)] #Remove false values

            if len(df) < self.cfg.window_size:
                continue

            chunk_id = len(self._chunks)

            centers = np.arange(self.half, len(df) - self.half)

            # Keep only ON centers
            on_mask = df["appliance"].iloc[centers].to_numpy() >= self.cfg.threshold
            on_centers = centers[on_mask]

            if len(on_centers) == 0:
                continue

            self._indices.extend([(chunk_id, int(i)) for i in on_centers])
            self._chunks.append(df)

        if self.cfg.shuffle:
            np.random.shuffle(self._indices)

    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)
        W = self.cfg.window_size
        KW = 1000.0

        X_mains = np.empty((len(batch), W), dtype=np.float32)
        X_delta = np.empty((len(batch), W), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.float32)

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window_w = df["mains"].iloc[center - self.half:center + self.half + 1].to_numpy(dtype=np.float32)
            delta_window_w = np.diff(mains_window_w, prepend=mains_window_w[0]).astype(np.float32)

            appl_power_w = float(df["appliance"].iloc[center])  # target in Watts

            # scale to kW
            X_mains[j] = mains_window_w / KW
            X_delta[j] = delta_window_w / KW
            y[j] = appl_power_w / KW

        X = np.concatenate([X_mains[..., None], X_delta[..., None]], axis=-1)  # (B, W, 2)
        return X, y


class DualOnOnlyRegressionEvalGenerator(DualOnOnlyRegressionGenerator):
    """
    Same as DualOnOnlyRegressionGenerator but returns timestamps too.
    Returns: X, y, ts
    """
    def __getitem__(self, batch_idx: int):
        batch = self._get_batch_indices(batch_idx)
        W = self.cfg.window_size
        KW = 1000.0

        X_mains = np.empty((len(batch), W), dtype=np.float32)
        X_delta = np.empty((len(batch), W), dtype=np.float32)
        y = np.empty((len(batch),), dtype=np.float32)
        ts = []

        for j, (chunk_id, center) in enumerate(batch):
            df = self._chunks[chunk_id]

            mains_window_w = df["mains"].iloc[center - self.half:center + self.half + 1].to_numpy(dtype=np.float32)
            delta_window_w = np.diff(mains_window_w, prepend=mains_window_w[0]).astype(np.float32)

            appl_power_w = float(df["appliance"].iloc[center])

            # scale to kW
            X_mains[j] = mains_window_w / KW
            X_delta[j] = delta_window_w / KW
            y[j] = appl_power_w / KW
            ts.append(df.index[center])

        X = np.concatenate([X_mains[..., None], X_delta[..., None]], axis=-1)
        return X, y, ts
