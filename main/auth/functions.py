from .. import settings
from requests_oauth2 import OAuth2
from flask import request, url_for, render_template, redirect, jsonify
from ..errutils import UnexpectedError


def _get_client():
    return OAuth2(client_id=settings.GOOGLE_CLIENT_ID, 
                  client_secret=settings.GOOGLE_CLIENT_SECRET, 
                  site="https://accounts.google.com/o/", 
                  redirect_uri=settings.SERVICE_URL+url_for("auth.auth"),
                  authorization_url='oauth2/auth', 
                  token_url='oauth2/token')    


def get_auth_url(scope, **params):
    client = _get_client()
    return client.authorize_url(scope, **params)


def get_auth_token(code):
    client = _get_client()
    data = client.get_token(code)
    if not data or data.get('error'):
        raise UnexpectedError("Couldn't get token")
    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')
    expires = data.get('expires_in', 0)
    return access_token, expires, refresh_token


def refresh_auth_token(user):
    code = user.get('refresh_token')
    client = _get_client()
    data =  client.refresh_token(code)
    if not data or data.get('error'):
        raise UnexpectedError("Couldn't refresh token")
    access_token = data.get('access_token')
    expires = data.get('expires_in', 0)
    return access_token, expires


