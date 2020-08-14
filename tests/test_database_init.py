import os
import sqlite3
import unittest
import time
from util.schema_db.main import DB

base_dir = os.path.dirname(os.path.realpath(__file__))

class TestDataBaseInit(unittest.TestCase):
    DB_TABLES = [
        'DEVICE_INFO',
        'USER_INFO',
        'TOKEN_INFO',
        'POLL_INFO',
        'CALLBACK_INFO'
    ]
    @classmethod
    def setUpClass(cls):
        cls.db = DB()
        cls.db.DB_URL = base_dir + 'test_db.sqlite'
        cls.db.init()

    @classmethod
    def tearDownClass(cls):
        os.remove(base_dir + 'test_db.sqlite')

    def setUp(self):
        self.conn = sqlite3.connect(self.db.DB_URL)
        cursor = self.conn.cursor()
        query = \
            'SELECT name ' + \
            'FROM sqlite_master'
        self.tables = cursor.execute(query).fetchall()

    def tearDown(self):
        self.conn.commit()
        self.conn.close()

    def test_database_tables(self):
        for table_name in self.DB_TABLES:
            db_table = list(filter(lambda t: t[0] == table_name, self.tables))
            self.assertEquals(table_name, db_table[0][0])
