import jwt
import logging
import pickle
import os
from datetime import datetime
from lib.oauth.oauth_config import (USER_INFO_PATH,
                                    SECRET,
                                    ALGORITHM,
                                    TOKEN_TYPE)


# LOGGING CONFIG
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')


class User:
    def __init__(self, email, password, last_login):
        self.email = email
        self.password = password
        self.last_login = last_login
        self.access_token = None


class BearerToken:
    def __init__(self, **kwargs):
        self.access_token = kwargs.get('access_token')
        self.refresh_token = kwargs.get('refresh_token')
        self.code = kwargs.get('code')
        self.expires_in = kwargs.get('expires_in')
        self.token_type = kwargs.get('token_type')


class UserInformation():
    # def __init__(self):
    basedir = os.path.abspath(os.path.dirname(__file__))
    user_info_path = USER_INFO_PATH

    def new_user(self, *data):
        email, password = data
        new = User(email, password, str(datetime.now()))
        new.access_token = self._create_bearer_token(new)
        self._save_record(new.__dict__) # saving record at user_information.p
        return new.access_token['code']

    @staticmethod
    def _create_bearer_token(data):
        # Create BearerToken instance.
        # Returns __dict__ of class instance
        # with JWT tokens.
        #
        # Data to encode
        json_data = dict(email=data.email,
                         password=data.password,
                         timestamp=data.last_login)
        # Access Token
        json_data['grant'] = 'access'
        acc_token = jwt.encode(json_data, SECRET, algorithm=ALGORITHM)
        # Refresh Token
        json_data['grant'] = 'refresh'
        ref_token = jwt.encode(json_data, SECRET, algorithm=ALGORITHM)
        # Code
        json_data['grant'] = 'code'
        code = jwt.encode(json_data, SECRET, algorithm=ALGORITHM)
        del json_data['grant']
        expires_in = 3600
        # BearerToken instance
        bearer_token = BearerToken(access_token=acc_token,
                                   refresh_token=ref_token,
                                   code=code,
                                   expires_in=expires_in,
                                   token_type=TOKEN_TYPE)
        return bearer_token.__dict__

    def get_code(self):
        # Return code from for
        # GET Http Request at /authorize.
        pass

    def get_access_token(self):
        # Return tokens exchange for
        # POST Http Request at /token.
        pass

    def refresh_token(self):
        # Refresh user tokens.
        pass

    def _save_record(self, user_data):
        # Read file step
        file_path = self.basedir + self.user_info_path
        try:
            _file = open(file_path, 'rb')
            info = pickle.load(_file)
        except EOFError:
            # If file totally empty,
            # then insert [].
            _file = open(file_path, 'wb')
            pickle.dump([], _file)
            _file.close()
            return self._save_record(user_data)
        else:
            info = [] if not isinstance(info, list) else info
            info.append(user_data)
            _file = open(file_path, 'wb')
            pickle.dump(info, _file)
            _file.close()
            logging.info('user_data stored')

    def _load_record(self):
        # Read file step
        with open(self.basedir + self.user_info_path, 'rb') as info:
            return pickle.load(info)
