from gspread.httpsession import HTTPSession, urlencode
from gspread.urls import SPREADSHEETS_FEED_URL
from quickkvs import KeyValueStore, RedisBackend
from copy import copy
from cStringIO import StringIO
import settings

class CachedHTTPSession(HTTPSession):

    cache = KeyValueStore(backend=RedisBackend, host=settings.REDIS_HOST,
                                                port=int(settings.REDIS_PORT),
                                                pw=settings.REDIS_PASS)
    ttl = 300

    def _serialize_headers(self, **kwargs):
        headers = copy(self.headers)
        headers.update(kwargs.get('headers', {}))
        return urlencode(headers)


    def get(self, url, **kwargs):
        if not kwargs.pop('cached', True):
            return self.request('GET', url, **kwargs)

        # never cache requests for cells
        if url.startswith(SPREADSHEETS_FEED_URL+"cells"):
            return self.request('GET', url, **kwargs)

        key = "CACHEKEY::"+url+"::"+self._serialize_headers(**kwargs)
        try:
            result = self.cache[key]
        except KeyError:
            result = self.request('GET', url, **kwargs).read()
            self.cache.set(key, result, expires=self.ttl)
        if type(result) == unicode:
            result = unicode(result).encode("utf-8")
        return StringIO(result)

