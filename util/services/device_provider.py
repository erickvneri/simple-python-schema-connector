from stschema import SchemaDevice
from dataclasses import dataclass
from app import db


class DeviceProvider:
    """
    Device Provider interface. Service
    instance that takes query results
    and parse them into SchemaDevice
    instances.
    """

    @staticmethod
    def fetch_device_by_token(token: str) -> list:
        # DB List of Results
        fetch_result = db.prov_user_devices(user_tkn=token)
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
        fetch_result = db.polling_device(id_list)
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

    def put_device_state(self, id_list: list, *poll_data) -> list:
        capability, value = poll_data
        if len(poll_data) > 2:
            unit = poll_data[2]
        else:
            unit = None

        return db.polling_device(
            id_list,
            dict(
                capability=capability,
                value=value,
                unit=unit
            )
        )

