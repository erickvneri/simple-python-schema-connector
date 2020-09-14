from urllib import parse
from hashlib import md5
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from lib.oauth.data import UserInformation
from lib.oauth.oauth_config import *

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


class OAuth2(BaseHTTPRequestHandler, UserInformation):
    """
    Module comments...
    """
    protocol_version=HTTP_V
    cookies = {}

    def do_GET(self):
        # GET Http Request handler
        path = parse.urlsplit(self.path).path
        # Handle path
        if path in _PUBLIC_PATH:
            # Handle public
            return self._handle_public_request(path)
        elif path in _PRIVATE_PATH:
            # Handle private
            return self._handle_private_request(path)
        else:
            return self.send_error(HTTPStatus.BAD_REQUEST)

    def do_POST(self):
        # POST Http Request handler
        ##### Reading Devices Reference #####
        path = parse.urlsplit(self.path)
        if path.path == '/final_path':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            devices_ref = set(parse.parse_qs(body))
            print(devices_ref)
        ####################################
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
        if path.path == AUTHORIZE_ENDPOINT:
            # Move along with authorization process
            if self._authorize_code_request(query):
                # Session persistence
                if query.get('state'):
                    state = query['state'][0]
                    cookie = self._set_cookie(state=state)
                return self._send_public_file(LOGIN_PAGE, cookie)
            # else:
                # Init Session control
                # return self.send_error(HTTPStatus.UNAUTHORIZED)

    def _handle_public_request(self, path):
        # Public Request handler:
        #   - POST /login
        if path == LOGIN_ENDPOINT:
            # Read Request Body
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(content_length).decode('utf-8')
            query = parse.parse_qs(req_body)
            # Collect user information
            user_email =  query['email'][0]
            user_pass = query['password'][0]
            # Create user registry
            # super().new_user(user_email,
                            #  md5(user_pass.encode('utf-8')).hexdigest())
            # If cookie
            if self.headers['Cookie']:
                cookie = self.headers['Cookie'].lstrip('Cookie: ')
            return self._send_public_file(DEVICES_PAGE, cookie)

    def _authorize_code_request(self, params):
        # Params to authorize
        response_type = params.get('response_type')
        client_id = params.get('client_id')
        redirect_uri = None if not params.get('redirect_uri') else params['redirect_uri'][0]
        # OAuth2.0 flow
        if response_type != [RESPONSE_TYPE]:
            # Response type check
            self.send_error(HTTPStatus.BAD_REQUEST)
        elif client_id != [CLIENT_ID]:
            # Client Id check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        elif not redirect_uri or redirect_uri not in REDIRECT_URI.split(','):
            # Redirect URI check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        else:
            return True

    def _send_public_file(self, public_file, cookie=None):
        # Send response
        self.send_response(HTTPStatus.OK)
        # Set Http Headers
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', int(len(public_file)))
        self.send_header('Connection', 'keep-alive')
        self.send_header('keep-alive', 'timeout=10, max=5')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(public_file)

    def _set_cookie(self, **params):
        encode_data = {k: v for k, v in params.items()}
        cookie = md5(str(encode_data).encode('utf-8')).hexdigest()
        self.cookies[cookie] = encode_data
        return cookie
