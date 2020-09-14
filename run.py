import sys
import argparse
import logging
from http.server import HTTPServer
from lib.oauth import oauth_config, OAuth2
from lib.webhook import webhook_config, Webhook


# LOGGING CONFIG
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# SUPPORTED SERVICES
OAUTH_SERVICE='oauth'
WEBHOOK_SERVICE='webhook'

# CLI ARG PARSER
cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('-s', '--service')
arg = cli_parser.parse_args()

# APP INIT
if __name__ == "__main__":
    if arg.service == OAUTH_SERVICE:
        service = OAuth2
        app_address = oauth_config.ADDRESS
        app_port = oauth_config.PORT
    elif arg.service == WEBHOOK_SERVICE:
        service = Webhook
        app_address = webhook_config.ADDRESS
        app_port = webhook_config.PORT

    address = (app_address, app_port)
    http = HTTPServer(address, service)
    logging.info(f'{service.__name__} service running at: {app_address}:{app_port}')
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.warning(f'{service.__name__} service aborted!!')
        sys.exit()
