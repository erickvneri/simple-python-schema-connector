"""
Docstring here...
"""
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from lib.webhook.my_connector import MyConnector
from lib.webhook.webhook_config import (ADDRESS,
                                        PORT,
                                        ENCODING,
                                        WEBHOOK_ENDPOINT)


class Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        # POST Http Request Handler
        if self.path != WEBHOOK_ENDPOINT:
            # Endpoint not supported
            self.send_error(HTTPStatus.BAD_REQUEST)

        content_length = int(self.headers['Content-Length'])
        req_body = self.rfile.read(content_length).decode(ENCODING)
        # Parse JSON string
        json_data = json.loads(req_body)
        self._authorize_request(json_data)

    def _authorize_request(self, json_data):
        authentication = json_data.get('authentication')
        if not authentication:
            self.send_error(HTTPStatus.UNAUTHORIZED)
        else:
            bearer_token = authentication.get('token')
            token_type = authentication.get('tokenType')
            if not bearer_token:
                self.send_error(HTTPStatus.UNAUTHORIZED)
            elif token_type and token_type != 'Bearer':
                self.send_error(HTTPStatus.UNAUTHORIZED)
            else:
                # if not self._authorize_bearer_token(bearer_token):
                    # self.send_error(HTTPStatus.UNAUTHORIZED)
                # Proceed to send interaction types
                # to the SchemaConnector instance.
                self._schema_connector_route(json_data)

    def _authorize_bearer_token(self):
        # Authorize Bearer Token
        # with OAuth Instance.
        raise NotImplementedError('Not implemented yet.')

    def _schema_connector_route(self, json_data):
        # Call to interacion_handler from
        # SchemaConnector Instance.
        my_connector = MyConnector()
        response_data = my_connector.interaction_handler(json_data)
        self._success_response(response_data)

    def _success_response(self, json_data):
        # Http Response envelope config
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        # Http Response body config
        json_response = json.dumps(json_data).encode(ENCODING)
        self.wfile.write(json_response)
