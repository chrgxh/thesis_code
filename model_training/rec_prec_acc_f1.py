from nilmtk.electric import align_two_meters
import numpy as np

"""
based on the power threshold of the appliances we say that every data point that is above that threshold is considered an activation of the appliance and for
every data point below that threshold we consider the device as deactivated (deactivations)
Then we compare the activations/deactivations between real and disaggregated data and based on those results we create the metrics recall,precision,accuracy,f1    
"""
def results(disaggregation_data, real_data):

    true_appliance_activations = 0      #tp
    true_appliance_deactivations = 0    #tn
    false_appliance_activations = 0     #fp
    false_appliance_deactivations = 0   #fn
 
    # appliance_power_threshold = real_data.on_power_threshold()
    appliance_power_threshold = 10
   
    aligned_meters_chunk_total_length = 0

    for aligned_meters_chunk in align_two_meters(disaggregation_data, real_data):

        aligned_meters_chunk_total_length += len(aligned_meters_chunk)
               
        predicted_activations_deactivations = np.array(aligned_meters_chunk['master'].apply(lambda x: False if x < appliance_power_threshold else True))
        actual_activations_deactivations = np.array(aligned_meters_chunk['slave'].apply(lambda x: False if x < appliance_power_threshold else True))

        true_appliance_activations = int(np.sum(np.logical_and(predicted_activations_deactivations == True, actual_activations_deactivations == True)))+true_appliance_activations
        true_appliance_deactivations = int(np.sum(np.logical_and(predicted_activations_deactivations == False, actual_activations_deactivations == False)))+true_appliance_deactivations
        false_appliance_activations = int(np.sum(np.logical_and(predicted_activations_deactivations == True, actual_activations_deactivations == False)))+false_appliance_activations
        false_appliance_deactivations = int(np.sum(np.logical_and(predicted_activations_deactivations == False, actual_activations_deactivations == True)))+false_appliance_deactivations
     
    if aligned_meters_chunk_total_length == 0:
        raise TypeError("disaggregation data are incompatible with real data")
    else:

        recall = (true_appliance_activations)/(true_appliance_activations+false_appliance_deactivations)
        precision = (true_appliance_activations)/(true_appliance_activations+false_appliance_activations)
        accuracy = (true_appliance_activations+true_appliance_deactivations)/(true_appliance_activations+true_appliance_deactivations+false_appliance_activations+false_appliance_deactivations)
        f1 = (2*recall*precision)/(recall+precision)

        return ({"recall" : recall, "precision" : precision, "accuracy" : accuracy, "f1" : f1})