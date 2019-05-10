
import os
import uuid
import time
import json
import urllib.request

from requests.adapters import HTTPAdapter
from httpie.plugins.base import TransportPlugin

__version__ = '0.0.1'
__author__ = 'Jove Yu'
__license__ = 'MIT'

class ZipkinHTTPAdapter(HTTPAdapter):

    def get_zipkin_server(self):
        return os.environ.get('ZIPKIN_SERVER')

    def gen_spanid(self):
        return uuid.uuid4().hex[:16]

    def gen_traceid(self):
        return uuid.uuid4().hex

    def add_headers(self, request, **kwargs):
        super(ZipkinHTTPAdapter, self).add_headers(request, **kwargs)

        if self.get_zipkin_server():
            request.headers['X-B3-TraceId'] = self.gen_traceid()
            request.headers['X-B3-SpanId'] = self.gen_spanid()
            request.headers['X-B3-Sampled'] = 1
            request._start = time.time()

    def build_response(self, req, resp):
        response = super(ZipkinHTTPAdapter, self).build_response(req, resp)

        server = self.get_zipkin_server()
        if server:

            span = {
                'traceId': req.headers.get('X-B3-TraceId',''),
                'name': req.path_url,
                'id': req.headers.get('X-B3-SpanId',''),
                'kind': 'CLIENT',
                'timestamp': int(req._start * 1000000),
                'duration': int((time.time() - req._start) * 1000000),
                'localEndpoint': {
                    'serviceName':'HTTPie',
                },
            }
            self.post_json(server, [span])

        return response

    def post_json(self, url, data):
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
            urllib.request.urlopen(req)
        except Exception as e:
            print(e)


class ZipkinPlugin(TransportPlugin):

    prefix = 'http://'
    name = 'HTTPie Zipkin Plugin'
    description = 'trace http request from HTTPie'

    def get_adapter(self):
        return ZipkinHTTPAdapter()
