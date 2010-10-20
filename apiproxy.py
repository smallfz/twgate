#!/usr/bin/python
# -*- coding: utf8 -*-

from bottle import route, get, post, request, response
from bottle import view, redirect, abort
from time import time as now
import re
from urllib import urlencode
from http import WebRequest, WebResponse


@get("/proxy")
def api_proxy_home():
	response.headers["content-type"] = "text/plain; charset=utf-8"
	# write a log
	log = open('proxy.log', 'ab+')
	log.write('try to access "/proxy/"...')
	log.write('\n\n\n')
	log.close()
	#
	return """Welcome to TwGate proxy.

	This is a public accessable SSL twitter api proxy,
	it's not supposed to be accessed directly from your browser.
	You may want to use a client like 'seesmic'.""".replace("\t","")

@get("/proxytest")
def api_proxy_test_form():
	return """
	<html>
	<head><title>api test</title></head>
	<body>
		<form method='post' action='/proxy/?test'>
		<input type='text' name='arg1' value='1' /><br />
		<input type='text' name='arg2' value='2' /><br />
		<input type='submit' />
		</form>
	</body>
	</html>
	"""

def do_http_proxy(base_url, host):
	original_url = request.url
	m = re.search(r'^http[s]?\:\/\/[^\/\?]+\/[a-zA-Z]+\/(.+)$', original_url, re.IGNORECASE)
	if m is None:
		return api_proxy_home()
	url = "%s%s" % (base_url, m.group(1))
	x_req = WebRequest(method=request.method, url=url)
	x_headers = {}
	copying_headers = ['authorization', 'www-authorization', 'oauth', 'x-auth',
					   'xauth', 'user-agent', 'host', 'content-type']
	for k in request.headers:
		for h in copying_headers:
			if k.lower().startswith(h):
				x_headers[k.lower()] = request.headers[k]
	x_headers['host'] = host #'api.twitter.com'
	if len(request.POST)>0:
		x_headers['content-type'] = 'application/x-www-form-urlencoded'
		x_post = {}
		x_post.update(request.POST)
		x_req.data = urlencode(x_post)
	x_req.headers = x_headers
	x_response = x_req.send()
	# write a log
	log = open('proxy.log', 'ab+')
	log.write('%s\n' % x_req)
	log.write('--------\nresponse: %s\n' % x_response.status)
	log.write('content-type: %s\n' % x_response.content_type)
	log.write(x_response.text)
	log.write('\n\n\n')
	log.close()
	# transfer response
	response.status = x_response.status
	response.content_type = x_response.content_type
	return x_response.text



@get("/proxy/:args#.*#")
@post("/proxy/:args#.*#")
def api_proxy(args):
	return do_http_proxy("https://api.twitter.com/1/", 'api.twitter.com')

@get("/xauthproxy/:args#.*#")
@post("/xauthproxy/:args#.*#")
def xauth_api_proxy(args):
	return do_http_proxy("https://api.twitter.com/", 'api.twitter.com')

@get("/oauthproxy/:args#.*#")
@post("/oauthproxy/:args#.*#")
def oauth_api_proxy(args):
	return do_http_proxy("https://twitter.com/oauth/", 'twitter.com')






