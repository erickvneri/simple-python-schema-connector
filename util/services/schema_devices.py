from stschema import SchemaDevice
from dataclasses import dataclass
from app import db


class DeviceProv:
    """
    Device Provider interface. Service
    instance that takes query results
    and parse them into SchemaDevice
    instances.
    """
    def fetch_by_user_tkn(self, token: str) -> list:
        # DB List of Results
        fetch_result = db.prov_user_devices(user_tkn=token)
        # Elaborate SchemaDevice instances
        devices = []
        for i in fetch_result:
            d = SchemaDevice(i[0], i[2], i[3])
            d.set_mn(i[4], i[5])
            devices.append(d)
        return devices

    def poll_by_device_id(self, id_list: list) -> list:
        # DB List of Results
        fetch_result = db.prov_device_poll(id_list)
        # Elaborate SchemaDevice instances
        devices = [SchemaDevice(_id) for _id in id_list]
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

