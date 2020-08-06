# The SchemaDB module handles the storage
# of users, devices, tokens and callback
# arguments received at the Grant Callback
# Access interaction type
from stschema import SchemaDevice
from dataclasses import dataclass
import logging
import sqlite3
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
        except sqlite3.OperationalError as e:
            logging.warning('DATABASE ERROR - %s' % e)
        finally:
            db.close()

    def _create_all(self, database):
        self._create_callback_table(database)
        self._create_tokens_table(database)
        self._create_devices_table(database)
        self._create_poll_table(database)
        self._create_user_table(database)

    @staticmethod
    def _create_callback_table(database: object) -> None:
        callback_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'CALLBACK_ARGS(' + \
            'id INT AUTO_INCREMENT,' + \
            'callback_url VARCHAR,' + \
            'oauth_url VARCHAR,' + \
            'code VARCHAR,' + \
            'client_id VARCHAR,' + \
            'client_secret VARCHAR,' + \
            'PRIMARY KEY (id))'

        cursor = database.cursor()
        cursor.execute(callback_table_query)

    @staticmethod
    def _create_tokens_table(database: object) -> None:
        token_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'TOKEN_INFO(' + \
            'id INT AUTO_INCREMENT,' + \
            'access_token VARCHAR,' + \
            'refresh_token VARCHAR,' + \
            'last_update TIMESTAMP,' + \
            'PRIMARY KEY (id))'
        cursor = database.cursor()
        cursor.execute(token_table_query)

    @staticmethod
    def _create_user_table(database: object) -> None:
        users_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'USER_INFO(' + \
            'id INT AUTO_INCREMENT,' + \
            'username VARCHAR,' + \
            'password VARCHAR,' + \
            'last_login TIMESTAMP,' + \
            'created_date TIMESTAMP,' + \
            'PRIMARY KEY (id))'
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
            'model VARCHAR,' + \
            'room VARCHAR,' + \
            'PRIMARY KEY (id),' + \
            'FOREIGN KEY (user_id) REFERENCES USER_INFO(id))'
        cursor = database.cursor()
        cursor.execute(devices_table_query)

    @staticmethod
    def _create_poll_table(database: object) -> None:
        poll_table_query = \
            'CREATE TABLE IF NOT EXISTS ' + \
            'POLL_INFO(' + \
            'id INT AUTO_INCREMENT,' + \
            'device_id VARCHAR,' + \
            'poll_date TIMESTAMP,' + \
            'capability VARCHAR,' + \
            'attribute VARCHAR,' + \
            'value VARCHAR,' + \
            'PRIMARY KEY (id),' + \
            'FOREIGN KEY (device_id) REFERENCES DEVICE_INFO(id))'
        cursor = database.cursor()
        cursor.execute(poll_table_query)
