import Globals
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError
from httplib import HTTPException

class RestfulService(object):
    def get(self, url, endpoint, payload):
        try:
            response = urlopen(url + endpoint + '?' + urlencode(payload))
            return (200, response)
        except HTTPError, e:
            return (e.code, None)
        except URLError, e:
            return (e.errno, None)
        except HTTPException, e:
            return (e.errno, None)