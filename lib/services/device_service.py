from stschema import SchemaDevice
from datetime import datetime
from lib.db import MainDB
from dataclasses import dataclass


@dataclass
class DeviceService(MainDB):
    """
    Device Provider interface. Service
    instance that takes query results
    and parse them into SchemaDevice
    instances.
    """

    def fetch_device_by_token(self, token: str) -> list:
        # DB List of Results
        fetch_result = self._get_devices(user_token=token)
        # Elaborate SchemaDevice instances
        devices = []
        for i in fetch_result:
            device = SchemaDevice(i[0], i[1], i[2],i[0])
            device.set_mn(i[3], i[4], i[6], i[5])
            device.set_context(
                i[8],
                i[7].split(','),
                i[9].split(',')
            )
            devices.append(device)
        return devices

    def fetch_device_state(self, id_list: list):
        # Elaborate SchemaDevice instances
        devices = [SchemaDevice(_id) for _id in id_list]
        # DB List of Results
        fetch_result = self._get_device_state(id_list)
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
        return self._put_device_state(
            id_list,
            poll_data.get('component'),
            poll_data.get('capability'),
            poll_data.get('attribute'),
            poll_data.get('value'))

    # def put_callback_data(self, callback_authentication: dict, callback_urls: dict, client_secret: str):
        # data = dict(
        #     callback_url=callback_urls['stateCallback'],
        #     oauth_url=callback_urls['oauthToken'],
        #     client_id=callback_authentication['clientId'],
        #     code=callback_authentication['code'],
        #     client_secret=client_secret
        # )
        # return super().put_callback_info(data)

    # def get_token_request_data(self):
        # return super().get_callback_info()

    # def get_access_token(self):
        # return super().get_access_token()

    # def put_access_token(self, access_token: str, refresh_token: str=None):
        # return super().put_access_token(access_token, refresh_token)

    def _get_device_state(self, id_list):
        # From list of ids, return
        # filtered results.
        if len(id_list) > 1:
            condition = 'IN {}'.format(tuple(id_list))
        else:
            condition = '="%s"' % id_list[0]
        # Elaborate Base query
        poll_query = \
            'SELECT * FROM POLL_INFO ' + \
            'WHERE device_id ' + \
            condition #filtered condition
        return super().init_session(poll_query)

    def _get_devices(self, user_token):
        # From auth_token received, get
        # user id and return respective
        # devices.
        fields = [
            'DEVICE_INFO.id','label','device_handler',
            'manufacturer_name','model_name',
            'sw_version','hw_version','categories',
            'room_name','groups'
        ]
        user_id_query = \
            '(SELECT user_id FROM TOKEN_INFO ' + \
            'WHERE access_token=?)'
        devices_query = \
            'SELECT %s ' % ','.join(fields) + \
            'FROM DEVICE_INFO ' + \
            'INNER JOIN MN_INFO ON ' + \
            'DEVICE_INFO.id=MN_INFO.device_id ' + \
            'INNER JOIN DEVICE_CONTEXT ON ' + \
            'MN_INFO.device_id=DEVICE_CONTEXT.device_id ' + \
            'WHERE DEVICE_INFO.user_id IN %s' % user_id_query
        return super().init_session(devices_query, user_token)

    def _put_device_state(self, id_list, *state_data):
        component, capability, attribute, value = state_data
        # Update POLL_INFO table based
        # on the device_id passed.
        poll_query = \
            'UPDATE POLL_INFO ' + \
            'SET ' + \
            'value=?,' + \
            'poll_date=? ' + \
            'WHERE device_id=? ' + \
            'AND capability=? ' + \
            'AND attribute=? ' + \
            'AND component=?'
        return super().init_session(
            poll_query,
            value,
            str(datetime.now()),
            id_list[0],
            capability,
            attribute,
            component
        )
