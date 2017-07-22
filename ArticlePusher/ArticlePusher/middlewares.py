# coding: utf-8
import base64
from scrapy.utils.python import to_bytes
# write your proxy settings in private_settings
from ArticlePusher.private_settings import *


# Start your middleware class
class HttpProxyMiddleware(object):
    def __init__(self, auth_encoding='latin-1'):
        self.auth_encoding = auth_encoding

    def _basic_auth_header(self, username, password):
        user_pass = to_bytes(
            '%s:%s' % (username, password),
            encoding=self.auth_encoding)
        return base64.b64encode(user_pass).strip()

    # overwrite process request
    def process_request(self, request, spider):
        # Set the location of the proxy
        if hasattr(spider, 'proxy') and spider.proxy:
            # PROXY: 'http://PROXY_IP:PORT'
            request.meta['proxy'] = PROXY

            # setup basic authentication for the proxy
            encoded_user_pass = self._basic_auth_header(PROXY_USER, PROXY_PASS)
            request.headers['Proxy-Authorization'] = b'Basic ' + encoded_user_pass


