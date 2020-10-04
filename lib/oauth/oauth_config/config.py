import os
import dotenv

# LOAD ENVIRONMENT VARIABLES
dotenv.load_dotenv()

# PUBLIC FILES
LOGIN_ENDPOINT=os.getenv('LOGIN_ENDPOINT')
# HTML FILES PRELOAD
public_files_path = os.path.abspath(os.path.dirname(__file__) + '/../public')
with open(public_files_path + '/login.html') as view:
    LOGIN_PAGE=view.read().encode('utf-8')

# PRIVATE FILES
AUTHORIZE_ENDPOINT=os.getenv('AUTHORIZE_ENDPOINT')
TOKEN_ENDPOINT=os.getenv('TOKEN_ENDPOINT')
CLIENT_ID=os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
REDIRECT_URI=os.getenv('REDIRECT_URI')
RESPONSE_TYPE=os.getenv('RESPONSE_TYPE')

# JWT INFO & DATA INFO
SECRET=os.getenv('SECRET')
USER_INFO_PATH=os.getenv('USER_INFO_PATH')
ALGORITHM=os.getenv('ALGORITHM')
TOKEN_TYPE=os.getenv('TOKEN_TYPE')

# APP CONFIG
ADDRESS=os.getenv('OAUTH_ADDRESS')
PORT=int(os.getenv('OAUTH_PORT'))
HTTP_VERSION=os.getenv('HTTP_VERSION')
