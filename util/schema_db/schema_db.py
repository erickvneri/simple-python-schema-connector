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

    def prov_user_devices(self, user_tkn):
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
            return self._prov_user_devices(cursor, user_tkn)

    @staticmethod
    def _prov_user_devices(*info):
        cursor, param = info
        # From auth_token received, get
        # user id and return respective
        # devices.
        user_id_query = \
            'SELECT user_id FROM TOKEN_INFO ' + \
            'WHERE access_token="%s"' % param
        devices_query = \
            'SELECT * FROM DEVICE_INFO ' + \
            'WHERE user_id=(%s)' % user_id_query
        data = cursor.execute(devices_query)
        return data.fetchall()

    def prov_device_poll(self, id_list: list):
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
            return self._prov_device_poll(cursor, id_list)

    @staticmethod
    def _prov_device_poll(*info):
        cursor, id_list = info
        # Fron list of ids, return
        # filtered results.
        poll_query = \
            'SELECT * FROM POLL_INFO ' + \
            'WHERE device_id ' + \
            'IN {}'.format(tuple(id_list))
        data = cursor.execute(poll_query)
        return data.fetchall()

#############################################################
#############################################################
############# MOCK DATA FOR TESTING PURPOSES ################
#############################################################
#############################################################
    @staticmethod
    def _user_mock_inserts(database):
        cursor = database.cursor()
        cursor.execute('DELETE FROM USER_INFO')
        for i in range(1,200):
            q_user = \
                'INSERT INTO USER_INFO' + \
                '(username, password,last_login,created_date)' + \
                'VALUES ' + \
                '("USER_%s","PASS","%s", "%s")' % (i,datetime.now(),datetime.now())
            cursor.execute(q_user)

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
                '("x%s", %i, "device_%s","c2c-switch","MNMN","MODEL")' % (i,randint(1,200),i)
            cursor.execute(q_device)
            # Poll query
            q_poll = \
                'INSERT INTO POLL_INFO' + \
                '(device_id,poll_date,capability,attribute,value,component) ' + \
                'VALUES' + \
                '("x%s","%s","switch","switch","%s","%s")' \
                % (i,datetime.now(),choice(['on','off']),choice(['main','secondary']))
            q_poll += \
                ',("x%s", "%s", "healthCheck","healthStatus","%s","%s")' \
                % (i,datetime.now(),choice(['online','offline']),choice(['main','secondary']))
            cursor.execute(q_poll)

