

from .. import settings
from flask import request, url_for, render_template, redirect, jsonify
from flask.ext import login as flogin

from model import Users
from functions import get_auth_url

def login(force=True):
    next = request.args.get('next') or settings.SERVICE_URL
    scopes = ["https://spreadsheets.google.com/feeds/",
              "https://www.googleapis.com/auth/plus.me"]
              # "https://www.googleapis.com/auth/userinfo.email"]
    params = {
        'response_type':'code',
        'access_type':'offline',
        'state': next
    }

    if force:
        params.update(approval_prompt='force')

    authorization_url = get_auth_url(' '.join(scopes), **params)
    return redirect(authorization_url)


def logout():
    flogin.logout_user()
    return redirect("/")


def authorize():
    code = request.args.get('code')
    next = request.args.get('state')
    user = Users().make_from_code(code)
    flogin.login_user(user)
    return redirect(next or settings.SERVICE_URL)


@flogin.login_required
def currentuser():
    return jsonify(flogin.current_user)

