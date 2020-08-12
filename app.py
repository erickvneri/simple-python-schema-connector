from util import SchemaDB


# DB Instance
db = SchemaDB()

if __name__ == '__main__':
    db.init_db()

    from util import DeviceProvider
    d = DeviceProvider()
    devices = d.put_device_state(['x10'],'healthCheck','offline')