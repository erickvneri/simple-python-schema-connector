from urllib import parse
from hashlib import md5
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from lib.oauth.data import UserInformation
from lib.oauth.oauth_config import *

# PATH CONFIG REFERENCE
_PUBLIC_PATH = [LOGIN_ENDPOINT,
                LOGIN_PAGE]

_PRIVATE_PATH = [AUTHORIZE_ENDPOINT,
                 TOKEN_ENDPOINT,
                 CLIENT_ID,
                 CLIENT_SECRET,
                 REDIRECT_URI,
                 RESPONSE_TYPE]


class OAuth2(BaseHTTPRequestHandler, UserInformation):
    """
    This Test OAuth2.0 client follows
    the Code Flow principle described
    by the RFC 6749 which is the the
    Authorization flow currently supported
    at SmartThings to integrate Third-party
    Clouds.

    After client authorization, this
    client offers two views:
        - Login
        - Device selection

    The Device selection view offers a
    predefined list of devices that will
    be sent as Access Token and decoded
    by the SchemaConnector instance
    implemented at the lib.webhook module.
    """
    protocol_version=HTTP_VERSION
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
        path = parse.urlsplit(self.path).path
        # Handle path
        if path in _PUBLIC_PATH:
            return self._handle_public_request(path)
        elif path in _PRIVATE_PATH:
            return self._handle_private_request(path)

    def _handle_private_request(self, path):
        # Private request handler:
        #   - Code GET Http Request
        #   - Token POST Http Request
        path = parse.urlsplit(self.path)
        if path.path == AUTHORIZE_ENDPOINT:
            # Move along with authorization process.
            query = parse.parse_qs(path.query)
            if self._authorize_code_request(query):
                # If request authorized,
                # persist session.
                if query.get('state'):
                    state = query['state'][0]
                    redirect_uri = query['redirect_uri'][0]
                    cookie = self._set_cookie(state=state,
                                              redirect_uri=redirect_uri)
                return self._send_public_file(LOGIN_PAGE, cookie)

        elif path.path == TOKEN_ENDPOINT:
            # Move along with token request
            # authorization.
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(content_length).decode('utf-8')
            query = parse.parse_qs(req_body)

            # Check Authorization Headers
            if not self.headers.get('Authorization'):
                self.send_error(HTTPStatus.UNAUTHORIZED)
            elif self._authorize_token_request(query):
                pass

    def _handle_public_request(self, path):
        # Public Request handler:
        #   - POST /login
        #   - POST /login/devices
        if path == LOGIN_ENDPOINT:
            # Collect Http Request
            # information.
            content_length = int(self.headers['Content-Length'])
            req_body = self.rfile.read(content_length).decode('utf-8')
            query = parse.parse_qs(req_body)
            cookie = self.headers.get('Cookie', None)
            # Current session
            session = self.cookies[cookie]
            redirect_uri = session['redirect_uri']
            state = session['state']

            # Process user data
            user_email = query.pop('email')[0]
            user_pass = query.pop('password')[0]
            user_pass = md5(user_pass.encode('utf-8')).hexdigest()

            # At this point, users should
            # have a valid third-party account
            # to integrate devices into
            # third-parties.
            user_id = super().grant_user_access(user_email,
                                                user_pass)
            # Update current cookie to
            # track user bearer token at
            # Token Request.
            self._update_cookie(cookie, user_id=user_id)

            # Parse device type info
            devices = dict(devices=list(query.keys()))
            code = super().create_bearer_token(devices=devices,
                                               user_id=user_id)

            self._redirect_code(redirect_uri, code=code, state=state)
        else:
            self.send_error(HTTPStatus.BAD_REQUEST)

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

    def _authorize_token_request(self, params):
        # 1. Basic Authentication
        # 2. Params.
        print(params)
        pass

    def _authorize_basic_header(self):
        cred = self.headers.get('Authorization')
        pass

    def _send_public_file(self, public_file, cookie=None):
        # Send response
        self.send_response(HTTPStatus.OK)
        # Set Http Headers
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', int(len(public_file)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(public_file)

    def _redirect_code(self, url, **params):
        qs = parse.urlencode(params)
        self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        self.send_header('Location', f'{url}?{qs}')
        self.end_headers()

    def _set_cookie(self, **params):
        encode_data = {k: v for k, v in params.items()}
        cookie = md5(str(encode_data).encode('utf-8')).hexdigest()
        self.cookies[cookie] = encode_data
        return cookie

    def _update_cookie(self, cookie, **params):
        for k, v in params.items():
            self.cookies[cookie][k] = v
