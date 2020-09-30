import jwt
from stschema import SchemaConnector, SchemaDevice
from lib.webhook.webhook_config import ALGORITHM, SECRET
from lib.webhook.data import DeviceInformation

class MyConnector(SchemaConnector, DeviceInformation):
    def __init__(self, *opts):
        SchemaConnector.__init__(self, enable_logger=True)

    def discovery_handler(self, request_id, access_token):
        # The discovery_handler built-in method
        # gives access to discoveryRequest data.
        #
        # SchemaDevice instances must be passed
        # as a list argument to discovery_response
        # built-in method.
        declared_devices = []

        # Decode access token and collect raw device info
        token_info = jwt.decode(access_token, SECRET, ALGORITHM)
        device_info = super().get_device_info(token_info['devices'])

        # Create SchemaDevice instances
        for device in device_info:
            # Discovery information
            instance = SchemaDevice(device['unique_id'],        # externalDeviceId
                                    device['label'],            # friendlyName
                                    device['device_handler'],   # deviceHandlerType
                                    device['unique_id'])        # deviceUniqueId
            # Manufacturer Information
            instance.set_mn(device['mn']['mn'],
                            device['mn']['model'])

            # Collect instance into predefined list
            declared_devices.append(instance)

        # Return Discovery Response
        return super().discovery_response(declared_devices, request_id)

    def state_refresh_handler(self, devices, request_id, access_token):
        # The state_refresh_handler gives access to
        # stateRefreshRequest data.
        # A filtered list of SchemaDevice instances
        # must be passed as response to the
        # state_refresh_response built-in method.
        filtered_devices = []
        device_ids = list(map(lambda device: device['externalDeviceId'], devices))

        # Collect raw device state info
        device_info = super().get_states(device_ids)

        # Create SchemaDevice instances
        for device in device_info:
            instance = SchemaDevice(device['unique_id'])
            for state in device['states']:
                instance.set_state(state.get('capability'),
                                   state.get('attribute'),
                                   state.get('value'),
                                   state.get('unit'),
                                   state.get('component'))

            filtered_devices.append(instance)

        # Return State Refresh Response
        return self.state_refresh_response(filtered_devices, request_id)

    def command_handler(self, devices, request_id, access_token):
        # The command_handler gives access to the
        # commandRequest data.
        # A list of an updated SchemaDevice instance
        # must be passed as response to the
        # command_response built-in method.
        updated_device = []
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
