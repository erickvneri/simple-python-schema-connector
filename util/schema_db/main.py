# The SchemaDB module handles the storage
# of users, devices, tokens and callback
# arguments received at the Grant Callback
# Access interaction type
from dataclasses import dataclass
from datetime import datetime
from sqlite3 import OperationalError, IntegrityError
import sqlite3
import logging
import os
# Logger config.
logging.basicConfig(format='%(asctime)s - %(message)s')


@dataclass
class DB:
    """
    The DB is the main entity that
    containt CREATE TABLES statements
    to initialize the database and an
    init_session method to initialize
    a db context.
    """
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    DB_URL = f'{BASE_DIR}/schema_connector_db.sqlite'

    def init(self) -> None:
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

    def put_callback_info(self, callback_data: dict) -> None:
        # Check if there are values
        cur_data = self.init_session('SELECT * FROM CALLBACK_INFO WHERE id=1')
        if not cur_data:
            # query
            cb_query = \
                'INSERT INTO CALLBACK_INFO ' + \
                '(callback_url,oauth_url,code,client_id,client_secret) ' + \
                'VALUES ' + \
                '(?,?,?,?,?)'
        else:
            cb_query = \
                'UPDATE CALLBACK_INFO ' + \
                'SET ' + \
                'callback_url=?,' + \
                'oauth_url=?,' + \
                'code=?,' + \
                'client_id=?,' + \
                'client_secret=? ' + \
                'WHERE id=1'
        # parse data in tuple
        return self.init_session(
            cb_query,
            callback_data['callback_url'],
            callback_data['oauth_url'],
            callback_data['code'],
            callback_data['client_id'],
            callback_data['client_secret'])

    def get_callback_info(self):
        cb_query = \
            'SELECT ' + \
            'oauth_url, code, client_id, client_secret ' + \
            'FROM CALLBACK_INFO ' + \
            'WHERE id=1'
        return self.init_session(cb_query)

    def get_access_token(self):
        token_query = \
            'SELECT cb_access_token ' + \
            'FROM CALLBACK_INFO ' + \
            'WHERE id=1'
        return self.init_session(token_query)

    def put_access_token(self, access_token, refresh_token) -> None:
        token_query = \
            'UPDATE CALLBACK_INFO ' + \
            'SET ' + \
            'cb_access_token=?,' + \
            'cb_refresh_token=? ' + \
            'WHERE id=1'
        return self.init_session(token_query, access_token, refresh_token)

    def init_session(self, query, *args):
        # Script that initialize a db
        # connection and executes the
        # passed query.
        try:
            db = sqlite3.connect(self.DB_URL)
            cursor = db.cursor()
            result = cursor.execute(query, args).fetchall()
        except (OperationalError, IntegrityError) as e:
            logging.warning('Database Execution error - %s' % e )
        else:
            db.commit()
            db.close()
            return result

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
