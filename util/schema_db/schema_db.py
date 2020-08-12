# The SchemaDB module handles the storage
# of users, devices, tokens and callback
# arguments received at the Grant Callback
# Access interaction type
from stschema import SchemaDevice
from dataclasses import dataclass
from datetime import datetime
from sqlite3 import OperationalError, IntegrityError
import sqlite3
import logging
import os
# Logger config.
logging.basicConfig(format='%(asctime)s - %(message)s')


@dataclass
class SchemaDB:
    """
    The SchemaDB stores the necessary
    information to handle users, devices,
    polling data and auth token related
    info.
    """
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DB_URL = f'{BASE_DIR}/schema_connector_db.sqlite'

    def init_db(self) -> None:
        try:
            db = sqlite3.connect(self.DB_URL)
            self._create_all(db)
        except (OperationalError, IntegrityError) as e:
            logging.warning('DATABASE ERROR - %s' % e)
        else:
            db.commit()
        finally:
            db.close()

    def _create_all(self, database):
        self._create_callback_table(database)
        self._create_tokens_table(database)
        self._create_devices_table(database)
        self._create_poll_table(database)
        self._create_user_table(database)
        # Run mock inserts
        self._user_mock_inserts(database)
        self._token_mock_inserts(database)
        self._devices_mock_inserts(database)

    @staticmethod
    def _create_callback_table(database: object) -> None:
        callback_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'CALLBACK_INFO(' + \
            'id INTEGER PRIMARY KEY,' + \
            'callback_url VARCHAR,' + \
            'oauth_url VARCHAR,' + \
            'code VARCHAR,' + \
            'client_id VARCHAR,' + \
            'client_secret VARCHAR,' + \
            'cb_access_token VARCHAR,'+ \
            'cb_refresh_token VARCHAR)'

        cursor = database.cursor()
        cursor.execute(callback_table_query)

    @staticmethod
    def _create_tokens_table(database: object) -> None:
        token_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'TOKEN_INFO(' + \
            'id INTEGER PRIMARY KEY,' + \
            'user_id INT,' + \
            'access_token VARCHAR,' + \
            'refresh_token VARCHAR,' + \
            'last_update TIMESTAMP,' + \
            'FOREIGN KEY (user_id) REFERENCES USER_INFO(id))'
        cursor = database.cursor()
        cursor.execute(token_table_query)

    @staticmethod
    def _create_user_table(database: object) -> None:
        users_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'USER_INFO(' + \
            'id INTEGER PRIMARY KEY UNIQUE,' + \
            'username VARCHAR,' + \
            'password VARCHAR,' + \
            'last_login TIMESTAMP,' + \
            'created_date TIMESTAMP)'
        cursor = database.cursor()
        cursor.execute(users_table_query)

    @staticmethod
    def _create_devices_table(database: object) -> None:
        devices_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'DEVICE_INFO(' + \
            'id VARCHAR UNIQUE NOT NULL,' + \
            'user_id INT,' + \
            'label VARCHAR,' + \
            'device_handler VARCHAR,' + \
            'mn VARCHAR,' + \
            'model VARCHAR,' + \
            'PRIMARY KEY (id),' + \
            'FOREIGN KEY (user_id) REFERENCES USER_INFO(id))'
        cursor = database.cursor()
        cursor.execute(devices_table_query)

    @staticmethod
    def _create_poll_table(database: object) -> None:
        poll_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'POLL_INFO(' + \
            'id INTEGER PRIMARY KEY,' + \
            'device_id VARCHAR,' + \
            'poll_date TIMESTAMP,' + \
            'capability VARCHAR,' + \
            'attribute VARCHAR,' + \
            'value VARCHAR,' + \
            'unit VARCHAR,' + \
            'component VARCHAR,' + \
            'FOREIGN KEY (device_id) REFERENCES DEVICE_INFO(id))'
        cursor = database.cursor()
        cursor.execute(poll_table_query)

    def prov_user_devices(self, user_token):
        """
        prov_user_devices is invoked while
        gathering response data for Schema
        Discovery Requests.
        """
        try:
            db = sqlite3.connect(self.DB_URL)
        except OperationalError as e:
            logging.warning(e)
        else:
            cursor = db.cursor()
            return self._prov_user_devices(cursor, user_token)

    @staticmethod
    def _prov_user_devices(*info):
        cursor, user_token = info
        # From auth_token received, get
        # user id and return respective
        # devices.
        user_id_query = \
            'SELECT user_id FROM TOKEN_INFO ' + \
            'WHERE access_token="%s"' % user_token
        devices_query = \
            'SELECT * FROM DEVICE_INFO ' + \
            'WHERE user_id=(%s)' % user_id_query
        data = cursor.execute(devices_query)
        return data.fetchall()

    def polling_device(self, id_list: list, poll_data: dict=None):
        """
        prov_devices_poll is invoked while
        gathering response data for Schema
        State Refresh or Command Requests.
        """
        try:
            db = sqlite3.connect(self.DB_URL)
        except OperationalError as e:
            logging.warning(e)
        else:
            cursor = db.cursor()
            if not poll_data:
                return self._get_device_state(cursor, id_list)
            else:
                return self._put_device_state(cursor, id_list, poll_data)

    @staticmethod
    def _get_device_state(*info):
        # Output poll
        cursor, id_list = info
        # From list of ids, return
        # filtered results.
        if len(id_list) > 1:
            condition = 'IN '.format(tuple(id_list))
        else:
            condition = '="%s"' % id_list[0]
        # Elaborate Base query
        poll_query = \
            'SELECT * FROM POLL_INFO ' + \
            'WHERE device_id ' + \
            condition #filtered condition
        # Execute query
        data = cursor.execute(poll_query)
        return data.fetchall()

    @staticmethod
    def _put_device_state(*info):
        # Input poll
        cursor, device_id, data = info
        # Update POLL_INFO table based
        # on the device_id passed.
        poll_query = \
            'UPDATE POLL_INFO ' + \
            'SET ' + \
            'value="%s",' % data['value'] + \
            'poll_date="%s" ' % str(datetime.now()) + \
            'WHERE ' + \
            'device_id="%s" ' % device_id[0] + \
            'AND ' + \
            'capability="%s"' % data['capability']
        # Execute query
        cursor.execute(poll_query)

    def put_callback_info(self, callback_info: dict):
        try:
            db = sqlite3.connect(self.DB_URL)
            cursor = db.cursor()
            self._put_callback_info(cursor, callback_info)
        except OperationalError as e:
            logging.warning('DATABASE ERROR - %s' % e)
        else:
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _put_callback_info(*info):
        cursor, callback_data = info
        # Check if there are values
        cur_data = cursor.execute('SELECT * FROM CALLBACK_INFO WHERE id=1').fetchall()
        if not cur_data:
            # query
            q_callback = \
                'INSERT INTO CALLBACK_INFO ' + \
                '(callback_url,oauth_url,code,client_id,client_secret) ' + \
                'VALUES ' + \
                '(?,?,?,?,?)'
        else:
            q_callback = \
                'UPDATE CALLBACK_INFO ' + \
                'SET ' + \
                'callback_url=?,' + \
                'oauth_url=?,' + \
                'code=?,' + \
                'client_id=?,' + \
                'client_secret=? ' + \
                'WHERE id=1'
        # Execute query
        data = (callback_data['callback_url'],
                callback_data['oauth_url'],
                callback_data['code'],
                callback_data['client_id'],
                callback_data['client_secret'])
        cursor.execute(q_callback, data)

    def get_callback_info(self):
        try:
            db = sqlite3.connect(self.DB_URL)
            cursor = db.cursor()
            callback_info = self._get_callback_info(cursor)
        except OperationalError as e:
            logging.warning('DATABASE ERROR', e)
        else:
            db.close()
            return callback_info

    @staticmethod
    def _get_callback_info(cursor):
        q_callback = \
            'SELECT ' + \
            'oauth_url, code, client_id, client_secret ' + \
            'FROM CALLBACK_INFO ' + \
            'WHERE id=1'
        data = cursor.execute(q_callback)
        return data.fetchall()

    def get_access_token(self):
        try:
            db = sqlite3.connect(self.DB_URL)
            cursor = db.cursor()
            access_token = self._get_access_token(cursor)
        except OperationalError as e:
            logging.warning('DATABASE ERROR', e)
        else:
            db.close()
            return access_token

    @staticmethod
    def _get_access_token(cursor):
        q_token = \
            'SELECT cb_access_token ' + \
            'FROM CALLBACK_INFO ' + \
            'WHERE id=1'
        data = cursor.execute(q_token)
        return data.fetchone()

    def put_access_token(self, access_token, refresh_token):
        try:
            db = sqlite3.connect(self.DB_URL)
            cursor = db.cursor()
            self._put_access_token(cursor, access_token, refresh_token)
        except (OperationalError, IntegrityError) as e:
            logging.warning('DATABASE ERROR', e)
        else:
            db.commit()
            db.close()

    @staticmethod
    def _put_access_token(cursor, *token):
        q_token = \
            'UPDATE CALLBACK_INFO ' + \
            'SET ' + \
            'cb_access_token=?,' + \
            'cb_refresh_token=? ' + \
            'WHERE id=1'
        cursor.execute(q_token, token)

#############################################################
#############################################################
############# MOCK DATA FOR TESTING PURPOSES ################
#############################################################
#############################################################
    @staticmethod
    def _user_mock_inserts(database):
        from hashlib import md5

        cursor = database.cursor()
        cursor.execute('DELETE FROM USER_INFO')
        for i in range(1,200):
            q_user = \
                'INSERT INTO USER_INFO' + \
                '(username,password,last_login,created_date)' + \
                'VALUES ' + \
                '(?, ?, ?, ?)'
            cursor.execute(
                q_user,
                (f'TEST_USER_{i}', md5(b'mock_pass').hexdigest(), datetime.now(), datetime.now()
            ))

    @staticmethod
    def _token_mock_inserts(database):
        cursor = database.cursor()
        cursor.execute('DELETE FROM TOKEN_INFO')
        for i in range(1, 200)    :
            q_tkn = \
                'INSERT INTO TOKEN_INFO' +\
                '(user_id,access_token,refresh_token,last_update)' + \
                'VALUES ' + \
                '(%s,"access_token_%s","refresh_token_%s","%s")' % (i,i,i,datetime.now())
            cursor.execute(q_tkn)

    @staticmethod
    def _devices_mock_inserts(database):
        from random import randint, choice
        cursor = database.cursor()
        cursor.execute('DELETE FROM DEVICE_INFO')
        cursor.execute('DELETE FROM POLL_INFO')
        for i in range(1, 1000):
            # Devices query
            q_device = \
                'INSERT INTO DEVICE_INFO' + \
                '(id,user_id,label,device_handler,mn,model) ' + \
                'VALUES ' + \
                '(?,?,?,"c2c-switch","MNMN","MODEL")'
            cursor.execute(q_device, (f'x{i}', i, f'device_{randint(1,200)}'))
            # Poll query
            q_poll = \
                'INSERT INTO POLL_INFO' + \
                '(device_id,poll_date,capability,attribute,value,component) ' + \
                'VALUES' + \
                '("x%s","%s","st.switch","switch","%s","%s")' \
                % (i,datetime.now(),choice(['on','off']),choice(['main','secondary']))
            q_poll += \
                ',(?, ?, "st.healthCheck","healthStatus", ?, ?)'
            cursor.execute(
                q_poll,
                (f'x{i}',datetime.now(),choice(['online','offline']),choice(['main','secondary'])
            ))
