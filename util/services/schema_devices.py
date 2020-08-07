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
