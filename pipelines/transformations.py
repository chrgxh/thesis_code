import pandas as pd

def remove_milliseconds(df:pd.DataFrame,timestamp_col="timestamp")->pd.DataFrame:
    df[timestamp_col] = pd.to_datetime(df[timestamp_col]) # Ensure the timestamp column is a datetime type
    df[timestamp_col] = df[timestamp_col].dt.floor('S')
    return df

def aggregate_power(df:pd.DataFrame)->pd.DataFrame:
    #Average power for same device_id, timestamp, and phase
    df_avg = df.groupby(['device_id', 'timestamp', 'phase'], as_index=False).agg({'power_data': 'mean'})

    #Sum power for same device_id and timestamp across different phases
    df_final = df_avg.groupby(['device_id', 'timestamp'], as_index=False).agg({'power_data': 'sum'})
    return df_final

def map_device_id(df:pd.DataFrame, mapping_dict:dict)->pd.DataFrame:
    """
    Assigns a number to each device_id based on a given mapping dictionary.
    
    If a device_id is not found in the mapping dictionary, raises a KeyError.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing a 'device_id' column.
    mapping_dict (dict): A dictionary mapping each device_id to a unique number.

    Returns:
    pd.DataFrame: The DataFrame with 'devie_id' column replaced by the mapped number.
    
    Raises:
    KeyError: If a device_id does not exist in mapping dictionary.
    """
    
    # Check for any device_id not in the mapping_dict
    unknown_ids = set(df['device_id']) - set(mapping_dict.keys())
    
    if unknown_ids:
        raise KeyError(f"Device IDs not found in mapping dictionary: {unknown_ids}")

    # Apply the mapping
    df['device_id'] = df['device_id'].map(mapping_dict).astype(int)
    
    return df

def reshape_power_data(df: pd.DataFrame, num_devices: int) -> pd.DataFrame:
    """
    Transforms a DataFrame by ensuring no duplicate device_id per timestamp 
    and reshaping it to have separate columns for each device's power data.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame with columns ['device_id', 'timestamp', 'power_data'].
    num_devices (int): The total number of power_data_meter_* columns to include.

    Returns:
    pd.DataFrame: A DataFrame with 'timestamp' as index and power_data columns from 0 to num_devices-1.

    Raises:
    ValueError: If duplicate 'device_id' values exist for any 'timestamp'.
    """
    # Check for duplicate device_id per timestamp
    if df.duplicated(subset=['timestamp', 'device_id']).any():
        raise ValueError("Duplicate device_id values found for the same timestamp.")

    # Pivot the DataFrame to reshape it
    df_pivot = df.pivot(index='timestamp', columns='device_id', values='power_data')

    # Ensure all required device_id columns exist (fill missing ones with NaN)
    all_device_ids = list(range(num_devices))  # Ensure columns exist from 0 to num_devices-1
    df_pivot = df_pivot.reindex(columns=all_device_ids)

    # Rename columns: 0 → power_data_main, others → power_data_meter_N
    column_names = {0: 'power_data_main'}
    column_names.update({i: f'power_data_meter_{i}' for i in range(1, num_devices)})

    df_pivot.rename(columns=column_names, inplace=True)

    # Reset index to keep timestamp as a column
    df_pivot.reset_index(inplace=True)

    df_pivot.columns.name = None #Removes device_id metadata column

    return df_pivot

def apply_transformations(df: pd.DataFrame, *transforms) -> pd.DataFrame:
    """
    Applies multiple transformation functions sequentially to a DataFrame.
    
    Each transformation can either be:
    - A function that only takes `df` as input.
    - A tuple `(function, args, kwargs)`, where `args` and `kwargs` are optional positional and keyword arguments.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    *transforms: Transformation functions or tuples of (function, args, kwargs).

    Returns:
    pd.DataFrame: The transformed DataFrame.

    Raises:
    Exception: If a transformation function fails, it raises an error with the function name and the original exception.
    """
    for transform in transforms:
        try:
            if isinstance(transform, tuple):
                func, *args = transform
                df = func(df, *args)  # Call function with arguments
            else:
                df = transform(df)  # Call function normally if no extra args
        except Exception as ex:
            raise Exception(f"[{type(ex).__name__}] Error in transformation '{func.__name__ if isinstance(transform, tuple) else transform.__name__}': {ex}")
    
    return df

if __name__ == "__main__":
    raise RuntimeError("This file cannot be run as __main__.")