from dataclasses import dataclass
from stschema import SchemaConnector, SchemaDevice
from lib.services import DeviceService, CommandService


@dataclass
class Connector(SchemaConnector):
    def __init__(self):
        SchemaConnector.__init__(self, enable_logger=True)
        self.device_service = DeviceService()
        self.command_service = CommandService()

    def discovery_handler(self, request_id: str, access_token: str):
        # Fetch devices by access
        # token received
        devices = self.device_service.fetch_device_by_token(access_token)
        return super().discovery_response(devices, request_id)

    def state_refresh_handler(self, devices: list, request_id: str, access_token: str):
        # Fetch and filter devices
        # to retreive current status
        id_list = list(map(lambda device: device['externalDeviceId']), devices)
        devices = self.device_service.fetch_device_state(id_list)

        return super().state_refresh_response(devices, request_id)

    def command_handler(self, devices: str, request_id: str, access_token: str):
        # Map device Id
        id_list = list(map(lambda device: device['externalDeviceId'], devices))
        command = devices[0]['commands'][0]
        # Prepare command dictionary
        # to put new state.
        poll_data = self.command_service.handle_command(command)

        # Update database with command data
        self.device_service.put_device_state(id_list, poll_data)
        # Consult database for the
        # updated value and filter
        # response to return required
        # capability state.
        updated_device = self.device_service.fetch_device_state(id_list)
        updated_device[0].states = \
            list(filter(lambda state: state.capability == command['capability'], updated_device[0].states))

        return super().command_response(updated_device, request_id)
