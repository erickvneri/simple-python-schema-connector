from dataclasses import dataclass
from stschema import SchemaConnector
from lib.services import DeviceProvider


@dataclass
class Connector(SchemaConnector):
    def __init__(self):
        SchemaConnector.__init__(self, enable_logger=True)
        self.service = DeviceProvider()


    def discovery_handler(self, request_id: str, access_token: str):
        # Fetch devices by access
        # token received
        devices = self.service.fetch_device_by_token(access_token)
        return super().discovery_response(devices, request_id)

    def state_refresh_handler(self, devices: list, request_id: str, access_token: str):
        # Fetch and filter devices
        # to retreive current status
        id_list = list(map(lambda device: device['externalDeviceId']), devices)
        devices = self.service.fetch_device_state(id_list)

        return super().state_refresh_response(devices, request_id)

    def command_handler(self, devices: str, request_id: str, access_token: str):
        # Map device Id
        id_list = list(map(lambda device: device['externalDeviceId'], devices))
        command = devices[0]['commands']
        # Prepare command dictionary
        # to put new state.
        poll_data = dict(
            capability=command['capability'],
            value=command['arguments'][0]
        )
        self.service.put_device_state(id_list, poll_data)
        # Retrieve status
        updated_device = self.service.fetch_device_state(id_list)
        return super().command_response(updated_device, request_id)
