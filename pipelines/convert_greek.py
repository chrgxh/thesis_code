import pandas as pd
import numpy as np
from copy import deepcopy
from os.path import join, isdir, isfile, exists
from os import listdir
import fnmatch
import re
from sys import stdout
from nilmtk.utils import get_datastore
from nilmtk.datastore import Key
from nilmtk.timeframe import TimeFrame
from nilmtk.measurement import LEVEL_NAMES
from nilmtk.utils import get_module_directory, check_directory_exists
from nilm_metadata import convert_yaml_to_hdf5, save_yaml_to_datastore


def convert_greek(input_path, metadata_path, output_filename, format='HDF'):
    """
    Parameters
    ----------
    input_path : str
        The root path of the CSV files, e.g. House1.csv
    output_filename : str
        The destination filename (including path and suffix).
    format : str
        format of output. Either 'HDF' or 'CSV'. Defaults to 'HDF'
    """
        
    # Open DataStore
    store = get_datastore(output_filename, format, mode='w')

    # Convert raw data to DataStore
    _convert(input_path, store, 'Europe/Athens')

    # Use convert_yaml_to_hdf5 to convert YAML metadata to HDF5
    try:
        print("Converting YAML to HDF5 metadata...")
        convert_yaml_to_hdf5(metadata_path, output_filename)
        print("Metadata successfully converted.")
    except Exception as e:
        print(f"Error during YAML to HDF5 conversion: {e}")

    store.close()
    print("Done converting GREEK to HDF5!")

    # Add metadata
    ##save_yaml_to_datastore('/Users/user/Desktop/DAE-main 2/greek_data/greek/greek/metadata', store)

    # save_yaml_to_datastore(join(get_module_directory(), 
    #                           'dataset_converters', 
    #                           'greek', 
    #                           'metadata'),
    #                      store)
    # store.close()

    print("Done converting GREEK to HDF5!")

def _convert(input_path, store, tz, sort_index=True):
    """
    Parameters
    ----------
    input_path : str
        The root path of the GREEK dataset.
    store : DataStore
        The NILMTK DataStore object.
    tz : str 
        Timezone e.g. 'US/Eastern'
    sort_index : bool
    """

    check_directory_exists(input_path)
    nilmtk_house_id = 0
    prefix = 'combined_main_and_meters_'
    version_checked = False
    
    # Define the columns for the house with the most appliances (e.g., house 7)
    columns = ['timestamp', 'power_data_main', 'power_data_meter_1', 'power_data_meter_2', 
               'power_data_meter_3', 'power_data_meter_4', 'power_data_meter_5', 
               'power_data_meter_6']
    
    for house_id in range(1,27):
        nilmtk_house_id += 1
        print("Loading house", house_id, end="... ")
        stdout.flush()
        
        csv_filename = join(input_path, prefix + str(house_id) + '.csv')
        
        if not version_checked:
            version_checked = True
            if exists(csv_filename):
                print('Using original filenames (combined_main_and_meters_XX.csv)')
                
        if not exists(csv_filename):
            raise RuntimeError('Could not find GREEK files. Please check the provided folder.')
        
        # Load CSV file with consistent columns (adding missing columns as NaN)
        df = _load_csv(csv_filename, columns, tz)
        if sort_index:
            df = df.sort_index()  # Ensure timestamps are sorted
            
        chan_id = 0
        for col in df.columns:
            chan_id += 1
            print(chan_id, end=" ")
            stdout.flush()
            
            key = Key(building=nilmtk_house_id, meter=chan_id)
            
            chan_df = pd.DataFrame(df[col])
            chan_df.columns = pd.MultiIndex.from_tuples([('power', 'active')])

            # Modify the column labels to reflect the power measurements recorded.
            chan_df.columns.set_names(LEVEL_NAMES, inplace=True)
            
            store.put(str(key), chan_df)
            
        print('')


def _load_csv(filename, columns, tz):
    """
    Parameters
    ----------
    filename : str
    columns : list of columns to keep
    tz : str e.g. 'US/Eastern'

    Returns
    -------
    dataframe
    """
    # Load data with the specified columns (usecols)
    df = pd.read_csv(filename, usecols=lambda col: col in columns or col == 'timestamp')
    
    # Fill missing columns with NaN if they don't exist
    for col in columns:
        if col not in df.columns and col != 'timestamp':
            df[col] = np.nan
    
    # Convert the integer index column to timezone-aware datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    df.set_index('timestamp', inplace=True)
    df = df.tz_convert(tz)

    return df

if __name__ == '__main__':
    input_path=r"D:\thesis_code\my_code\pipelines\data"
    output_path=r"D:\thesis_code\my_code\pipelines\data\third_test.h5"
    metadata_path=r"D:\thesis_code\my_code\pipelines\metadata"
    convert_greek(input_path,metadata_path,output_path)