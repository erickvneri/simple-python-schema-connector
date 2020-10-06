import jwt
from stschema import SchemaConnector, SchemaDevice
from lib.webhook.webhook_config import ALGORITHM, SECRET
from lib.webhook.data import DeviceInformation

class MyConnector(SchemaConnector, DeviceInformation):
    def __init__(self, *opts):
        SchemaConnector.__init__(self, enable_logger=True) # Logger enabled by default

    def discovery_handler(self, request_id, access_token):
        # The discovery_handler built-in method
        # gives access to discoveryRequest data.
        #
        # SchemaDevice instances must be passed
        # as a list argument to discovery_response
        # built-in method.

        # Decode access token and collect raw device info
        token_info = jwt.decode(access_token, SECRET, ALGORITHM)
        # Collect raw device info
        device_info = super().get_device_info(token_info['devices'])

        # Create SchemaDevice instances
        declared_devices = list(map(self._discovery_information, device_info))

        # Return Discovery Response
        return super().discovery_response(declared_devices, request_id)

    def state_refresh_handler(self, devices, request_id, access_token):
        # The state_refresh_handler gives access to
        # stateRefreshRequest data.
        # A filtered list of SchemaDevice instances
        # must be passed as response to the
        # state_refresh_response built-in method.

        device_ids = list(map(lambda device: device['externalDeviceId'], devices))
        # Collect raw device state info
        device_info = super().get_states(device_ids)

        # Create SchemaDevice instances
        filtered_devices = list(map(self._state_information, device_info))

        # Return State Refresh Response
        return self.state_refresh_response(filtered_devices, request_id)

    def command_handler(self, devices, request_id, access_token):
        # The command_handler gives access to the
        # commandRequest data.
        # A list of an updated SchemaDevice instance
        # must be passed as response to the
        # command_response built-in method.
        #
        # For the purpose of this ST Schema
        # example, this Schema Connector instance
        # will respond to individual commands.
        device_id = devices[0]['externalDeviceId']
        updated_device = [self.handle_command(device_id, devices[0]['commands'][0])]
        return  self.command_response(updated_device, request_id)

    def grant_callback_access(self, callback_authentication, callback_urls):
        # Built-in method triggered with the
        # grantCallbackAccess interaction type.
        pass

    def integration_deleted(self, callback_authentication):
        # Built-in method triggered with the
        # integrationDeleted interactionType.
        pass

    def interaction_result_handler(self, interaction_result, origin):
        # The interaction_result_handler provides
        # a description of the error triggered
        # between interaction type responses.
        pass

    """
    SchemaConnector instance custom utils
    to map raw device info and device commands.
    """
    @staticmethod
    def _discovery_information(device):
        # Create SchemaDevice instances
        # for Discovery Response.
        # for device in device_info:
        # Discovery information
        instance = SchemaDevice(device['unique_id'],        # externalDeviceId
                                device['label'],            # friendlyName
                                device['device_handler'],   # deviceHandlerType
                                device['unique_id'])        # deviceUniqueId
        # Manufacturer Information
        instance.set_mn(device['mn']['mn'],
                        device['mn']['model'],
                        device['mn']['hw_version'],
                        device['mn']['sw_version'])
        # Device Context Information
        instance.set_context(device['context']['room_name'],
                                device['context']['groups'],
                                device['context']['categories'])
        return instance

    @staticmethod
    def _state_information(device):
         # Create SchemaDevice instances
         # for State Refresh Response.
        instance = SchemaDevice(device['unique_id'])
        for state in device['states']:
            instance.set_state(state.get('capability'),
                               state.get('attribute'),
                               state.get('value'),
                               state.get('unit'),
                               state.get('component'))
        return instance

    @staticmethod
    def handle_command(device_id, command):
        device = SchemaDevice(device_id)
        capability = command['capability']
        unit = None
        value = None
        # Flow Control depending on capability
        if not command['arguments']:
            command = command['command']
            if 'door' in capability:
                state_attr = 'door'
                value = 'closed' if command == 'close' else 'open'
            elif 'switch' in capability:
                state_attr = 'switch'
                value = command
            elif 'valve' in capability:
                state_attr = 'valve'
                value = 'closed' if command == 'close' else 'open'
            elif 'window' in capability:
                state_attr = 'windowShade'
                value = 'closed' if command == 'close' else 'open'
        else:
            value = command['arguments'][0]
            if 'thermostatMode' in capability:
                state_attr = 'thermostatMode'
            elif 'Level' in capability:
                state_attr = 'level'
            elif 'Heating' in capability:
                state_attr = 'heatingSetpoint'
                unit = 'C'
            elif 'Cooling' in capability:
                state_attr = 'coolingSetpoint'
                unit = 'C'
        # Control if unit in state
        if unit:
            device.set_state(capability,
                             state_attr,
                             value,
                             unit)
        else:
            device.set_state(capability,
                             state_attr,
                             value)
        return device
