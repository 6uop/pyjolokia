try:
    import json
except:
    import simplejson as json

import urllib2

class Jolokia:
    '''
        pyJolokia class Jolokia is a JSON featching python class.
        It uses urllib2 and json or simplejson to do post requests
        to a jolokia URL. Then returns back a python dictionary.

        .. code-block:: python

            j4p = Jolokia('http://localhost:9199/jolokia/')
            j4p.request(type = 'read', mbean = 'java.lang:type=Threading',
                        attribute = 'ThreadCount' )
            >> { 'status' : 200, ...
    '''
    def __init__(self, url):
        self.url = url
        self.data = None
        self.proxyConfig = {}
    def proxy(self, url, **kwargs):
        '''
            Used to add proxy info if using jolokia as a proxy to other
            java jmx apps.

            example

            .. code-block:: python

                j4p.proxy('service:jmx:rmi://somehost:1234/some.mbean.server',
                           user = 'cwood',
                           password = 'somePassword')

        '''
        self.proxyConfig['target'] = {}
        self.proxyConfig['target']['url'] = url
        self.proxyConfig['target']['user'] = kwargs.get('user')
        self.proxyConfig['target']['password'] = kwargs.get('password')
    def __getJson(self):
        if isinstance(self.data, dict):
            mainRequest = dict(self.data.items() + self.proxyConfig.items())
        else:
            mainRequest = []
            for request in self.data:
                request = dict(request.items() + self.proxyConfig.items())
                mainRequest.append(request)
        jdata = json.dumps(mainRequest)
        request = urllib2.Request(self.url, 
                                  jdata, 
                                  {'content-type' : 'application/json'})
        responseStream = urllib2.urlopen(request)
        jsonData = responseStream.read()

        pythonDict = json.loads(jsonData)
        return pythonDict
    def __mkrequest(self, type, **kwargs):
        newRequest = {}
        newRequest['type'] = type

        if type != 'list':
            newRequest['mbean'] = kwargs.get('mbean')
        else:
            newRequest['path'] = kwargs.get('path')

        if type == 'read':
           newRequest['attribute'] = kwargs.get('attribute')
           newRequest['path'] = kwargs.get('path')
        elif type == 'write':
            newRequest['attribute'] = kwargs.get('attribute', '')
            newRequest['value'] = kwargs.get('value', '')
            newRequest['path'] = kwargs.get('path', '')
        elif type == 'exec':
            newRequest['operation'] = kwargs.get('operation')
            newRequest['arguments'] = kwargs.get('arguments')
        return newRequest
    def request(self, type, **kwargs):
        if not isinstance(self.data, dict):
            self.data = {}
        self.data = self.__mkrequest(type, **kwargs)
        response = self.__getJson()
        return response
    def add_request(self, type, **kwargs):
        new_response = self.__mkrequest(type, **kwargs)
        if not isinstance(self.data, list):
            self.data = list()
        self.data.append(new_response)
    def getRequests(self):
        response = self.__getJson()
        return response
