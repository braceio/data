import requests
import urlparse
import hashlib
import redis
import re

import flask
from flask import request, url_for, render_template, redirect, Response
from flask.ext.login import LoginManager


import werkzeug.datastructures

from paste.util.multidict import MultiDict

import settings
import log

from spreadsheets import views as ssviews
from auth import views as aviews
from auth.model import Users
from utils import crossdomain


''' 
helpers

'''

def ordered_storage(f):
    '''
    By default Flask doesn't maintain order of form arguments, pretty crazy
    From: https://gist.github.com/cbsmith/5069769
    '''

    def decorator(*args, **kwargs):
        flask.request.parameter_storage_class = werkzeug.datastructures.ImmutableOrderedMultiDict
        return f(*args, **kwargs)
    return decorator


def nl2br(value): 
    return value.replace('\n','<br>\n')


'''
views

'''

def default(template='index'):
    template = template if template.endswith('.html') else template+'.html'
    return render_template(template, is_redirect = request.args.get('redirected'))


def favicon():
    return flask.redirect(url_for('static', filename='img/favicon.ico'))

'''
Add routes and create app (create_app is called in __init__.py)

'''

def configure_routes(app):
    app.add_url_rule('/', 'index', view_func=default, methods=['GET'])
    app.add_url_rule('/favicon.ico', view_func=favicon)
    app.add_url_rule('/admin', 'viewapi', view_func=ssviews.view_api, methods=['GET'])

    app.add_url_rule('/auth/login', 'auth.login', view_func=aviews.login)
    app.add_url_rule('/auth/logout', 'auth.logout', view_func=aviews.logout)
    app.add_url_rule('/auth/authorize', 'auth.auth', view_func=aviews.authorize)
    app.add_url_rule('/auth/currentuser', view_func=aviews.currentuser)

    app.add_url_rule('/ss', view_func=ssviews.new_gspread, methods=['POST'])
    app.add_url_rule('/ss/<key>.js', view_func=ssviews.js_gspread, methods=['GET'])
    app.add_url_rule('/ss/<key>', view_func=ssviews.get_gspread, methods=['GET'])
    app.add_url_rule('/ss/<key>', view_func=ssviews.post_gspread, methods=['POST'])
    app.add_url_rule('/ss/<key>', view_func=ssviews.unlink_gspread, methods=['DELETE'])

    # app.add_url_rule('/<path:template>', 'default', view_func=default, methods=['GET'])

def create_app():
    app = flask.Flask('main')
    app.config.from_object(settings)
    configure_routes(app)

    # Configure users

    login_manager = LoginManager()

    @login_manager.user_loader
    def load_user(id):
        return Users().get(id)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Configure Error handling

    @app.errorhandler(500)
    @crossdomain(origin='*')
    def internal_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(404)
    @crossdomain(origin='*')
    def page_not_found(e):
        return render_template('error.html', title='Oops, page not found'), 404

    @app.errorhandler(403)
    @crossdomain(origin='*')
    def custom_403(error):
        return Response('Unauthorized. Please login at %s' % settings.SERVICE_URL, 403)

    # Configure jinja filters

    app.jinja_env.filters['nl2br'] = nl2br
    
    return app