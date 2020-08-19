from lib import MainDB


# DB Instance
db = MainDB()

if __name__ == '__main__':
    db.init()

    from lib.resources import Connector
    from pprint import pprint
    c = Connector()
    pprint(c.discovery_handler('asdfasd','access_token_925'))