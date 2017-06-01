import Globals
from urllib import urlencode
from urllib2 import urlopen

class RestfulService(object):
    def __request(self, url, endpoint, payload):
        pass

    def get(self, url, endpoint, payload):
        response = urlopen(url + endpoint + '?' + urlencode(payload))

        return response
