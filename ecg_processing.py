# ecg_processing.py
import h5py
import numpy as np
from tensorflow.keras.models import load_model as keras_load_model
from ml4h.models.model_factory import get_custom_objects
from ml4h.tensormap.ukb.survival import mgb_afib_wrt_instance2
from ml4h.tensormap.ukb.demographics import age_2_wide, af_dummy, sex_dummy3

ECG_REST_LEADS = {
    'strip_I': 0, 'strip_II': 1, 'strip_III': 2, 'strip_V1': 3, 'strip_V2': 4,
    'strip_V3': 5, 'strip_V4': 6, 'strip_V5': 7, 'strip_V6': 8, 'strip_aVF': 9,
    'strip_aVL': 10, 'strip_aVR': 11
}
ECG_SHAPE = (5000, 12)
ECG_HD5_PATH = 'ukb_ecg_rest'

def ecg_as_tensor(ecg_file):
    with h5py.File(ecg_file, 'r') as hd5:
        tensor = np.zeros(ECG_SHAPE, dtype=np.float32)
        for lead in ECG_REST_LEADS:
            data = np.array(hd5[f'{ECG_HD5_PATH}/{lead}/instance_0'])
            tensor[:, ECG_REST_LEADS[lead]] = data
        tensor -= np.mean(tensor)
        tensor /= np.std(tensor) + 1e-6
        if tensor.shape == ECG_SHAPE:
            tensor = np.expand_dims(tensor, axis=0)

    return tensor

def load_model():
    output_tensormaps = {tm.output_name(): tm for tm in [mgb_afib_wrt_instance2, age_2_wide, af_dummy, sex_dummy3]}
    custom_dict = get_custom_objects(list(output_tensormaps.values()))
    model = keras_load_model('./model_zoo/ECG2AF/ecg_5000_survival_curve_af_quadruple_task_mgh_v2021_05_21.h5', custom_objects=custom_dict)
    return model

def predict_risk(ecg, model):
    predictions = model(ecg)
    return {
        # Survival curve probabilities
        "afib_risk": predictions[0].numpy().tolist(),
        # Age prediction probabilities     
        "age_estimate": predictions[1].numpy().tolist(),
        # AFib dummy score  
        "afib_dummy": predictions[2].numpy().tolist(),
        # Sex prediction probabilities    
        "sex_dummy": predictions[3].numpy().tolist()      
    }

def validate_ecg_file(ecg_file_path):
    """Validates the structure and content of the ECG .h5 file."""
    required_leads = [
        'strip_I', 'strip_II', 'strip_III', 'strip_V1', 'strip_V2',
        'strip_V3', 'strip_V4', 'strip_V5', 'strip_V6', 'strip_aVF',
        'strip_aVL', 'strip_aVR'
    ]
    try:
        with h5py.File(ecg_file_path, 'r') as hd5:
            if 'ukb_ecg_rest' not in hd5:
                return False
            for lead in required_leads:
                path = f'ukb_ecg_rest/{lead}/instance_0'
                if path not in hd5 or hd5[path].shape != (5000,):
                    return False
    except Exception:
        return False
    return True
