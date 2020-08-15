from dataclasses import dataclass
from util.db.main_db import MainDB
from datetime import datetime


@dataclass
class DevicesDB(MainDB):
    """
    This class offers interfaces to
    execute device-related db transaction.
    It inherits from the main DB class.
    """
    def prov_user_devices(self, user_token):
        # From auth_token received, get
        # user id and return respective
        # devices.
        user_id_query = \
            'SELECT user_id FROM TOKEN_INFO ' + \
            'WHERE access_token=?'
        devices_query = \
            'SELECT * FROM DEVICE_INFO ' + \
            'WHERE user_id=(%s)' % user_id_query
        return self.init_session(devices_query, user_token)

    def get_device_state(self, id_list):
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
        return self.init_session(poll_query)

    def put_device_state(self, id_list, *state_data):
        capability, value, unit = state_data
        # Update POLL_INFO table based
        # on the device_id passed.
        poll_query = \
            'UPDATE POLL_INFO ' + \
            'SET ' + \
            'value=?,' + \
            'poll_date=?,' + \
            'unit=? ' + \
            'WHERE ' + \
            'device_id=? ' + \
            'AND ' + \
            'capability=?'
        return self.init_session(
            poll_query,
            value,
            str(datetime.now()),
            unit,
            id_list[0],
            capability
        )
