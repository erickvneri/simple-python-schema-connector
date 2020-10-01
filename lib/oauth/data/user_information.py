"""
To simplify the storage of user and
token information, this module will
serve as database saving data in
binary form using the pickle built-in
module.

In addition, to avoid massive data
storage, the <user_info.p> file
will store only one record, therefore,
data will be overwritten at every
login attempt, e.g.:
  [{
      "email": ...,
      "password"...,
      "bearer_token": {...},
  }].
"""
from datetime import datetime
import logging
import pickle
import os
import secrets
import jwt
from lib.oauth.oauth_config import (
    USER_INFO_PATH,
    SECRET,
    ALGORITHM,
    TOKEN_TYPE
)


# LOGGING CONFIG
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class User:
    def __init__(self, email, password, last_login):
        self.email = email
        self.password = password
        self.last_login = last_login
        self.bearer_token = None

class UserInformation:
    basedir = os.path.abspath(os.path.dirname(__file__))
    user_info_path = USER_INFO_PATH

    def grant_user_access(self, *data) -> None:
        email, password = data
        new = User(email, password, str(datetime.now()))
        self._save_user_record(new.__dict__)  # saving record at user_information.p

    def create_bearer_token(self, **data):
        # Create BearerToken instance.
        # Returns __dict__ of class instance
        # with JWT tokens.
        #
        # Data to encode
        access_jwt_data = data.get("devices")
        access_jwt_data['timestamp'] = str(datetime.now())
        refresh_jwt_data = dict(timestamp=str(datetime.now()))
        # Create JSON Web Tokens
        acc_token = jwt.encode(access_jwt_data, SECRET, ALGORITHM).decode("utf-8")
        ref_token = jwt.encode(refresh_jwt_data, SECRET, ALGORITHM).decode("utf-8")
        expires_in = 3600
        code = secrets.token_hex(20)
        # BearerToken dictionary
        bearer_token = dict(
            access_token=acc_token,
            refresh_token=ref_token,
            code=code,
            expires_in=expires_in,
            token_type=TOKEN_TYPE
        )
        # Update user data to include
        # set of JWT Tokens.
        self._save_bearer_token(bearer_token=bearer_token)

        logging.info("authorization code generated.")
        return code

    def _save_bearer_token(self, **data) -> None:
        file_path = self.basedir + self.user_info_path
        # Read and update record.
        _file = open(file_path, "rb")
        info = pickle.load(_file)
        info[0]["bearer_token"] = data["bearer_token"]

        # Write changes.
        _file = open(file_path, "wb")
        pickle.dump(info, _file)
        _file.close()
        logging.info("bearer token saved.")

    def get_access_token(self, code: str) -> dict:
        # Return tokens exchange for
        # POST Http Request at /token.
        with open(self.basedir + self.user_info_path, "rb") as _file:
            info = pickle.load(_file)
            # Validate code
            if not code == info[0]['bearer_token']['code']:
                return None
            # Return bearer token
            info[0]["bearer_token"].pop("code")
            self._revoke_oauth_code()
        return info[0]["bearer_token"]

    def refresh_token(self, refresh_token: str) -> dict:
        # Refresh user tokens.
        file_path = self.basedir + self.user_info_path
        _file = open(file_path, 'rb')
        info = pickle.load(_file)
        token_data = info[0]['bearer_token']

        # Validate if refresh token.
        if not refresh_token == token_data['refresh_token']:
            return None

        # Refresh Token data
        ref_token_data = dict(timestamp=str(datetime.now()))
        # Access token data
        cur_access_token = token_data['access_token']
        acc_token_data = jwt.decode(cur_access_token, SECRET, ALGORITHM)
        acc_token_data['timestamp'] = str(datetime.now())

        # Redefine tokens
        token_data['access_token'] = jwt.encode(acc_token_data, SECRET, ALGORITHM).decode('utf-8')
        token_data['refresh_token'] = jwt.encode(ref_token_data, SECRET, ALGORITHM).decode("utf-8")

        # Update file.
        _file = open(file_path, 'wb')
        pickle.dump(info, _file)
        _file.close()
        logging.info('access token refreshed')
        token_data.pop('code')
        return token_data

    def _revoke_oauth_code(self) -> None:
        # Once OAuth Code has been
        # exchanged by an access_token,
        # it will be revoked.
        #
        # Read and set to None current code
        file_path = self.basedir + self.user_info_path
        _file = open(file_path, "rb")
        info = pickle.load(_file)
        info[0]["bearer_token"]["code"] = None
        # Update values
        _file = open(file_path, "wb")
        pickle.dump(info, _file)
        _file.close()
        logging.info("OAuth code revoked after token exchange.")

    def _save_user_record(self, user_data) -> None:
        # Read file step
        file_path = self.basedir + self.user_info_path
        try:
            _file = open(file_path, "rb")
            info = pickle.load(_file)
        except (EOFError, FileNotFoundError):
            # When file is empty or doesn't exists.
            _file = open(file_path, "wb")
            pickle.dump([], _file)
            _file.close()
            return self._save_user_record(user_data)
        else:
            info = []
            info.append(user_data)
            # Write data.
            _file = open(file_path, "wb")
            pickle.dump(info, _file)
            _file.close()
            logging.info("new user information stored")
