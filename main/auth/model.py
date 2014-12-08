import requests
import datetime
from quickdata import Model, Collection, MongoBackend

from flask.ext.login import UserMixin

from .. import settings
from ..errutils import UnexpectedError
from functions import get_auth_token, refresh_auth_token


class User(Model, UserMixin):
    fields = ['access_token', 'refresh_token', 'expires', 'email', 'name']

    def refresh_auth_token(self):
        access_token, expiresin = refresh_auth_token(self)
        expires = datetime.datetime.now() + datetime.timedelta(seconds=expiresin)
        self.update(access_token=access_token, expires=expires, id=self.id)
        self.save()


class Users(Collection):
    modelClass=User

    def make_from_code(self, code):
        access_token, expiresin, refresh_token = get_auth_token(code)
        expires = datetime.datetime.now() + datetime.timedelta(seconds=expiresin)
        return self.make_from_token(access_token, 
            expires=expires,
            refresh_token=refresh_token)


    def make_from_token(self, access_token, **kwargs):
        r = requests.get("https://www.googleapis.com/plus/v1/people/me",
                               params={'access_token': access_token})
        
        if r.status_code != requests.codes.ok:
            print r.__dict__
            raise UnexpectedError("couldn't get user details")

        profile = r.json()
        userid = profile.get('id')
        user = self.get(userid)
        if not user:
            user = self.create(id=userid)

        user.update(access_token=access_token, **kwargs)

        if profile.get('emails'):
            for email in profile.get('emails', []):
                if email.get('type') == 'account':
                    user['email'] = email.get('value')

        try:
            user['name'] = profile['displayName']
        except KeyError:
            pass

        user.save()

        return user



Users().setBackend(MongoBackend, host=settings.MONGO_HOST,
                                 user=settings.MONGO_USER,
                                 passwd=settings.MONGO_PASS,
                                 dbName=settings.MONGO_DB)

