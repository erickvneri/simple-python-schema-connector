import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from lib.webhook.webhook_config import (ADDRESS,
                                        PORT,
                                        ENCODING,
                                        WEBHOOK_ENDPOINT)


class Webhook(BaseHTTPRequestHandler):
    """
    Comments here...
    """
    def do_POST(self):
        # POST Http Request Handler
        if self.path != WEBHOOK_ENDPOINT:
            # Endpoint not supported
            return self.send_error(HTTPStatus.BAD_REQUEST)

        content_length = int(self.headers['Content-Length'])
        req_body = self.rfile.read(content_length).decode(ENCODING)
        # Parse JSON string
        json_data = json.loads(req_body)
        return self._authorize_request(json_data)

    def _authorize_request(self, data):
        authentication = data.get('authentication')
        if not authentication:
            return self.send_error(HTTPStatus.UNAUTHORIZED)
        else:
            bearer_token = authentication.get('token')
            token_type = authentication.get('tokenType')
            if not bearer_token:
                return self.send_error(HTTPStatus.UNAUTHORIZED)
            elif token_type and tokenType != 'Bearer':
                return self.send_error(HTTPStatus.UNAUTHORIZED)
            else:
                if not self._authorize_bearer_token(bearer_token):
                    return self.send_error(HTTPStatus.UNAUTHORIZED)
                else:  # FIXME: Extra indentation could be deleted
                    user_data = self._decode_bearer_token(bearer_token)['devices']
                    return self._schema_connector_route(data, user_data)

    def _authorize_bearer_token(self):
        # Authorize Bearer Token
        # with OAuth Instance.
        raise NotImplementedError('Not implemented yet.')

    def _decode_bearer_token(self):
        # Decode Bearer Token to access
        # device selection from OAuth
        # user config flow.
        raise NotImplementedError('Not implemented yet.')

    def _schema_connector_route(self, *args):
        # Call to interacion_handler from
        # SchemaConnector Instance.
        raise NotImplementedError('Not implemented yet.')

    def _success_response(self, data):
        # Http Response envelope config
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        # Http Response body config
        json_response = json.dumps(data).encode(ENCODING)
        self.wfile.write(json_response)
