import pandas as pd
import pickle as pkl
from os.path import exists


def clean_demand_data(csv_file_path, pkl_file_path):
    demand_data = pd.read_csv(csv_file_path)
    demand_data = demand_data[['time_stamp', 'starts', 'ends']]
    demand_data['time_stamp'] = pd.to_datetime(demand_data.time_stamp, errors='coerce',
                                               infer_datetime_format=True).dt.tz_localize(None)
    demand_data['starts'] = pd.to_datetime(demand_data.starts, errors='coerce', infer_datetime_format=True)
    demand_data['ends'] = pd.to_datetime(demand_data.ends, errors='coerce', infer_datetime_format=True)
    demand_data['booking_length'] = (demand_data.ends - demand_data.starts).dt.total_seconds() / 3600
    demand_data['lead_time'] = (demand_data.starts - demand_data.time_stamp).dt.total_seconds()/3600
    pkl.dump(demand_data, open(pkl_file_path, 'wb'))
    return demand_data


def get_demand_data(csv_file_path, pkl_file_path):
    if exists(pkl_file_path):
        demand_data = pd.read_pickle(pkl_file_path)
    else:
        demand_data = clean_demand_data(csv_file_path, pkl_file_path)
    return demand_data






