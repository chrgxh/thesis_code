from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def find_active_days(dataset, building_ids, appliance_type='dish washer', min_energy_per_day=100):
    results = defaultdict(list)

    for b in building_ids:
        print(f"🔍 Scanning building {b}...")
        appliances = dataset.buildings[b].elec.select_using_appliances(type=appliance_type)
        if len(appliances.meters) == 0:
            print(f"❌ No '{appliance_type}' found in building {b}")
            continue

        meter = appliances.meters[0]
        try:
            power_series = meter.power_series(sample_period=60)
            df = next(power_series)
            df = df.dropna()
            df = df[df > 0]  # remove 0-Watt readings
            df.index = pd.to_datetime(df.index)

            daily_energy = df.resample('D').sum()

            active_days = daily_energy[daily_energy > min_energy_per_day]
            for date in active_days.index[:5]:  # grab first 5 active days
                results[b].append(date.strftime('%Y-%m-%d'))

            print(f"✅ Found {len(active_days)} active days in building {b}. Sample: {results[b]}")

        except Exception as e:
            print(f"⚠️ Error in building {b}: {e}")
    
    return results

def analyze_generator(generator, max_batches=10, appliance_scale=3000, dual=False):
    building_data = {}

    # Collect data grouped by building (df_id)
    for i in range(min(len(generator), max_batches)):
        X_batch, y_batch, ts_batch = generator.get_with_timestamps(i)

        if dual:
            mains_batch = X_batch['mains'].squeeze(-1)
        else:
            mains_batch = X_batch.squeeze(-1)

        appliance_batch = y_batch
        if isinstance(y_batch, dict):
            appliance_batch = y_batch.get('regression') or y_batch.get('classification')

        for j, ts in enumerate(ts_batch):
            building_id = generator.indices[i * generator.batch_size + j][0]  # df_id
            if building_id not in building_data:
                building_data[building_id] = {
                    'mains': [],
                    'appliance': [],
                    'timestamp': []
                }
            building_data[building_id]['mains'].append(mains_batch[j])
            building_data[building_id]['appliance'].append(appliance_batch[j])
            building_data[building_id]['timestamp'].append(ts)

    # Plot per building
    for building_id, data in building_data.items():
        mains = np.vstack(data['mains'])
        appliance = np.hstack(data['appliance'])
        mains_center = np.mean(mains, axis=1)

        if np.max(appliance) == 1.0 and np.min(appliance) == 0.0:
            scaled_appliance = appliance * appliance_scale
        else:
            scaled_appliance = appliance

        df_plot = pd.DataFrame({
            'timestamp': pd.to_datetime(data['timestamp']),
            'mains': mains_center,
            'appliance': scaled_appliance,
            'appliance_raw': appliance
        }).sort_values('timestamp')

        # Plot signals
        plt.figure(figsize=(18, 4))
        plt.plot(df_plot['timestamp'], df_plot['mains'], label="Mains (avg window)", alpha=0.7)
        plt.plot(df_plot['timestamp'], df_plot['appliance'], label=f"Appliance (x{appliance_scale} if binary)", alpha=0.7, color='orange')
        plt.title(f"Building {building_id} - Sample Time Series")
        plt.xlabel("Time")
        plt.ylabel("Power (Watts)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot appliance only
        plt.figure(figsize=(18, 3))
        plt.plot(df_plot['timestamp'], df_plot['appliance_raw'], color='orange', label="Appliance (raw)")
        plt.title(f"Building {building_id} - Appliance Signal")
        plt.xlabel("Time")
        plt.ylabel("Binary State" if np.array_equal(appliance, appliance.astype(bool)) else "Power")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Print stats
        zero_pct_mains = (mains == 0).sum() / mains.size * 100
        zero_pct_appliance = (appliance == 0).sum() / len(appliance) * 100

        print(f"🏠 Building {building_id}")
        print(f"🔌 Mains: {zero_pct_mains:.2f}% zero values")
        print(f"⚙️ Appliance: {zero_pct_appliance:.2f}% zero values\n")

def analyze_gated_generator(generator, max_batches=10, appliance_scale=3000):
    building_data = {}

    for i in range(min(len(generator), max_batches)):
        X_batch, delta_batch, y_batch, ts_batch = generator.get_with_timestamps(i)

        mains_batch = X_batch.squeeze(-1)
        appliance_batch = y_batch

        for j, ts in enumerate(ts_batch):
            building_id = generator.indices[i * generator.batch_size + j][0]

            if building_id not in building_data:
                building_data[building_id] = {
                    'mains': [],
                    'appliance': [],
                    'timestamp': []
                }

            building_data[building_id]['mains'].append(mains_batch[j])
            building_data[building_id]['appliance'].append(appliance_batch[j])
            building_data[building_id]['timestamp'].append(ts)

    # Plot per building
    for building_id, data in building_data.items():
        mains = np.vstack(data['mains'])
        appliance = np.hstack(data['appliance'])
        mains_center = np.mean(mains, axis=1)

        if np.max(appliance) == 1.0 and np.min(appliance) == 0.0:
            scaled_appliance = appliance * appliance_scale
        else:
            scaled_appliance = appliance

        df_plot = pd.DataFrame({
            'timestamp': pd.to_datetime(data['timestamp']),
            'mains': mains_center,
            'appliance': scaled_appliance,
            'appliance_raw': appliance
        }).sort_values('timestamp')

        # Plot signals
        plt.figure(figsize=(18, 4))
        plt.plot(df_plot['timestamp'], df_plot['mains'], label="Mains (avg window)", alpha=0.7)
        plt.plot(df_plot['timestamp'], df_plot['appliance'], label=f"Appliance (x{appliance_scale} if binary)", alpha=0.7, color='orange')
        plt.title(f"Building {building_id} - Sample Time Series")
        plt.xlabel("Time")
        plt.ylabel("Power (Watts)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot appliance only
        plt.figure(figsize=(18, 3))
        plt.plot(df_plot['timestamp'], df_plot['appliance_raw'], color='orange', label="Appliance (raw)")
        plt.title(f"Building {building_id} - Appliance Signal")
        plt.xlabel("Time")
        plt.ylabel("Binary State" if np.array_equal(appliance, appliance.astype(bool)) else "Power")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Print stats
        zero_pct_mains = (mains == 0).sum() / mains.size * 100
        zero_pct_appliance = (appliance == 0).sum() / len(appliance) * 100

        print(f"🏠 Building {building_id}")
        print(f"🔌 Mains: {zero_pct_mains:.2f}% zero values")
        print(f"⚙️ Appliance: {zero_pct_appliance:.2f}% zero values\n")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def analyze_minimal_generator(generator, max_batches=10, appliance_scale=3000):
    building_data = {}

    for i in range(min(len(generator), max_batches)):
        X_batch, y_batch, ts_batch = generator[i]

        mains_window = X_batch["mains"].squeeze(-1)
        mains_center = X_batch["mains_center"]
        appliance_batch = y_batch

        for j, ts in enumerate(ts_batch):
            df_chunk_id = generator.indices[i * generator.batch_size + j][0]
            building_id = generator.building_ids[df_chunk_id]


            if building_id not in building_data:
                building_data[building_id] = {
                    'mains': [],
                    'mains_center': [],
                    'appliance': [],
                    'timestamp': []
                }

            building_data[building_id]['mains'].append(mains_window[j])
            building_data[building_id]['mains_center'].append(mains_center[j])
            building_data[building_id]['appliance'].append(appliance_batch[j])
            building_data[building_id]['timestamp'].append(ts)

    # === Plot per building ===
    for building_id, data in building_data.items():
        mains_windowed = np.vstack(data['mains'])
        mains_center = np.array(data['mains_center'])
        appliance = np.hstack(data['appliance'])

        mains_window_avg = np.mean(mains_windowed, axis=1)

        if np.max(appliance) == 1.0 and np.min(appliance) == 0.0:
            scaled_appliance = appliance * appliance_scale
        else:
            scaled_appliance = appliance

        df_plot = pd.DataFrame({
            'timestamp': pd.to_datetime(data['timestamp']),
            'mains_avg': mains_window_avg,
            'mains_center': mains_center,
            'appliance': scaled_appliance,
            'appliance_raw': appliance
        })

        df_plot = df_plot.sort_values('timestamp')

        # Plot signals
        plt.figure(figsize=(18, 4))
        plt.plot(df_plot['timestamp'], df_plot['mains_avg'], label="Mains (avg window)", alpha=0.6)
        plt.plot(df_plot['timestamp'], df_plot['mains_center'], label="Mains (original)", color='green', alpha=0.9, linestyle='--')
        plt.plot(df_plot['timestamp'], df_plot['appliance'], label="Appliance", alpha=0.7, color='orange')
        plt.title(f"Building {building_id} - Sample Time Series")
        plt.xlabel("Time")
        plt.ylabel("Power (Watts)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # Plot appliance only
        plt.figure(figsize=(18, 3))
        plt.plot(df_plot['timestamp'], df_plot['appliance_raw'], color='orange', label="Appliance (raw)")
        plt.title(f"Building {building_id} - Appliance Signal")
        plt.xlabel("Time")
        plt.ylabel("Binary State" if np.array_equal(appliance, appliance.astype(bool)) else "Power")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Print stats
        zero_pct_mains = (mains_windowed == 0).sum() / mains_windowed.size * 100
        zero_pct_appliance = (appliance == 0).sum() / len(appliance) * 100

        print(f"🏠 Building {building_id}")
        print(f"🔌 Mains (windowed): {zero_pct_mains:.2f}% zero values")
        print(f"⚙️ Appliance: {zero_pct_appliance:.2f}% zero values\n")
        print(f"🔌 Total Mains: {mains_windowed.size} values")
        print(f"⚙️ Total Appliance: {len(appliance)} values\n")
