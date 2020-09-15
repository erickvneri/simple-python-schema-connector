import jwt
import logging
import pickle
import os
from hashlib import md5
from datetime import datetime
from lib.oauth.oauth_config import (USER_INFO_PATH,
                                    SECRET,
                                    ALGORITHM,
                                    TOKEN_TYPE,
                                    CLIENT_ID)


# LOGGING CONFIG
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s')


class User:
    def __init__(self, email, password, last_login):
        self.email = email
        self.password = password
        self.last_login = last_login
        self.user_id = None
        self.bearer_token = None


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

    def grant_access_user(self, *data):
        email, password = data
        new = User(email, password, str(datetime.now()))
        new.user_id = md5(str(new.__dict__).encode('utf-8')).hexdigest()
        self._save_record(new.__dict__) # saving record at user_information.p
        return new.user_id

    def create_bearer_token(self, **data):
        # Create BearerToken instance.
        # Returns __dict__ of class instance
        # with JWT tokens.
        #
        # Data to encode
        access_jwt_data = dict(devices=data.get('devices'))
        refresh_jwt_data = dict(user_id=data.get('user_id'))
        # Create JSON Web Tokens
        acc_token = jwt.encode(access_jwt_data, SECRET, algorithm=ALGORITHM).decode('utf-8')
        ref_token = jwt.encode(refresh_jwt_data, SECRET, algorithm=ALGORITHM).decode('utf-8')
        expires_in = 3600
        code = md5(CLIENT_ID.encode('utf-8')).hexdigest()
        # BearerToken instance
        bearer_token = BearerToken(access_token=acc_token,
                                   refresh_token=ref_token,
                                   code=code,
                                   expires_in=expires_in,
                                   token_type=TOKEN_TYPE)
        # Update user data to include
        # set of JWT Tokens.
        self._save_bearer_token(user_id=data.get('user_id'),
                                bearer_token=bearer_token.__dict__)

        logging.info('authorization code generated.')
        return code

    def _save_bearer_token(self, **data) -> None:
        file_path = self.basedir + self.user_info_path
        # Read file step
        _file = open(file_path, 'rb')
        info = pickle.load(_file)
        # Filter user
        user = list(filter(lambda u: u['user_id'] == data['user_id'], info))
        user[0]['bearer_token'] = data['bearer_token']

        # Write file step
        _file = open(file_path, 'wb')
        pickle.dump(info, _file)
        _file.close()
        logging.info('bearer token saved.')

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
            logging.info('new user information stored')
