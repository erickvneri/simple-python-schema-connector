import os

public_files_path = os.path.abspath(os.path.dirname(__file__) + '/../public')
# PUBLIC FILES
LOGIN_PAGE=public_files_path + '/login.html'
DEVICES_PAGE=public_files_path + '/devices.html'
LOGIN_ENDPOINT='/login'

# PRIVATE FILES
AUTHORIZE_ENDPOINT='/authorize'
TOKEN_ENDPOINT='/token'
CLIENT_ID='my-oauth2.0-instance-client-id'
CLIENT_SECRET='my-oauth2.0-instance-client-secret'
REDIRECT_URI='https://c2c-us.smartthings.com/oauth/callback,https://c2c-eu.smartthings.com/oauth/callback,https://c2c-ap.smartthings.com/oauth/callback'
RESPONSE_TYPE='code'

# JWT INFO & DATA INFO
SECRET='my-schema-connector-webhook'
USER_INFO_PATH='/user_info.b'
ALGORITHM='HS256'
TOKEN_TYPE='Bearer'
# APP CONFIG
ADDRESS='127.0.0.1'
PORT=5000
