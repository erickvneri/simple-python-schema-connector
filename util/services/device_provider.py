from stschema import SchemaDevice
from datetime import datetime
from util.db import DevicesDB
from dataclasses import dataclass


@dataclass
class DeviceProvider(DevicesDB):
    """
    Device Provider interface. Service
    instance that takes query results
    and parse them into SchemaDevice
    instances.
    """

    def fetch_device_by_token(self, token: str) -> list:
        # DB List of Results
        fetch_result = super().prov_user_devices(user_token=token)
        # Elaborate SchemaDevice instances
        devices = []
        for i in fetch_result:
            d = SchemaDevice(i[0], i[2], i[3])
            d.set_mn(i[4], i[5])
            devices.append(d)
        return devices

    def fetch_device_state(self, id_list: list):
        # Elaborate SchemaDevice instances
        devices = [SchemaDevice(_id) for _id in id_list]
        # DB List of Results
        fetch_result = super().get_device_state(id_list)
        # Iteration to filter
        # states results
        d_id, s_index = 0, 0
        while d_id < len(devices):
            if not devices[d_id].external_device_id == fetch_result[s_index][1]:
                s_index += 1
            else:
                devices[d_id].set_state(
                    fetch_result[s_index][3],  # capability
                    fetch_result[s_index][4],  # attribute
                    fetch_result[s_index][5],  # value
                    fetch_result[s_index][6],  # unit
                    fetch_result[s_index][7]   # component
                )
                s_index += 1
            if s_index == len(fetch_result):
                s_index = 0
                d_id += 1
        return devices

    def put_device_state(self, id_list: list, poll_data: dict) -> list:
        return super().put_device_state(
            id_list,
            poll_data.get('capability'),
            poll_data.get('value'),
            poll_data.get('unit', None))

    def put_callback_data(self, callback_authentication: dict, callback_urls: dict, client_secret: str):
        data = dict(
            callback_url=callback_urls['stateCallback'],
            oauth_url=callback_urls['oauthToken'],
            client_id=callback_authentication['clientId'],
            code=callback_authentication['code'],
            client_secret=client_secret
        )
        return super().put_callback_info(data)

    def get_token_request_data(self):
        return super().get_callback_info()

    def get_access_token(self):
        return super().get_access_token()

    def put_access_token(self, access_token: str, refresh_token: str=None):
        return super().put_access_token(access_token, refresh_token)
