import json
from urllib import parse
from hashlib import md5
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from lib.oauth.data import UserInformation
from lib.oauth.oauth_config import (
    LOGIN_ENDPOINT,
    LOGIN_PAGE,
    AUTHORIZE_ENDPOINT,
    TOKEN_ENDPOINT,
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    RESPONSE_TYPE,
    HTTP_VERSION
)

# PATH CONFIG REFERENCE
_PUBLIC_PATH = [LOGIN_ENDPOINT, LOGIN_PAGE]

_PRIVATE_PATH = [
    AUTHORIZE_ENDPOINT,
    TOKEN_ENDPOINT,
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URI,
    RESPONSE_TYPE,
]


class OAuth2(BaseHTTPRequestHandler, UserInformation):
    """
    This example OAuth2.0 client follows
    the Code Flow principle described
    by the RFC 6749 which is the the
    Authorization flow currently supported
    at SmartThings to integrate Third-party
    Clouds as ST Schema Integrations.

    Once GET Http Request for code has
    been authorized, LOGIN view will be
    exposed with a list of test devices
    to select.
    """

    protocol_version = HTTP_VERSION
    cookies = {}

    def do_GET(self):
        """
        GET Http Request handler
        """
        path = parse.urlsplit(self.path)
        # Handle path
        if path.path in _PUBLIC_PATH:
            # Handle request for public
            # resource.
            self._handle_public_request(path)
        elif path.path in _PRIVATE_PATH:
            # Handle request for private
            # resource.
            self._handle_private_request(path)
        else:
            self.send_error(HTTPStatus.BAD_REQUEST)

    def do_POST(self):
        """
        POST Http Request handler
        """
        path = parse.urlsplit(self.path)
        # Handle path
        if path.path in _PUBLIC_PATH:
            # Handle request for public
            # resource.
            self._handle_public_request(path)
        elif path.path in _PRIVATE_PATH:
            # Handle request for private
            # resource.
            self._handle_private_request(path)

    def _handle_private_request(self, path):
        # Private request handler:
        #   - Code GET Http Request
        #   - Token POST Http Request
        if path.path == AUTHORIZE_ENDPOINT:
            # Authorization of Code Http Request.
            query = parse.parse_qs(path.query)
            if self._authorize_code_request(query):
                # If request has state,
                # persist session.
                if query.get("state"):
                    state = query["state"][0]
                    redirect_uri = query["redirect_uri"][0]
                    cookie = self._set_cookie(state=state, redirect_uri=redirect_uri)
                self._send_public_file(LOGIN_PAGE, cookie)

        elif path.path == TOKEN_ENDPOINT:
            # Authorization of Token Http Request.
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")
            params = parse.parse_qs(body)

            if self._authorize_token_request(params):
                grant_type = params.get("grant_type")[0]
                if grant_type == "authorization_code":
                    # Return access token
                    code = params.get("code")
                    access_token = super().get_access_token(code)
                    self._send_access_token(access_token)
                elif grant_type == "refresh_token":
                    pass

    def _handle_public_request(self, path):
        # Public Request handler:
        #   - POST /login
        if path.path == LOGIN_ENDPOINT:
            # Collect Http Request
            # information.
            content_length = int(self.headers["Content-Length"])
            req_body = self.rfile.read(content_length).decode("utf-8")
            query = parse.parse_qs(req_body)
            cookie = self.headers.get("Cookie", None)
            # Current session
            session = self.cookies[cookie]
            redirect_uri = session["redirect_uri"]
            state = session["state"]

            # Process user data
            user_email = query.pop("email")[0]
            user_pass = query.pop("password")[0]
            user_pass = md5(user_pass.encode("utf-8")).hexdigest()

            # At this point, users should
            # have a valid third-party account
            # to integrate devices into
            # third-parties.
            user_id = super().grant_user_access(user_email, user_pass)
            # Update current cookie to
            # track user bearer token at
            # Token Request.
            self._update_cookie(cookie, user_id=user_id)

            # Parse device type info
            devices = dict(devices=list(query.keys()))
            code = super().create_bearer_token(devices=devices, user_id=user_id)

            self._redirect_code(redirect_uri, code=code, state=state)

    def _authorize_code_request(self, params):
        # Params to authorize
        response_type = params.get("response_type")
        client_id = params.get("client_id")
        redirect_uri = (
            None if not params.get("redirect_uri") else params["redirect_uri"][0]
        )
        # OAuth2.0 flow
        if response_type != [RESPONSE_TYPE]:
            # Response type check
            self.send_error(HTTPStatus.BAD_REQUEST)
        elif client_id != [CLIENT_ID]:
            # Client Id check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        elif not redirect_uri or redirect_uri not in REDIRECT_URI.split(","):
            # Redirect URI check
            self.send_error(HTTPStatus.UNAUTHORIZED)
        else:
            return True

    def _authorize_token_request(self, params):
        # Params
        auth_header = self.headers.get("Authorization")
        client_id = params.get("client_id")
        client_secret = params.get("client_secret")
        redirect_uri = (
            None if not params.get("redirect_uri") else params["redirect_uri"][0]
        )
        code = params.get("code")
        # Authorization steps.
        if not auth_header:
            # Unauthorize requests with no Basic Auth Header
            self.send_error(HTTPStatus.UNAUTHORIZED)
        # Basic Authorization Header check
        if self._authorize_basic_header(auth_header):
            if client_id != [CLIENT_ID]:
                # Client Id check
                self.send_error(HTTPStatus.UNAUTHORIZED)
            elif client_secret != [CLIENT_SECRET]:
                # Client Secret check
                self.send_error(HTTPStatus.UNAUTHORIZED)
            elif not redirect_uri or redirect_uri not in REDIRECT_URI.split(","):
                # Redrect URI check
                self.send_error(HTTPStatus.UNAUTHORIZED)
                # Code check
            elif not code:
                self.send_error(HTTPStatus.UNAUTHORIZED)
            else:
                return True

    @staticmethod
    def _authorize_basic_header(basic_cred):
        import base64

        # Encode mock credentials to
        # compare Basic Auth Header.
        app_cred = f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")
        encoded_cred = base64.b64encode(app_cred).decode("utf-8")

        # Basic Authorization header validation
        if basic_cred.lstrip("Basic ") != encoded_cred:
            return False
        else:
            return True

    def _send_public_file(self, public_file, cookie=None):
        # Send response
        self.send_response(HTTPStatus.OK)
        # Set Http Headers
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", int(len(public_file)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(public_file)

    def _redirect_code(self, url, **params):
        qs = parse.urlencode(params)
        self.send_response(HTTPStatus.MOVED_PERMANENTLY)
        self.send_header("Location", f"{url}?{qs}")
        self.end_headers()

    def _send_access_token(self, token_data):
        encoded_token = json.dumps(token_data).encode("utf-8")
        # Response headers
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", int(len(encoded_token)))
        self.end_headers()
        self.wfile.write(encoded_token)

    def _set_cookie(self, **params):
        cookie = md5(str(params).encode("utf-8")).hexdigest()
        self.cookies[cookie] = params
        return cookie

    def _update_cookie(self, cookie, **params):
        for key, value in params.items():
            self.cookies[cookie][key] = value
