import logging
from urllib import parse
from hashlib import md5
from http import HTTPStatus
from http.server import (BaseHTTPRequestHandler,
                         HTTPServer)
from data import UserInformation
from oauth_config import (ADDRESS,
                          PORT,
                          AUTHORIZE_ENDPOINT,
                          TOKEN_ENDPOINT,
                          CLIENT_ID,
                          CLIENT_SECRET,
                          REDIRECT_URI,
                          RESPONSE_TYPE,
                          LOGIN_PAGE,
                          DEVICES_PAGE,
                          LOGIN_ENDPOINT)

# PATH CONFIG REFERENCE
_PUBLIC_PATH = [LOGIN_PAGE,
                DEVICES_PAGE,
                LOGIN_ENDPOINT]

_PRIVATE_PATH = [AUTHORIZE_ENDPOINT,
                 TOKEN_ENDPOINT,
                 CLIENT_ID,
                 CLIENT_SECRET,
                 REDIRECT_URI,
                 RESPONSE_TYPE]


# LOGGING CONFIG
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')


class OAuth2(BaseHTTPRequestHandler, UserInformation):
    """
    Module comments...
    """
    def do_GET(self):
        # GET Http Request handler
        path = parse.urlsplit(self.path).path
        # Handle path
        if path in _PUBLIC_PATH:
            return self._handle_public_request(path)
        elif path in _PRIVATE_PATH:
            # Handle private path
            if path == AUTHORIZE_ENDPOINT:
                return self._handle_private_request(path)
            else:
                return self.send_error(HTTPStatus.BAD_REQUEST)

    def do_POST(self):
        # POST Http Request handler
        path = parse.urlsplit(self.path).path
        # Handle path
        if path in _PUBLIC_PATH:
            return self._handle_public_request(path)

    def _handle_private_request(self, path):
        # Private request handler:
        #   - Code GET Http Request
        #   - Token POST Http Request
        path = parse.urlsplit(self.path)
        query = parse.parse_qs(path.query)

        if path == AUTHORIZE_ENDPOINT:
            if not self._authorize_code_request(query):
                # Move along with authorization process
                return self.send_error(HTTPStatus.UNAUTHORIZED)
            else:
                return self._send_public_file(LOGIN_PAGE)

    def _handle_public_request(self, path):
        # Public Request handler:
        #   - GET /login
        if path == LOGIN_ENDPOINT:
            # Read Request Body
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(content_length).decode('utf-8')
            query = parse.parse_qs(req_body)
            # Collect user information
            user_email =  query['email'][0]
            user_pass = query['password'][0].encode('utf-8')
            # Create user registry
            super().new_user(user_email,
                             md5(user_pass).hexdigest())
            logging.info('\n\nHttp Headers %s ' % self.headers)
            return self._send_public_file(DEVICES_PAGE)

    def _authorize_code_request(self, params):
        # OAuth2.0 flow
        if params['response_type'][0] != RESPONSE_TYPE:
            # Response type check
            self.send_error(HTTPStatus.BAD_REQUEST)
        elif params['client_id'][0] != CLIENT_ID:
            # Client Id check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        elif params['redirect_uri'][0] not in REDIRECT_URI.split(','):
            # Redirect URI check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        print(query)
        return True

    def _send_public_file(self, path):
        # Read public file
        with open(path, 'r') as public_file:
            response = public_file.read().encode('utf-8')
        # Send response
        self.send_response(HTTPStatus.OK)
        # Set Http Headers
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(response)


if __name__ == "__main__":
    import sys
    address = ('0.0.0.0', PORT)
    http = HTTPServer(address, OAuth2)
    logging.info(f'OAuth2.0 service running at: {ADDRESS}:{PORT}')
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        logging.warning('OAuth2.0 service aborted!!')
        sys.exit()

# import cgi
# form_data = cgi.FieldStorage(fp=self.rfile,
#                                 headers=self.headers,
#                                 environ={'REQUEST_METHOD': 'POST',
#                                         'CONTENT_TYPE': self.headers['Content-Type']})
# print(form_data)
# client_id = form_data['client_id'].value
# redirect_uri = form_data['redirect_uri'].value
# state = form_data['state'].value

# import pickle
# _file = '/home/bts/Documents/Projects/ST-Schema-Pyhton-SDK/ST-Schema-Python-Samples/simple-python-schema-connector/lib/oauth/data/user_info.b'
# o = open(_file, 'rb')
# data = pickle.load(o)
# print(data)
# if not data:
#     print(data)
#     data = []
#     o = open(_file, 'wb')
#     pickle.dump(data, o)
# o.close()

