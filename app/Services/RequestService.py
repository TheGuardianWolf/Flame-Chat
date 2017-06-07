from app import Globals
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError
from httplib import HTTPException

class RequestService(object):
    def get(self, url, endpoint, payload=None, timeout=None):
        try:
            requestUrl = url + endpoint
            if (payload is not None):
                requestUrl += '?' + urlencode(payload)
            if (timeout is not None):
                response = urlopen(requestUrl, timeout=timeout)
            else:
                response = urlopen(requestUrl)
            return (200, response)
        except HTTPError, e:
            return (e.code, None)
        except URLError, e:
            return (e.errno, None)
        except HTTPException, e:
            return (e.errno, None)

    def post(self, url, endpoint, payload=None, timeout=None):
        try:
            requestUrl = url + endpoint
            if (payload is not None):
                requestUrl += '?' + urlencode(payload)
            if (timeout is not None):
                response = urlopen(requestUrl, timeout=timeout)
            else:
                response = urlopen(requestUrl)
            return (200, response)
        except HTTPError, e:
            return (e.code, None)
        except URLError, e:
            return (e.errno, None)
        except HTTPException, e:
            return (e.errno, None)
