#!/usr/bin/python
# -*- coding: utf8 -*-

from httplib import HTTPConnection
import urlparse
import sys
import traceback
import re

class WebResponse(object):
	
	def __init__(self, status, response_text, headers):
		self.status = status
		self.text = response_text
		self.headers = {}
		if headers is not None:
			for item in headers:
				if len(item)>=2:
					self.headers[item[0]] = item[1]
	
	def as_dict(self):
		data = {}
		if self.text is not None:
			items = [part.split('=') for part in self.text.split('&') if len(part)>0]
			for item in items:
				if len(item)>0:
					k=item[0]
					if len(item)>1:
						data[k] = item[1]
					else:
						data[k] = ''
		return data

	@property
	def content_type(self):
		for k in self.headers:
			if k.lower()=='content-type':
				return self.headers[k]
		return ''

	@property
	def content_encoding(self):
		for k in self.headers:
			if k.lower()=='content-encoding':
				return self.headers[k]
		return ''

class WebRequest(object):
	
	def get_port_from_url(self, url):
		m = re.search(r'^http(s)?\:\/\/[^\/\:]+(\:\d+)?', url)
		if m is not None:
			port_str = m.group(2)
			if port_str is not None:
				return int(port_str)
			is_https = m.group(1) is not None
			if is_https:
				return 443
		return 80

	def __init__(self, method='GET', url='', postdata=None, headers={}):
		self.method = method
		self.url = url
		urlobj = urlparse.urlparse(self.url)
		self.port = urlobj.port
		#if self.port is None:
		#	self.port = self.get_port_from_url(url)
		self.scheme = urlobj.scheme
		self.host = urlobj.netloc
		self.data = postdata or ''
		self.referer = ''
		self.headers = headers or {}
	
	def send(self):
		conn = HTTPConnection(self.host, self.port)
		headers = {
			'accept': '''application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5''',
			# 'cache-control': '''max-age=0''',
			'referer': '''%s''' % self.referer,
			'user-agent': '''Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Ubuntu/10.04 Chromium/6.0.472.53 Chrome/6.0.472.53 Safari/534.3'''
		}
		if not self.headers.has_key('accept'):
			self.headers['accept'] = '*'
		if not self.headers.has_key('use-agent'):
			self.headers['user-agent'] = headers['user-agent']
		#headers.update(self.headers)
		conn.request(self.method, self.url, self.data, self.headers)
		response = conn.getresponse()
		return WebResponse(response.status, response.read(), response.getheaders())

	def __str__(self):
		try:
			desc = []
			desc.append('<WebRequest')
			desc.append('method: %s' % self.method)
			desc.append('host: %s' % self.host)
			desc.append('port: %s' % self.port)
			desc.append('url: %s' % self.url)
			desc.append('headers: %s' % self.headers)
			desc.append('form-data: %s' % self.data)
			desc.append('>')
			return '\n'.join(desc)
		except:
			return '[Exception]'


if __name__ == '__main__':
	#req = WebRequest(url='http://twitter.com/oauth/request_token?oauth_nonce=tGxIeY5J0CdlkBK8&oauth_timestamp=1286007800&oauth_consumer_key=Gmb6FtQwSRDNfIIskdxl5Q&oauth_signature_method=HMAC-SHA1&oauth_version=1.0&oauth_signature=FVnBKgREHyh1CRIwBDpbsUfzSxc%3D')
	#response = req.send()
	#print response.status, response.text
	#print response.as_dict()
	try:
		x = 1/0
	except:
		#exc = sys.exc_info()
		print traceback.format_exc()









