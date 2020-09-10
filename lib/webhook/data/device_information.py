# To simplify the implementation of device
# related data manipulation, device information
# will be tracked at binary files using
# Pickle, Python's built-in module.
import pickle
import os


class DeviceInformation():
    """
    This module will handle device related
    transactions:
        - Get all devices.
        - Get many devices.
        - Get state of many devices.
        - Update device state.
    """
    def __init__(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.device_info_path = '/device_info.p'
        self.device_state_path = '/device_state_info.p'

    def get_all(self):
        # Read data step
        with open(self.basedir + self.device_info_path, 'rb') as info:
            info = pickle.load(info)
        return info

    def get_many(self, unique_ids: list) -> list:
        # Read data step
        with open(self.basedir + self.device_info_path, 'rb') as info:
            info = pickle.load(info)

        # Filter step
        filter_many = list(filter(lambda n: n['unique_id'] in unique_ids, info))
        return filter_many

    def get_states(self, unique_ids: list) -> list:
        # Read state data step
        with open(self.basedir + self.device_state_path, 'rb') as info:
            info = pickle.load(info)

        # Filter step
        filter_many = list(filter(lambda n: n['unique_id'] in unique_ids, info))
        return filter_many

    def update_state(self, unique_id: str, state: dict) -> list:
        # Read state data step
        with open(self.basedir + self.device_state_path, 'rb') as info:
            info = pickle.load(info)
        # Filter step
        filter_one = list(filter(lambda n: n['unique_id'] == unique_id, info))
        filter_state = list(filter(lambda s: s['capability'] == state['capability'], filter_one[0]['states']))

        # Update step
        filter_state[0]['value'] = state['value']

        # Update data step
        with open(self.basedir + self.device_state_path, 'wb') as cur_info:
            pickle.dump(info, cur_info)

        # Return updated state
        return filter_state
