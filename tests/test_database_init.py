import os
import sqlite3
import unittest
from random import randint
from sqlite3 import InterfaceError, IntegrityError
from util import MainDB

base_dir = os.path.dirname(os.path.realpath(__file__))

class TestDatabaseTables(unittest.TestCase):
    """
    Test case to verify unique and
    data constraints about columns
    declared.
    """
    @classmethod
    def setUpClass(cls):
        # Create test_db.sqlite file and
        # call init() method to create
        # all respective tables.
        db = MainDB()
        db.DB_URL = base_dir + 'test_db.sqlite'
        db.init()
        # Connection
        cls.connection = sqlite3.connect(db.DB_URL)
        cls.session = cls.connection.cursor()

    def setUp(self):
        # Lambda function that returns
        # an implemented data type from
        # the datat pereceived. Ease
        # the instantiation of different
        # datatypes.
        self.dtypes = lambda type: \
            int(123) if type == int else \
            bytes(b'bytes') if type == bytes else \
            list('list') if type == list else \
            dict(key='value') if type == dict else \
            set('set') if type == set else \
            frozenset('frozenset') if type is frozenset else \
            str('string')

    def _test_data_types(self, query: str, range_values: int):
        """
        Internal function that will test
        iterate and execute queries on not
        supported data types.
        """
        not_supported_types = [list, dict, set, frozenset]
        i, t = 0, 0
        while t < len(not_supported_types):
            values = [f'DEFAULT_VALUE{randint(0,1000)}' for _ in range(range_values)]
            values[i] = self.dtypes(not_supported_types[t])
            i += 1
            if i == len(values):
                i = 0
                t += 1
            with self.assertRaises(InterfaceError):
                self.session.execute(query, values)

    def test_defined_tables(self):
        q = 'SELECT name FROM sqlite_master'
        tables = [table[0] for table in self.session.execute(q).fetchall()]
        self.assertIn('USER_INFO', tables)
        self.assertIn('DEVICE_INFO', tables)
        self.assertIn('POLL_INFO', tables)
        self.assertIn('CALLBACK_INFO', tables)
        self.assertIn('TOKEN_INFO', tables)

    def test_devices_unique_constraint(self):
        q = 'INSERT INTO DEVICE_INFO ' + \
            '(id,user_id,label,device_handler,mn,model) ' + \
            'VALUES ' + \
            '(?,?,?,?,?,?)'
        values = ['UNIQUE_DEVICE_ID' for _ in range(6)]
        # First execution
        self.session.execute(q, values)
        with self.assertRaises(IntegrityError):
            # Second execution with same
            # device_id as argument.
            self.session.execute(q, values)

    def test_device_info_table_not_supported_types(self):
        q = 'INSERT INTO DEVICE_INFO ' + \
            '(id,user_id,label,device_handler,mn,model) ' + \
            'VALUES ' + \
            '(?,?,?,?,?,?)'
        self._test_data_types(q, 6)

    def test_callback_info_not_supported_types(self):
        q = 'INSERT INTO CALLBACK_INFO ' + \
            '(callback_url,oauth_url,code,client_id,client_secret,cb_access_token,cb_refresh_token) ' + \
            'VALUES ' + \
            '(?,?,?,?,?,?,?)'
        self._test_data_types(q, 7)

    def  test_token_info_not_supported_types(self):
        q = 'INSERT INTO TOKEN_INFO ' + \
            '(user_id,access_token,refresh_token,last_update) ' + \
            'VALUES ' + \
            '(?,?,?,?)'
        self._test_data_types(q, 4)

    def test_user_info_not_supported_types(self):
        q = 'INSERT INTO USER_INFO ' + \
            '(username,password,last_login,created_date) ' + \
            'VALUES ' + \
            '(?,?,?,?)'
        self._test_data_types(q, 4)

    def test_poll_info_not_supported_types(self):
        q = 'INSERT INTO POLL_INFO ' + \
            '(device_id,poll_date,capability,attribute,value,unit,component)' + \
            'VALUES ' + \
            '(?,?,?,?,?,?,?)'
        self._test_data_types(q, 7)

    def tearDown(self):
        self.connection.commit()

    @classmethod
    def tearDownClass(cls):
        # Close connection
        cls.connection.close()
        # Delete test_db.sqlite file created
        os.remove(base_dir + 'test_db.sqlite')
