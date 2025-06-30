import pandas as pd
import numpy as np
import pickle
#####
from keras.models import load_model, Sequential
import keras.layers as layer
from nilmtk.legacy.disaggregate import Disaggregator


class DA(Disaggregator):

    def __init__(self, sequence_length):
        
        self.sequence_length = sequence_length # the length of input sequences for the model
        self.denoising_autoencoder_model = self.denoising_autoencoder_model_creation(self.sequence_length)
        self.max_dataset_value = None
        self.train_meter_metadata = None
        

    '''
    we create the neural network that is going to be trained using the power consumption
    of an entire house and the consumption of a specific appliance
    '''
    def denoising_autoencoder_model_creation(self, sequence_length):
        
        denoising_autoencoder = Sequential(
            [
                # A 1D convolutional layer for feature extraction from the time series data.
                layer.Conv1D(kernel_size=4, strides=1, filters=8, activation="linear", input_shape=(sequence_length, 1), padding="same"),
                layer.Flatten(),
                # Detect patterns and perform non-linear transformations
                layer.Dense(units=sequence_length*8, activation='relu'),
                layer.Dense(units=128, activation='relu'),
                layer.Dense(units=sequence_length*8, activation='relu'),
                layer.Reshape(target_shape=(sequence_length, 8)),
                layer.Conv1D(kernel_size = 4, strides=1, filters = 1, activation="linear", padding="same"),
            ]
        ) 

        denoising_autoencoder.compile(loss='mean_squared_error', optimizer='adam')

        return denoising_autoencoder
    '''
    get visual summary of the denoising autoencoder model
    '''
    def get_denoising_autoencoder_model_summary(self):
        return print(self.denoising_autoencoder_model.summary())

    '''
    train a model to be able to disaggregate the power consumption of a specific appliance using only the power consumption of the building that device is on.
    train_mains_list: contain the consumption of the entire building.
    train_meter_list: contain the consumption of a specific device we want to train our model on.
    epochs : Number of complete passes through the entire training dataset during the training process.
    batch_size: number of training samples that the model processes before updating its internal parameters.
    load_kwargs : is used to pass the arguments sample_period, resample that change the sampling period and can resample using ffil

    note: It is important for train_mains_list and train_meter_list to contain data from the same time periods
    '''
    def train(self, train_mains_list, train_meter_list, batch_size=64, epochs=16,  **load_kwargs):

        '''
        mains_list: contains the lists of mains power consumption data 
        mains_data_max_value: contains the max value from train_mains_list data, and we use it to normalize the data
        meters_list: contains the lists of meter power consumption data
        total_data_values: contains the total number of data values that are going to be trained, its used to calculate the amount of data padding that needs to be done before 
        '''
        mains_list = []
        meters_list = []
        mains_data_max_value = 0
        total_data_values = 0
        '''
        save the first meter metadata to use its metadata in the disaggregated results metadata
        '''
        self.train_meter_metadata = train_meter_list[0]

        '''
        for every element in the mains list we load the data, remove nan values and get the its max value
        '''
        for main in train_mains_list:
            main_chunk = main.power_series(**load_kwargs)

            for m_chunk in main_chunk:
                temp_mains = m_chunk.dropna()
                if temp_mains.max()>mains_data_max_value:
                    mains_data_max_value = temp_mains.max()
                mains_list.append(temp_mains) 
          
        
        '''
        get the max value off the entire list and 
        '''
        self.max_dataset_value = mains_data_max_value

        '''
        normalize mains data by dividing each data point with the largest value of the input data 
        '''
        for i in range(len(mains_list)):
            mains_list[i] = mains_list[i].div(float(self.max_dataset_value))

        '''
        for every element in the train_meter_list list we load the data, remove nan values and normalize the data
        '''
        for meter in train_meter_list:
            meter_chunk = meter.power_series(**load_kwargs)
            for m_chunk in meter_chunk:
                
                temp_meters = m_chunk.dropna()
                '''
                normalize meters data by dividing each data point with the largest value of the input data
                '''
                temp_meters = temp_meters.div(float(self.max_dataset_value))
                meters_list.append(temp_meters) 

        '''
        keep the common indices of meters and mains and remove Nan values
        '''
        for i in range(len(mains_list)):
            '''
            between mains, meter keep the values that have common indices and train data
            '''
            mains_list_index = mains_list[i].index
            meters_list_index = meters_list[i].index

            common_indicies = mains_list_index.intersection(meters_list_index)
           
            mains_list[i] = mains_list[i][common_indicies].dropna()
            meters_list[i] = meters_list[i][common_indicies].dropna()
            
            '''
            Keep track of the number of data values
            '''
            total_data_values = total_data_values + len(common_indicies)

        additional = self.sequence_length - (total_data_values % self.sequence_length)
        

        '''
        concatenate list elements into single array and add zeros at the end to make the size of the array integer multiple of sequence_length
        '''
        if len(mains_list)>1 :
            mains_chunk_x = np.concatenate(mains_list)
            meter_chunk_y = np.concatenate(meters_list)

            mains_chunk_x = np.pad(mains_chunk_x, (0, additional), mode='constant', constant_values=0)
            meter_chunk_y = np.pad(meter_chunk_y, (0, additional), mode='constant', constant_values=0)

        else:
            mains_chunk_x = np.pad(mains_list[0], (0, additional), mode='constant', constant_values=0)
            meter_chunk_y = np.pad(meters_list[0], (0, additional), mode='constant', constant_values=0)


        '''
        reshape data to make them compatible with the model. array dimensions [(X_batch/sequence_length), sequence_length, 1]
        '''
        mains_chunk_x = np.reshape(mains_chunk_x, (int(mains_chunk_x.size / self.sequence_length), self.sequence_length, 1))
        meter_chunk_y = np.reshape(meter_chunk_y, (int(meter_chunk_y.size / self.sequence_length), self.sequence_length, 1))
        
        self.denoising_autoencoder_model.fit(mains_chunk_x, meter_chunk_y, epochs=epochs, batch_size=batch_size, shuffle=True)


    '''
    find the consumption of a specific appliance using only the building consumption by disaggregating the mains consumption using the model created in the train function.
    mains: contain the consumption of the entire building.
    output_datastore: filename of disaggregation results
    load_kwargs : is used to pass the arguments sample_period, resample that change the sampling period and can resample using ffil
    '''
    def disaggregate(self, mains, output_datastore, **load_kwargs):
        
        load_kwargs.setdefault('sample_period', 60)
        load_kwargs.setdefault('sections', mains.good_sections())

        '''
        create disaggregated meter path to be saved on output_datastore
        '''
        timeframes = []
        building_path = '/building{}'.format(mains.building())
        mains_data_location = building_path + '/elec/meter1'
        data_is_available = False

        '''
        clean mains data from Nan values, normalize data, disaggrega, denormalized data and then save it in a format compatible with nilmtk and .h5 file
        '''
        for mains_chunk in mains.power_series(**load_kwargs):    
            '''
            drop Nan values
            '''
            mains_chunk.dropna(inplace=True)
            
            '''
            save mains timeframe to use on the dissagragated data and normalize data
            '''
            timeframes.append(mains_chunk.timeframe)
            measurement = mains_chunk.name
            '''
            normalize mains_chunk data by dividing each data point with the largest value of the input data
            '''
            mains_chunk = mains_chunk.div(float(self.max_dataset_value))
                    
            additional = self.sequence_length - (len(mains_chunk) % self.sequence_length)
            '''
            add zeros at the end to make the size of the array integer multiple of sequence_length
            '''
            mains_chunk_x = np.pad(mains_chunk, (0, additional), mode='constant', constant_values=0)
                    
            '''
            reshape data to make them compatible with the model. array dimensions [(X_batch/sequence_length), sequence_length, 1]
            '''
            mains_chunk_x = np.reshape(mains_chunk_x, (int(mains_chunk_x.size / self.sequence_length), self.sequence_length ,1))
            '''
            dissagragate and make the data timeseries using original mains index
            '''
            disaggregated_meter = self.denoising_autoencoder_model.predict(mains_chunk_x)
            disaggregated_meter = np.reshape(disaggregated_meter, disaggregated_meter.size)[:len(mains_chunk)]
            disaggregated_meter = pd.Series(disaggregated_meter, index=mains_chunk.index, name=0)
            disaggregated_meter = pd.DataFrame(disaggregated_meter.clip(lower=0))

            '''
            denormalize data by multiplying each data point with the largest value of the input data
            self.max_dataset_value: largest value of input data
            '''          
            disaggregated_meter = disaggregated_meter.mul(self.max_dataset_value)

            '''
            save data in a format compatible with nilmtk and .h5 file
            '''
            data_is_available = True
            cols = pd.MultiIndex.from_tuples([mains_chunk.name])
            meter_instance = self.train_meter_metadata.instance()
            df = pd.DataFrame(
                disaggregated_meter.values, index=disaggregated_meter.index,
                columns=cols, dtype="float32")
            key = '{}/elec/meter{}'.format(building_path, meter_instance)
            output_datastore.append(key, df)

            mains_df = pd.DataFrame(mains_chunk, columns=cols, dtype="float32")
            output_datastore.append(key=mains_data_location, value=mains_df)

        '''
        combine the metadata collected from appliance meter in training and the mains metadata to create the disaggregated meter metadata.
        self.MODEL_NAME needs to be set in order for the _save_metadata_for_disaggregation function to work
        '''
        self.MODEL_NAME = 'Denoising autoencoder neural network'
        if data_is_available:
            self._save_metadata_for_disaggregation(
                output_datastore=output_datastore,
                sample_period=load_kwargs['sample_period'],
                measurement=measurement,
                timeframes=timeframes,
                building=mains.building(),
                meters=[self.train_meter_metadata]
            )

    '''
    Save and export trained model so you can use it later without having to train it again.
    Along with the model we also save self.max_dataset_value and self.sequence_length which are needed in order for the model to perform disaggregation successfully .
    filename: the name of the file that the model and the required variables are going to be saved
    '''
    def export_model(self, filename):
  
        self.denoising_autoencoder_model.save(filename+'.h5')

        data = {'max': self.max_dataset_value, 'sequence_length': self.sequence_length}

        with open(filename+'.pkl', 'wb') as file:
            pickle.dump(data, file)

    # def export_model(self, filename):
    #     self.denoising_autoencoder_model.save(filename + '.h5')
    #     data = {
    #         'max': self.max_dataset_value,
    #         'sequence_length': self.sequence_length,
    #         'train_meter_metadata': self.train_meter_metadata
    #     }
    #     with open(filename + '.pkl', 'wb') as file:
    #         pickle.dump(data, file)


    '''
    Import existing model in order to skip training
    Along with the model we also import self.max_dataset_value and self.sequence_length which are needed in order for the model to perform disaggregation successfully 
    filename: the name of the file from which the model and the required variables are going to be imported
    '''
    def import_model(self, filename):

        self.denoising_autoencoder_model = load_model(filename+'.h5')
        with open(filename+'.pkl', 'rb') as file:
            loaded_data = pickle.load(file)
        self.max_dataset_value = loaded_data['max']
        self.sequence_length = loaded_data['sequence_length']

    # def import_model(self, filename):
    #     self.denoising_autoencoder_model = load_model(filename + '.h5')
    #     with open(filename + '.pkl', 'rb') as file:
    #         loaded_data = pickle.load(file)
    #     self.max_dataset_value = loaded_data['max']
    #     self.sequence_length = loaded_data['sequence_length']
    #     # Assuming metadata is also saved in the same pickle file
    #     self.train_meter_metadata = loaded_data.get('train_meter_metadata', None)
    