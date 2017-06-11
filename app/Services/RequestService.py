from app import Globals
from socket import setdefaulttimeout, timeout as TimeoutError
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError, Request
from httplib import HTTPException
from json import dumps

class RequestService(object):
    """
    Request sender, sends requests to clients and handles exceptions sanely.
    """
    def __init__(self):
        setdefaulttimeout(10)

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
        except HTTPError as e:
            return (e.code, None)
        except URLError as e:
            return (e.reason.errno, None)
        except TimeoutError as e:
            return (504, None)
        except HTTPException as e:
            return (e.reason.errno, None)

    def post(self, url, endpoint, payload, timeout=None, json=True):
        try:
            requestUrl = url + endpoint
            if json:
                headers = {
                    'Content-Type': 'application/json'    
                }
                request = Request(requestUrl, dumps(payload), headers=headers) 
            else:
                requestUrl += '?' + urlencode(payload)
                request = Request(requestUrl)
            if (timeout is not None):
                response = urlopen(request, timeout=timeout)
            else:
                response = urlopen(request)
            return (200, response)
        except HTTPError, e:
            return (e.code, None)
        except URLError, e:
            return (e.reason.errno, None)
        except TimeoutError as e:
            return (504, None)
        except HTTPException, e:
            return (e.reason.errno, None)
