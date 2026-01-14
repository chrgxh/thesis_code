import numpy as np
from tensorflow.keras.utils import Sequence
from nilmtk import DataSet
import gc

class MultiRegionClassificationGenerator(Sequence):
    def __init__(self, h5_path, regions, appliance_name, window_size=301, batch_size=32, threshold=10, shuffle=True):
        self.h5_path = h5_path
        self.regions = regions  # List of (building, start_date, end_date)
        self.appliance_name = appliance_name
        self.window_size = window_size
        self.batch_size = batch_size
        self.threshold = threshold
        self.shuffle = shuffle
        self.half_window = window_size // 2

        self.df_chunks = []  # list of DataFrames
        self.indices = []    # (chunk_idx, center_idx)

        self._prepare_indices()

    def _prepare_indices(self):
        for building, start, end in self.regions:
            ds = None  # allow garbage collection of previous dataset
            gc.collect()
            ds = DataSet(self.h5_path)
            ds.set_window(start=start, end=end)
            elec = ds.buildings[building].elec

            mains = next(elec.mains().load(sample_period=6))
            appliance = next(elec[self.appliance_name].load(sample_period=6))

            mains.columns = ["mains"]
            appliance.columns = ["appliance"]

            df = mains.join(appliance, how="inner").dropna()

            if len(df) < self.window_size:
                continue

            local_indices = np.arange(self.half_window, len(df) - self.half_window)
            self.indices.extend([(len(self.df_chunks), i) for i in local_indices])
            self.df_chunks.append(df)

        if self.shuffle:
            np.random.shuffle(self.indices)

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        """Used by model.fit — returns (X, y) only."""
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_batch, y_batch = [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            appliance_power = df['appliance'].iloc[center_idx]

            label = float(appliance_power > self.threshold)

            X_batch.append(mains_window)
            y_batch.append(label)

        X_batch = np.array(X_batch)[..., np.newaxis]
        y_batch = np.array(y_batch)

        return X_batch, y_batch

    def get_with_timestamps(self, idx):
        """Used for visualization — returns (X, y, timestamps)."""
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_batch, y_batch, ts_batch = [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            appliance_power = df['appliance'].iloc[center_idx]
            timestamp = df.index[center_idx]

            label = float(appliance_power > self.threshold)

            X_batch.append(mains_window)
            y_batch.append(label)
            ts_batch.append(timestamp)

        X_batch = np.array(X_batch)[..., np.newaxis]
        y_batch = np.array(y_batch)

        return X_batch, y_batch, ts_batch

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

class MultiRegionRegressionGenerator(Sequence):
    def __init__(self, h5_path, regions, appliance_name,
                 window_size=301, batch_size=32,
                 max_main=20000, max_appliance=10000,
                 min_appliance_on=100,
                 dual_input=False, shuffle=True):
        self.h5_path = h5_path
        self.regions = regions
        self.appliance_name = appliance_name
        self.window_size = window_size
        self.batch_size = batch_size
        self.max_main = max_main
        self.max_appliance = max_appliance
        self.min_appliance_on = min_appliance_on
        self.dual_input = dual_input
        self.shuffle = shuffle
        self.half_window = window_size // 2

        self.df_chunks = []
        self.indices = []

        self._prepare_indices()

    def _prepare_indices(self):
        for building, start, end in self.regions:
            ds = None
            gc.collect()
            ds = DataSet(self.h5_path)
            ds.set_window(start=start, end=end)
            elec = ds.buildings[building].elec

            mains = next(elec.mains().load(sample_period=6))
            appliance = next(elec[self.appliance_name].load(sample_period=6))

            mains.columns = ["mains"]
            appliance.columns = ["appliance"]

            df = mains.join(appliance, how="inner").dropna()

            df = df[
                (df['mains'] > 0) &
                (df['appliance'] > 0) &
                (df['mains'] <= self.max_main) &
                (df['appliance'] <= self.max_appliance)
            ]

            if len(df) < self.window_size:
                continue

            local_indices = np.arange(self.half_window, len(df) - self.half_window)
            valid_indices = [
                i for i in local_indices
                if df['appliance'].iloc[i] >= self.min_appliance_on
            ]

            if valid_indices:
                self.indices.extend([(len(self.df_chunks), i) for i in valid_indices])
                self.df_chunks.append(df)

        if self.shuffle:
            np.random.shuffle(self.indices)

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch = [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]

            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(appliance_power)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)

        if self.dual_input:
            return {"mains": X_raw, "delta_mains": X_delta}, y_batch
        else:
            return X_raw, y_batch

    def get_with_timestamps(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch, ts_batch = [], [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]
            timestamp = df.index[center_idx]

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(appliance_power)
            ts_batch.append(timestamp)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)

        if self.dual_input:
            return {"mains": X_raw, "delta_mains": X_delta}, y_batch, ts_batch
        else:
            return X_raw, y_batch, ts_batch

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

class MultiRegionGatedGenerator(Sequence):
    def __init__(self, h5_path, regions, appliance_name,
                 window_size=301, batch_size=32, dual_input=True):
        self.h5_path = h5_path
        self.regions = regions  # list of (building, start, end)
        self.appliance_name = appliance_name
        self.window_size = window_size
        self.batch_size = batch_size
        self.dual_input = dual_input
        self.half_window = window_size // 2

        self.df_chunks = []
        self.indices = []

        self._prepare_indices()

    def _prepare_indices(self):
        for building, start, end in self.regions:
            gc.collect()
            ds = DataSet(self.h5_path)
            ds.set_window(start=start, end=end)
            elec = ds.buildings[building].elec

            mains = next(elec.mains().load())
            appliance = next(elec[self.appliance_name].load())

            mains.columns = ["mains"]
            appliance.columns = ["appliance"]
            df = mains.join(appliance, how="inner").dropna()

            if len(df) < self.window_size:
                continue

            local_indices = np.arange(self.half_window, len(df) - self.half_window)
            self.indices.extend([(len(self.df_chunks), i) for i in local_indices])
            self.df_chunks.append(df)

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch = [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]  # ← ORIGINAL VALUE

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(appliance_power)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)

        if self.dual_input:
            return {"mains": X_raw, "delta_mains": X_delta}, y_batch
        else:
            return X_raw, y_batch

    def get_with_timestamps(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch, ts_batch = [], [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]
            timestamp = df.index[center_idx]

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(appliance_power)
            ts_batch.append(timestamp)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)

        if self.dual_input:
            return {"mains": X_raw, "delta_mains": X_delta}, y_batch, ts_batch
        else:
            return X_raw, y_batch, ts_batch

    def on_epoch_end(self):
        pass  # No shuffling ever

from tensorflow.keras.utils import Sequence
import numpy as np
import gc
from nilmtk import DataSet

from tensorflow.keras.utils import Sequence
import numpy as np
import gc
from nilmtk import DataSet

class MinimalGatedGenerator(Sequence):
    def __init__(self, h5_path, regions, appliance_name, window_size=301, batch_size=32):
        self.h5_path = h5_path
        self.regions = regions  # list of (building, start, end)
        self.appliance_name = appliance_name
        self.window_size = window_size
        self.batch_size = batch_size
        self.half_window = window_size // 2

        self.df_chunks = []       # stores DataFrames
        self.building_ids = []    # actual building numbers per df_chunk
        self.indices = []         # list of (df_chunk_idx, center_idx)

        self._prepare_indices()

    def _prepare_indices(self):
        for building, start, end in self.regions:
            gc.collect()
            ds = DataSet(self.h5_path)  # ← FIX: open fresh for each building
            ds.set_window(start=start, end=end)
            elec = ds.buildings[building].elec

            mains = next(elec.mains().load())
            appliance = next(elec[self.appliance_name].load())

            mains.columns = ["mains"]
            appliance.columns = ["appliance"]

            df = mains.join(appliance, how="inner").dropna()

            if len(df) < self.window_size:
                continue

            df_chunk_idx = len(self.df_chunks)
            local_indices = np.arange(self.half_window, len(df) - self.half_window)
            self.indices.extend([(df_chunk_idx, i) for i in local_indices])
            self.df_chunks.append(df)
            self.building_ids.append(building)

        print(f"[INFO] Loaded {len(self.df_chunks)} regions for buildings: {self.building_ids}")

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch, ts_batch, mains_center = [], [], [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]
            timestamp = df.index[center_idx]
            mains_center_value = df['mains'].iloc[center_idx]

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(appliance_power)
            ts_batch.append(timestamp)
            mains_center.append(mains_center_value)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)
        mains_center = np.array(mains_center)

        return {"mains": X_raw, "delta_mains": X_delta, "mains_center": mains_center}, y_batch, ts_batch



class MinimalBinaryGatedGenerator(Sequence):
    def __init__(self, h5_path, regions, appliance_name, window_size=301, batch_size=32, threshold=50, shuffle=True):
        self.h5_path = h5_path
        self.regions = regions  # list of (building, start, end)
        self.appliance_name = appliance_name
        self.window_size = window_size
        self.batch_size = batch_size
        self.threshold = threshold
        self.shuffle = shuffle
        self.half_window = window_size // 2

        self.df_chunks = []       # stores DataFrames
        self.building_ids = []    # actual building numbers per df_chunk
        self.indices = []         # list of (df_chunk_idx, center_idx)

        self._prepare_indices()
        self.on_epoch_end()

    def _prepare_indices(self):
        for building, start, end in self.regions:
            gc.collect()
            ds = DataSet(self.h5_path)
            ds.set_window(start=start, end=end)
            elec = ds.buildings[building].elec

            mains = next(elec.mains().load())
            appliance = next(elec[self.appliance_name].load())

            mains.columns = ["mains"]
            appliance.columns = ["appliance"]

            df = mains.join(appliance, how="inner").dropna()

            if len(df) < self.window_size:
                continue

            df_chunk_idx = len(self.df_chunks)
            local_indices = np.arange(self.half_window, len(df) - self.half_window)
            self.indices.extend([(df_chunk_idx, i) for i in local_indices])
            self.df_chunks.append(df)
            self.building_ids.append(building)

    def __len__(self):
        return int(np.ceil(len(self.indices) / self.batch_size))

    def __getitem__(self, idx):
        batch = self.indices[idx * self.batch_size:(idx + 1) * self.batch_size]

        X_raw, X_delta, y_batch, ts_batch, mains_center = [], [], [], [], []

        for df_id, center_idx in batch:
            df = self.df_chunks[df_id]
            mains_window = df['mains'].iloc[center_idx - self.half_window:center_idx + self.half_window + 1].values
            delta_window = np.diff(mains_window, prepend=mains_window[0])
            appliance_power = df['appliance'].iloc[center_idx]
            timestamp = df.index[center_idx]
            mains_center_value = df['mains'].iloc[center_idx]

            binary_label = 1 if appliance_power >= self.threshold else 0

            X_raw.append(mains_window)
            X_delta.append(delta_window)
            y_batch.append(binary_label)
            ts_batch.append(timestamp)
            mains_center.append(mains_center_value)

        X_raw = np.array(X_raw)[..., np.newaxis]
        X_delta = np.array(X_delta)[..., np.newaxis]
        y_batch = np.array(y_batch)
        mains_center = np.array(mains_center)

        return {"mains": X_raw, "delta_mains": X_delta, "mains_center": mains_center}, y_batch, ts_batch

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)

class DeltaOnlyWrapper(Sequence):
    def __init__(self, gen):
        self.gen = gen
    def __len__(self):
        return len(self.gen)
    def __getitem__(self, idx):
        (X, y, _) = self.gen[idx]
        return X["delta_mains"], y
    def on_epoch_end(self):
        self.gen.on_epoch_end()

def normalize_dual_channel(mains_window, delta_window):
    # mains normalization (per window)
    m_mean, m_std = np.mean(mains_window), np.std(mains_window)
    if m_std == 0: m_std = 1.0
    mains_norm = (mains_window - m_mean) / m_std

    # delta normalization (per window)
    d_mean, d_std = np.mean(delta_window), np.std(delta_window)
    if d_std == 0: d_std = 1.0
    delta_norm = (delta_window - d_mean) / d_std

    # shape -> (window_size, 2)
    return np.stack([mains_norm, delta_norm], axis=-1)

class DualChannelWrapper(Sequence):
    def __init__(self, gen):
        self.gen = gen

    def __len__(self):
        return len(self.gen)

    def __getitem__(self, idx):
        (X_dict, y, _) = self.gen[idx]  
        mains = X_dict["mains"].squeeze(-1)
        delta = X_dict["delta_mains"].squeeze(-1)
        X_dual = np.array([
            normalize_dual_channel(mains[i], delta[i])
            for i in range(len(mains))
        ])
        return X_dual, y

    def on_epoch_end(self):
        self.gen.on_epoch_end()

