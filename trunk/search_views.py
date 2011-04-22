#-*- coding: utf-8 -*-

from bottle import route, redirect, view
from bottle import get, post, request, response
import urllib2
import zlib
import re
import json
import os

def decompress_gzip_string(data):
	dobj = zlib.decompressobj(16+zlib.MAX_WBITS)
	result = dobj.decompress(data)
	return result

def get_search_results_json(url):
	headers = {	
		'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
		'Accept-Charset': 'UTF-8,*;q=0.5',
		'Accept-Encoding': 'gzip,deflate,sdch',
		'Accept-Language': 'en-US,zh-CN;q=0.8',
		'Cache-Control': 'max-age=0',
		'Connection': 'keep-alive',
		'Host': 'www.googleapis.com',
		'If-None-Match': '"yX6LsxiRj85AIkg4qEEDh9-nhIQ/V2YEacA56PERlCErAWJ8BAJ5yc8"',
		'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.204 Safari/534.16',
		'Referer': 'https://twip.bluemask.net'
	}
	req = urllib2.Request(url, None, headers)
	g_response = urllib2.urlopen(req)
	if g_response:
		if g_response.code == 200:
			data = g_response.read()
			if g_response.headers.get('content-encoding').lower() == 'gzip':
				return decompress_gzip_string(data)
			else:
				return data
		elif g_response.code == 301:
			location = g_response.geturl()
			if location.lower().strip()!=url.lower().strip():
				# print u'redirecting: %s' % location
				return get_search_results(location)
			else:
				return '{"error": "Abort(server try to redirect to the original url)."}'
		else:
			return '{"error": "HTTP %s"}' % g_response.code
	return '{}'

@get('/search')
@get('/search/')
@post('/search')
@post('/search/')
@view('search_results')
def do_search():
	q = request.GET.get('q') or request.GET.get('k') or ''
	if not q:
		return {'title':'Google search API', 'q':'', 'items':None}
	api_key = 'AIzaSyBMGzwiXCKNBmvxmZzh1uYheLzhUDCc02c'
	search_id = '017576662512468239146:omuauf_lfve'
	skip_cached_file = True
	if os.access('d:/response.dat', os.F_OK) and not skip_cached_file:
		f = open('d:/response.dat', 'r')
		json_results = f.read()
		f.close()
		print 'read response from local file.'
	else:
		url = 'https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&callback=results' % (api_key, search_id, urllib2.quote(q))
		json_results = get_search_results_json(url)
		if skip_cached_file:
			f = open('d:/response.dat', 'wb+')
			f.write(json_results)
			f.close()
	pt = re.compile(r'^results\s*\((?P<content>.+)\)', re.I|re.S)
	m = pt.search(json_results)
	json_results = m.group('content') if m else '{"error": "json_error"}'
	obj_results = json.loads(json_results)
	results = obj_results.get('items') or []
	return {
		'title': 'Search results',
		'q': q, 
		'items': results
	}

	
	
	