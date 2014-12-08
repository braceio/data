
from flask import request, url_for, render_template, redirect, jsonify, abort
from flask.ext.login import current_user, login_required

import gspread
import shortuuid

from ..errutils import GenericError, UnexpectedError
from .. import log
from ..utils import crossdomain, get_url
from ..auth.model import Users
from ..cachedsession import CachedHTTPSession
from model import GSCredentials


def _get_gspread_client(user, refresh=False):
    if refresh:
        user.refresh_auth_token()
    token = user.get('access_token')
    auth = GSCredentials(access_token=token)
    session = CachedHTTPSession()
    client = gspread.Client(auth=auth, http_session=session)
    client.login()
    return client


def _ss_for_user(user, url, refresh=False, cached=True):
    gc = _get_gspread_client(user, refresh=refresh)
    try:
        ss = gc.open_by_url(url, cached=not refresh and cached)
    except gspread.NoValidUrlKeyFound:
        return None
    except gspread.SpreadsheetNotFound:
        try:
            ss = gc.open_by_url(url, cached=False)
        except gspread.SpreadsheetNotFound:
            abort(404)
    except gspread.httpsession.HTTPError:
        # try refreshing token and going again
        gc = _get_gspread_client(user, refresh=True)
        try:
            # optimise this
            ss = gc.open_by_url(url, cached=False)
        except gspread.httpsession.HTTPError as e:
            abort(e.code)
        except gspread.SpreadsheetNotFound:
            abort(404)
    return ss


def _do_with_ss(user, url, fn, cached=True):
    ss = _ss_for_user(user, url, cached=cached) 
    try:
        ws = ss.get_worksheet(0, cached=cached)
        return fn(ws)
    except gspread.httpsession.HTTPError:
        ss = _ss_for_user(user, url, refresh=True, cached=cached)
        ws = ss.get_worksheet(0)
        return fn(ws)


def _link_sheet(url):
    ss = _ss_for_user(current_user, url)
    if ss:
        spreadsheets = current_user.get('spreadsheets', [])
        try:
            sheetobj = next(i for i in spreadsheets if i.get('id') == ss.id)
        except StopIteration:
            # create new sheet obj
            sheetobj = {
                'url': url,
                'key': shortuuid.uuid(),
                'writekey': shortuuid.uuid(),
                'id': ss.id,
            }
            spreadsheets.append(sheetobj)
            current_user['spreadsheets'] = spreadsheets

        sheetobj['title'] = ss.title
        current_user.save()

        return sheetobj
    else:
        return None


@login_required
def new_gspread():
    url = request.form['url']
    result = _link_sheet(url)
    if result:
        return jsonify(result)
    else:
        abort(400)


def _user_for_key(key=None, writekey=None):
    if not key and not writekey:
        return None
    if key:
        query = 'spreadsheets.key'
        value = key
    else:
        query = 'spreadsheets.writekey'
        value = writekey

    users = Users().find({query: value})
    try:
        user = next(users)
    except StopIteration:
        return None
    return user


@crossdomain(origin='*')
def unlink_gspread(key):
    user = _user_for_key(key)
    if not user:
        abort(404)
    sheetobj = next(i for i in user['spreadsheets'] if i['key'] == key)
    sheets = current_user.get('spreadsheets') or []
    sheets.remove(sheetobj)
    current_user['spreadsheets'] = sheets
    current_user.save()
    return jsonify({'count': len(sheets)})


@crossdomain(origin='*')
def get_gspread(key):
    user = _user_for_key(key)
    if not user:
        abort(404)
    sheetobj = next(i for i in user['spreadsheets'] if i['key'] == key)

    def mk_result(ws):
        return {'rows': ws.get_all_records(), 'headers': ws.row_values(1)}

    # import pdb; pdb.set_trace()
    return jsonify(_do_with_ss(user, sheetobj['url'], mk_result))


def _compress_rows(ws):
    allvalues = ws.get_all_values()
    rowcount = initial = len(allvalues)
    for r in range(initial-1, -1, -1):
        if ''.join(allvalues[r]) != '':
            break
        rowcount -= 1
    if rowcount < initial or rowcount < ws.row_count:
        ws.resize(rows=rowcount)


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


@crossdomain(origin='*')
def post_gspread(key):
    user = _user_for_key(writekey=key)
    if not user:
        abort(404)
    sheetobj = next(i for i in user['spreadsheets'] if i['writekey'] == key)

    def mk_result(ws):
        headers = ws.row_values(1)
        values = ['']*len(headers)
        for field in request.form:
            if not field in headers:
                raise GenericError("Invalid column name: '%s'" % field, 400)
            values[headers.index(field)] = request.form[field]
        _compress_rows(ws)
        ws.append_row(values)
        return {'rows': values, 'headers': headers}
           
    try:
        result = _do_with_ss(user, sheetobj['url'], mk_result, cached=False)
        if request_wants_json():
            return jsonify(result)
        else:
            return render_template('thanks.html', next=request.referrer or None)
    except GenericError as e:
        if request_wants_json():
            return jsonify({'error': e.msg}), e.code
        else:
            return render_template('error.html', 
                                   title="Invalid form submission",
                                   text=e.msg)


@login_required
def view_api():
    url = request.args.get('url')
    if url:
        result = _link_sheet(url)
        if not result:
            return render_template('viewapi.html', title="Invalid spreadsheet URL"), 400
        key = result.get('key')
        return redirect(get_url('viewapi', secure=True, key=key))
    else:
        spreadsheets = current_user.get('spreadsheets', [])
        key = request.args.get('key')
        user = _user_for_key(key)
        if user == current_user:
            sheetobj = next(i for i in spreadsheets if i['key'] == key)
            writekey = sheetobj['writekey']
            title = "Your \"%s\" spreadsheet is ready" % sheetobj['title']
        else:
            key=None
            writekey=None
            title="Your Spreadsheets"
        return render_template('viewapi.html', key=key, writekey=writekey, title=title, spreadsheets=spreadsheets)

def js_gspread(key):
    return render_template('loader-ck.js', key=key)

