# -*- coding: utf8 -*-

from bottle import route, get, post, request, response
from bottle import view, redirect, abort
from widgets import *
from users import UserDb, CookieUser
from auth import *
import oauth
from time import time as now
import random
from http import WebRequest, WebResponse
import urllib
import re
import traceback
import json
from localcach import TwLocalCache
from dateformat import str_to_local_date
import datetime

sign_method_name = 'HMAC_SHA1'
oauth.SIGNATURE_METHOD = sign_method_name

default_clientinfo = {
	'Consumer_key': 		'Gmb6FtQwSRDNfIIskdxl5Q',
	'Consumer_secret': 		'jgA5556BBFaCtkDxbw8dT5VXHN6azWHvwaHaNXoKBo',
	'Request_token_URL': 	'http://twitter.com/oauth/request_token',
	'Access_token_URL': 	'http://twitter.com/oauth/access_token',
	'Authorize_URL': 		'http://twitter.com/oauth/authorize'
}

def randomstring(length):
	s = 'abcdefghijklmnopqrstuvwxyz01234567890' #ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	len_s = len(s)
	result = []
	for i in range(0, length):
		result.append(s[random.randint(0, len_s-1)])
	return ''.join(result)

def is_valid_token(token):
	if token is None:
		return False
	elif not token.key or not token.secret:
		return False
	return True


def make_link(m):
	url = m.group()
	return '<a href="%s" target="_blank">%s</a>' % (url, url)

def replace_qu(m):
	uname = m.group(1)
	return '<a href="/timeline/username/%s">%s</a>' % (uname, '@%s' % uname)

def localize_post(post):
	post['created_at'] = str_to_local_date(post['created_at'])
	t = post['text']
	t = re.sub(r'@([a-zA-Z0-9_]+)', replace_qu, t)
	t = re.sub(r'http[s]?\:\/\/[a-zA-Z0-9%_\-\&\?\=]+([\.\/][a-zA-Z0-9%_\-&\?\=]+)*\/?', make_link, t)
	post['text'] = t

def write_log(req, resp):
	return
	# write a log
	log = open('proxy.log', 'ab+')
	log.write('%s\n' % req)
	log.write('--------\nresponse: %s\n' % resp.status)
	log.write('content-type: %s\n' % resp.content_type)
	log.write(resp.text)
	log.write('\n\n\n')
	log.close()

class TwClient(object):
	
	def __init__(self, clientinfo=None):
		self.log = False
		self.need_oauth_sign = True
		self._clientinfo = clientinfo
	
	@property
	def clientinfo(self):
		if self._clientinfo is not None:
			if not self._clientinfo.has_key('Consumer_key') or not self._clientinfo.has_key('Consumer_secret'):
				return default_clientinfo
			else:
				return self._clientinfo
		return default_clientinfo

	@clientinfo.setter
	def clientinfo(self, value):
		self._clientinfo = value

	def post(self, acc_token, url, parameters={}, headers={}):
		if self.need_oauth_sign:
			if not is_valid_token(acc_token):
				return None
			sign_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
			params = {
				'oauth_consumer_key': self.clientinfo['Consumer_key'],
				'oauth_timestamp': '%s' % int(now()),
				'oauth_nonce': randomstring(8),
				'oauth_version': '1.0',
				'oauth_signature_method': sign_method_name,
				'oauth_token': acc_token.key
			}
			params.update(parameters)
			req = oauth.OAuthRequest(http_method='POST', http_url = url, parameters=params)
			req.sign_request(sign_method, 
				oauth.OAuthConsumer(self.clientinfo['Consumer_key'], self.clientinfo['Consumer_secret']), 
				acc_token)
			postdata = req.to_postdata()
		else:
			postdata = urllib.urlencode(parameters)
		wr = WebRequest(method='POST', url=url, postdata=postdata)
		wr.headers.update(headers)
		wr.headers['content-type'] = 'application/x-www-form-urlencoded'
		wresponse = wr.send()
		# log
		if self.log:
			write_log(wr, wresponse)
		return wresponse

	def send_request(self, acc_token, url, parameters={}, headers={}):
		if self.need_oauth_sign:
			if not is_valid_token(acc_token):
				return None
			sign_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
			params = {
				'oauth_consumer_key': self.clientinfo['Consumer_key'],
				'oauth_timestamp': '%s' % int(now()),
				'oauth_nonce': randomstring(8),
				'oauth_version': '1.0',
				'oauth_signature_method': sign_method_name,
				'oauth_token': acc_token.key
			}
			params.update(parameters)
			req = oauth.OAuthRequest(http_method='GET', http_url = url,	parameters=params)
			req.sign_request(sign_method, 
				oauth.OAuthConsumer(self.clientinfo['Consumer_key'], self.clientinfo['Consumer_secret']), 
				acc_token)
			# postdata = req.to_postdata()
			finalurl = req.to_url()
			# raise Exception(postdata)
		else:
			finalurl = url
		wr = WebRequest(method='GET', url=finalurl)#, postdata=postdata)
		wr.headers.update(headers)
		#wr.headers['content-type'] = 'application/x-www-form-urlencoded'
		wresponse = wr.send()
		# log
		if self.log:
			write_log(wr, wresponse)
		return wresponse

	def sign_url(self, acc_token, url, parameters={}):
		'''为url签名，返回已签名的url'''
		if not is_valid_token(acc_token):
			return None
		sign_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
		params = {
			'oauth_consumer_key': self.clientinfo['Consumer_key'],
			'oauth_timestamp': '%s' % int(now()),
			'oauth_nonce': randomstring(8),
			'oauth_version': '1.0',
			'oauth_signature_method': sign_method_name,
		}
		params.update(parameters)
		req = oauth.OAuthRequest(http_method='GET', http_url = url,	parameters=params)
		req.sign_request(sign_method, 
			oauth.OAuthConsumer(self.clientinfo['Consumer_key'], self.clientinfo['Consumer_secret']), 
			acc_token)
		return req.to_url()

	def get_url_of_req_token(self):
		sign_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
		req = oauth.OAuthRequest(http_method='GET', 
		http_url = default_clientinfo['Request_token_URL'],
		parameters={
			'oauth_consumer_key': self.clientinfo['Consumer_key'],
			'oauth_timestamp': '%s' % int(now()),
			'oauth_nonce': randomstring(8),
			'oauth_version': '1.0',
			'oauth_signature_method': sign_method_name
		})
		req.sign_request(sign_method, 
			oauth.OAuthConsumer(self.clientinfo['Consumer_key'], self.clientinfo['Consumer_secret']), 
			oauth.OAuthToken('', ''))
		return req.to_url()
	
	def obtain_req_token(self):		
		webrequest = WebRequest(url=self.get_url_of_req_token())
		webresponse = webrequest.send()
		token_data = webresponse.as_dict()
		if token_data.has_key('oauth_token') and token_data.has_key('oauth_token_secret'):
			return oauth.OAuthToken(token_data['oauth_token'], token_data['oauth_token_secret'])
		return None

	def get_authorizing_url(self, token, callback_url):
		url = []
		url.append(default_clientinfo['Authorize_URL'])
		url.append('?')
		url.append(urllib.urlencode({
			'oauth_token': token.key,
			'oauth_callback': callback_url
		}))
		return ''.join(url)
	
	def obtain_access_token(self, req_token):
		sign_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
		req = oauth.OAuthRequest(http_method='GET', 
		http_url = default_clientinfo['Access_token_URL'],
		parameters={
			'oauth_consumer_key': self.clientinfo['Consumer_key'],
			'oauth_timestamp': '%s' % int(now()),
			'oauth_nonce': randomstring(8),
			'oauth_version': '1.0',
			'oauth_signature_method': sign_method_name,
			'oauth_token': req_token.key
		})
		req.sign_request(sign_method, 
			oauth.OAuthConsumer(self.clientinfo['Consumer_key'], self.clientinfo['Consumer_secret']), 
			req_token)
		acctoken_obtain_url = req.to_url()
		# get acc-token
		webrequest = WebRequest(url=acctoken_obtain_url)
		webresponse = webrequest.send()
		token_data = webresponse.as_dict()
		if token_data.has_key('oauth_token') and token_data.has_key('oauth_token_secret'):
			return oauth.OAuthToken(token_data['oauth_token'], token_data['oauth_token_secret'])
		return None

@get("/sessions/revoke")
@auth_required()
def revoke_tokens():
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		service = UserDb()
		service.clear_tokens(cu.uid)
		redirect('/welcome')
	return ''

@get("/sessions/callback")
@view("oauth_ok")
def oauth_twitter_callback():
	form = Form(msg='Not implemented.')
	token_key = request.params.get('oauth_token') or ''
	if token_key:
		service = UserDb()
		user = service.get_user_by_req_token(token_key)
		if user is not None:
			# get access token
			clientinfo = service.get_user_clientinfo(user['id'])
			req_token = oauth.OAuthToken(user['tw_reqtoken'], user['tw_reqtokensecret'])
			client = TwClient(clientinfo=clientinfo)
			acc_token = client.obtain_access_token(req_token)
			if acc_token is not None:
				service.save_acc_token(user['id'], acc_token.key, acc_token.secret)
				service.generate_new_sessionkey(user['id'], randomstring(7).lower())
				form.msg = '授权完成，请返回。' #<br />%s, %s' % (acc_token.key, acc_token.secret)
				form.success = True
			else:
				form.msg = 'Failed to obtain access token.'
		else:
			form.msg = 'No such user.'
	else:
		form.msg = 'Please get a req-token first.'
	return dict(form_result=form)


@get("/sessions/req")
@auth_required()
def get_req_token():
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		clientinfo = service.get_user_clientinfo(user['id'])
		client = TwClient(clientinfo=clientinfo)
		# raise Exception('client.clientinfo: %s' % client.clientinfo)
		req_token = client.obtain_req_token()
		if req_token is not None:
			service.save_req_token(cu.uid, req_token.key, req_token.secret)
			forward_url = client.get_authorizing_url(req_token, 'https://twip.bluemask.net/sessions/')
			# return 'forward_url: \n%s' % forward_url
			redirect(forward_url)
			return forward_url
		else:
			return 'Failed to obtain request token.'
	else:
		return 'Access denied.'


@get("/oauth/:oauth_req#.*#")
@post("/oauth/:oauth_req#.*#")
def forward_oauth_req(oauth_req):
	try:
		method = 'GET' # if len(request.forms)<=0 else 'POST'
		url = 'http://twitter.com/oauth/%s' % oauth_req
		pars = {}
		if len(request.GET)>0:
			pars.update(request.GET)
		if len(request.forms)>0:
			pars.update(request.forms)
		url = '%s?%s' % (url, urllib.urlencode(pars))
		webrequest = WebRequest(method = method, url = url)
		webresponse = webrequest.send()
		response.status = webresponse.status
		if webresponse.status == 200:
			return webresponse.text
		else:
			return '%s\nstatus=%s, headers=%s, content=%s' % (url, webresponse.status, webresponse.headers, webresponse.text)
	except:
		response.status = 500
		return traceback.format_exc()
		# return 'failed to forward oauth request: %s' % oauth_req


def user_api(clientinfo, acc_token, base_url, need_auth):
	m = re.search(r'^http[s]?\:\/\/[^\/]+\/(searchapi|api)\/([a-z0-9A-Z]+)\/(.*)$', request.url, re.IGNORECASE)
	if m is None:
		return 'This is a twitter API proxy.'
	user_session_key = m.group(2)
	api_payload = m.group(3)
	url = '%s%s' % (base_url, api_payload)
	is_post = request.method.lower()=='post'
	parameters = {}
	if is_post:
		parameters.update(request.POST)
	else:
		parameters.update(request.GET)
	client = TwClient(clientinfo=clientinfo)
	client.log = True
	client.need_oauth_sign = need_auth
	t_response = None
	headers = {}
	headers['accept-encoding'] = 'gzip'
	if is_post:
		t_response = client.post(acc_token, url, parameters=parameters, headers=headers)
	else:
		t_response = client.send_request(acc_token, url, parameters=parameters, headers=headers)
	response.status = t_response.status
	response.content_type = t_response.content_type
	response.headers['content-encoding'] = t_response.content_encoding
	return t_response.text

@get("/api/:apipath#.+#")
@post("/api/:apipath#.+#")
def process_user_api(apipath):
	service = UserDb()
	req_text = ''
	sessionkey = ''
	if apipath is None:
		apipath = ''
	m = re.search(r'([a-zA-Z0-9]+)(/.*?)?$', apipath)
	if m is not None:
		sessionkey = m.group(1)
		req_text = m.group(2)
		if req_text.startswith('/'):
			req_text = req_text[1:]
	if sessionkey:
		user = service.get_user_by_sessionkey(sessionkey)
		if user is not None:
			clientinfo = service.get_user_clientinfo(user['id'])
			acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
			try:
				# return user_api_proxy(user)
				return user_api(clientinfo, acc_token, 'http://api.twitter.com/1/', True)
			except:
				response.status = 500
				return traceback.format_exc()
	return 'No such user(sk=%s)' % sessionkey


@get("/searchapi/:apipath#.+#")
@post("/searchapi/:apipath#.+#")
def process_search_api(apipath):
	service = UserDb()
	req_text = ''
	sessionkey = ''
	if apipath is None:
		apipath = ''
	m = re.search(r'([a-zA-Z0-9]+)(/.*?)?$', apipath)
	if m is not None:
		sessionkey = m.group(1)
		req_text = m.group(2)
		if req_text.startswith('/'):
			req_text = req_text[1:]
	if sessionkey:
		user = service.get_user_by_sessionkey(sessionkey)
		if user is not None:
			clientinfo = service.get_user_clientinfo(user['id'])
			acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
			try:
				# return user_api_proxy(user)
				return user_api(clientinfo, acc_token, 'http://search.twitter.com/', False)
			except:
				response.status = 500
				return traceback.format_exc()
	return 'No such user(sk=%s)' % sessionkey


@route("/api:slash#.?#")
def api_index(*args, **kargs):
	return 'Access denied.'

# --------------------------------------

def twitter_unfollow_user(clientinfo, acc_token, user_id=0, screen_name=''):
	url = 'http://api.twitter.com/1/friendships/destroy.json'
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	if user_id>0:
		parameters['user_id'] = '%s' % user_id
	if len(screen_name)>0:
		parameters['screen_name'] = screen_name
	result = client.post(acc_token, url, parameters=parameters)
	if result:
		try:
			tw_user = json.loads(result.text)
			if isinstance(tw_user, list):
				if len(tw_user)>0:
					return tw_user[0]
			elif isinstance(tw_user, dict):
				return tw_user
		except:
			pass
	return None


def twitter_follow_user(clientinfo, acc_token, user_id=0, screen_name=''):
	url = 'http://api.twitter.com/1/friendships/create.json'
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	parameters['follow'] = 'true'
	if user_id>0:
		parameters['user_id'] = '%s' % user_id
	if len(screen_name)>0:
		parameters['screen_name'] = screen_name
	result = client.post(acc_token, url, parameters=parameters)
	if result:
		try:
			tw_user = json.loads(result.text)
			if isinstance(tw_user, list):
				if len(tw_user)>0:
					return tw_user[0]
			elif isinstance(tw_user, dict):
				return tw_user
		except:
			pass
	return None

def get_twitter_user(clientinfo, acc_token, user_id=0, screen_name=''):
	url = 'http://api.twitter.com/1/users/show.json'
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	if user_id>0:
		parameters['user_id'] = '%s' % user_id
	if len(screen_name)>0:
		parameters['screen_name'] = screen_name
	result = client.send_request(acc_token, url, parameters=parameters)
	if result:
		tw_user = None
		try:
			tw_user = json.loads(result.text)
		except:
			pass
		if tw_user is not None:
			if tw_user.has_key('id'):
				return tw_user
			else:
				#raise Exception('%s' % tw_user)
				pass
	return None

def get_posts(clientinfo, acc_token, partname, max_id=0, since_id=0, user_id=0):
	url = 'http://api.twitter.com/1/statuses/%s.json' % partname
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	if max_id>0:
		parameters['max_id'] = '%s' % max_id
	if since_id>0:
		parameters['since_id'] = '%s' % since_id
	if user_id>0:
		parameters['user_id'] = '%s' % user_id
	client.log = True
	result = client.send_request(acc_token, url, parameters=parameters)
	if result:
		return result.text
	return '[]'

def send_post(clientinfo, acc_token, content, reply_to=0):
	url = 'http://api.twitter.com/1/statuses/update.json'
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	if isinstance(content, unicode):
		content = content.encode('utf-8', 'ignore')
	parameters['status'] = content
	if reply_to>0:
		parameters['in_reply_to_status_id'] = reply_to
	result = client.post(acc_token, url, parameters)
	if result:
		if result.status ==200:
			return result.text
	return '{}'

def retweet_post(clientinfo, acc_token, post_id):
	url = 'http://api.twitter.com/1/statuses/retweet/%s.json' % post_id
	client = TwClient(clientinfo=clientinfo)
	parameters = {}
	result = client.post(acc_token, url, parameters)
	if result:
		if result.status == 200:
			return result.text
	return '{}'
	
# --------------------------------------

def fetch_mentions(clientinfo, user):
	localcache = TwLocalCache(uid=user['id'])
	last_dumptime = localcache.get_max_dumptime(channel=3)
	newitemscount = 0
	if last_dumptime < now()-80:
		local_max_id = localcache.get_max_postid(channel=3)
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		# clientinfo = UserDb().get_user_clientinfo(user['id'])
		posts = get_posts(clientinfo, acc_token, 'mentions', since_id = local_max_id)
		posts = json.loads(posts)
		newitemscount = len(posts)
		for p in posts:
			localcache.add_post(p, channel=3)
	return newitemscount

def fetch_user_posts(clientinfo, user, tw_userid):
	localcache = TwLocalCache(uid=user['id'])
	last_dumptime = localcache.get_max_dumptime(channel=2)
	newitemscount = 0
	if last_dumptime < now()-80:
		# clientinfo = UserDb().get_user_clientinfo(user['id'])
		local_max_id = localcache.get_max_postid(channel=2, tw_userid=tw_userid)
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		posts = get_posts(clientinfo, acc_token, 'user_timeline', since_id = local_max_id, user_id=tw_userid)
		posts = json.loads(posts)
		newitemscount = len(posts)
		for p in posts:
			localcache.add_post(p, channel=2)
	return newitemscount

def fetch_my_posts(clientinfo, user):
	localcache = TwLocalCache(uid=user['id'])
	last_dumptime = localcache.get_max_dumptime(channel=1)
	newitemscount = 0
	if last_dumptime < now()-80:
		# clientinfo = UserDb().get_user_clientinfo(user['id'])
		local_max_id = localcache.get_max_postid(channel=1)
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		posts = get_posts(clientinfo, acc_token, 'user_timeline', since_id = local_max_id)
		posts = json.loads(posts)
		newitemscount = len(posts)
		for p in posts:
			localcache.add_post(p, channel=1)
	return newitemscount

def fetch_all_posts(clientinfo, user):
	localcache = TwLocalCache(uid=user['id'])
	last_dumptime = localcache.get_max_dumptime(channel=0)
	newitemscount = 0
	if last_dumptime < now()-80:
		# clientinfo = UserDb().get_user_clientinfo(user['id'])
		local_max_id = localcache.get_max_postid(channel=0)
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		posts = get_posts(clientinfo, acc_token, 'home_timeline', since_id = local_max_id)
		posts = json.loads(posts)
		newitemscount = len(posts)
		for p in posts:
			localcache.add_post(p, channel=0)
	return newitemscount

# --------------------------------------

@get("/timeline/username/:tw_username#[a-zA-Z0-9_]+#")
@get("/timeline/username/:tw_username#[a-zA-Z0-9_]+#/")
@view("timeline")
@auth_required()
def show_user_timeline_by_username(tw_username):
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		localcache = TwLocalCache(uid=cu.uid)
		tw_user = localcache.get_user(tw_username=tw_username)
		if tw_user is not None:
			tw_userid = int(tw_user['id'])
			url = '/timeline/user/%s' % tw_userid
			redirect(url)
		else:
			service = UserDb()
			user = service.get_user(cu.uid)
			acc_token = None
			clientinfo = None
			if user is not None:
				acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
				clientinfo = service.get_user_clientinfo(user['id'])
			tw_user = get_twitter_user(clientinfo, acc_token, screen_name=tw_username)
			if tw_user is not None:
				localcache.add_user(tw_user)
				tw_userid = int(tw_user['id'])
				url = '/timeline/user/%s' % tw_userid
				redirect(url)
			else:
				return '''Failed to query user's info'''
	return ''

@get("/timeline/user/:tw_userid#\d+#")
@get("/timeline/user/:tw_userid#\d+#/")
@view("timeline")
@auth_required()
def show_user_timeline(tw_userid):
	form = Form()
	tw_userid = int(tw_userid)
	tw_username = '%s' % tw_userid
	cu = CookieUser(request=request, response=response)
	service = UserDb()
	user = service.get_user(cu.uid)
	reloaded = 0
	posts = None
	offset = request.GET.get('offset')
	if offset is None:
		offset = ''
	try:
		offset = int(offset)
	except:
		offset = 0
	if offset<0:
		offset = 0
	pagesize = 30
	pagemark = None
	tw_user = None
	if user is not None:
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		clientinfo = service.get_user_clientinfo(user['id'])
		if not is_valid_token(acc_token):
			form.msg = '本服务当前仅能显示缓存数据除非获得你的授权，请前往“欢迎页”开始验证和授权。'
		localcache = TwLocalCache(uid=cu.uid)
		tw_user = localcache.get_user(tw_userid=tw_userid)
		if tw_user is None:
			tw_user = get_twitter_user(acc_token, user_id=tw_userid)
			if tw_user is not None:
				localcache.add_user(tw_user)
		reloaded = fetch_user_posts(clientinfo, user, tw_userid)
		posts = localcache.get_posts(channel=2, offset=offset, count=pagesize, tw_userid=tw_userid)
		pagemark = PageMark(offset=offset, pagesize=pagesize, linkpatten='<a href="/timeline/user/%s?offset=%s">%s</a>' % (tw_userid, '%s', '%s'))
		pagemark.separator = ' | '
		pagemark.current_count = len(posts)
		for p in posts:
			#p['created_at'] = str_to_local_date(p['created_at'])
			localize_post(p)
	return dict(posts=posts, reloaded=reloaded,  form_result=form, tw_user=tw_user,
	title='Timeline/%s' % tw_username, refresh_enabled=True, pagemark=pagemark,
	channel=2)



@get("/timeline/mentions")
@get("/timeline/mentions/")
@view("timeline")
@auth_required()
def show_mentions():
	form = Form()
	cu = CookieUser(request=request, response=response)
	service = UserDb()
	user = service.get_user(cu.uid)
	reloaded = 0
	posts = None
	offset = request.GET.get('offset')
	if offset is None:
		offset = ''
	try:
		offset = int(offset)
	except:
		offset = 0
	if offset<0:
		offset = 0
	pagesize = 30
	pagemark = None
	if user is not None:
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		clientinfo = service.get_user_clientinfo(user['id'])
		if not is_valid_token(acc_token):
			form.msg = '本服务当前仅能显示缓存数据除非获得你的授权，请前往“欢迎页”开始验证和授权。'
		localcache = TwLocalCache(uid=cu.uid)	
		reloaded = fetch_mentions(clientinfo, user)	
		posts = localcache.get_posts(channel=3, offset=offset, count=pagesize)
		pagemark = PageMark(offset=offset, pagesize=pagesize, linkpatten='<a href="/timeline/mentions?offset=%s">%s</a>')
		pagemark.separator = ' | '
		pagemark.current_count = len(posts)
		for p in posts:
			#p['created_at'] = str_to_local_date(p['created_at'])
			localize_post(p)
	return dict(posts=posts, reloaded=reloaded,  form_result=form, tw_user=None,
	title='Timeline/@', refresh_enabled=True, pagemark=pagemark,
	channel=3)


@get("/timeline/i")
@get("/timeline/i/")
@view("timeline")
@auth_required()
def show_my_timeline():
	form = Form()
	cu = CookieUser(request=request, response=response)
	service = UserDb()
	user = service.get_user(cu.uid)
	reloaded = 0
	posts = None
	offset = request.GET.get('offset')
	if offset is None:
		offset = ''
	try:
		offset = int(offset)
	except:
		offset = 0
	if offset<0:
		offset = 0
	pagesize = 30
	pagemark = None
	tw_user = None
	if user is not None:
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		clientinfo = service.get_user_clientinfo(user['id'])
		if not is_valid_token(acc_token):
			form.msg = '本服务当前仅能显示缓存数据除非获得你的授权，请前往“欢迎页”开始验证和授权。'
		localcache = TwLocalCache(uid=cu.uid)	
		reloaded = fetch_my_posts(clientinfo, user)	
		posts = localcache.get_posts(channel=1, offset=offset, count=pagesize)
		pagemark = PageMark(offset=offset, pagesize=pagesize, linkpatten='<a href="/timeline/i?offset=%s">%s</a>')
		pagemark.separator = ' | '
		pagemark.current_count = len(posts)
		for p in posts:
			#p['created_at'] = str_to_local_date(p['created_at'])
			localize_post(p)
	return dict(posts=posts, reloaded=reloaded,  form_result=form,  tw_user=tw_user,
	title='Timeline/My Statuses', refresh_enabled=True, pagemark=pagemark,
	channel=1)


@get("/timeline")
@get("/timeline/")
@get("/timeline/home")
@get("/timeline/home/")
@view("timeline")
@auth_required()
def show_home_timeline():
	form = Form()
	cu = CookieUser(request=request, response=response)
	service = UserDb()
	user = service.get_user(cu.uid)
	reloaded = 0
	posts = None
	offset = request.GET.get('offset')
	if offset is None:
		offset = ''
	try:
		offset = int(offset)
	except:
		offset = 0
	if offset<0:
		offset = 0
	pagesize = 30
	pagemark = None
	if user is not None:
		acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
		clientinfo = service.get_user_clientinfo(user['id'])
		if not is_valid_token(acc_token):
			form.msg = '本服务当前仅能显示缓存数据除非获得你的授权，请前往“欢迎页”开始验证和授权。'
		localcache = TwLocalCache(uid=cu.uid)
		reloaded = fetch_all_posts(clientinfo, user)
		posts = localcache.get_posts(channel=0, offset=offset, count=pagesize)
		pagemark = PageMark(offset=offset, pagesize=pagesize, linkpatten='<a href="/timeline?offset=%s">%s</a>')
		pagemark.separator = ' | '
		pagemark.current_count = len(posts)
		for p in posts:
			#p['created_at'] = str_to_local_date(p['created_at'])
			localize_post(p)
	return dict(posts=posts, reloaded=reloaded, form_result=form, tw_user=None,
	title='Timeline/Home', refresh_enabled=True, pagemark=pagemark,
	channel=0)



@get("/timeline/i/add/")
@get("/timeline/i/add")
@post("/timeline/i/add/")
@post("/timeline/i/add")
@view("post")
@auth_required()
def add_new_post():
	form = Form()
	cu = CookieUser(request=request, response=response)
	content = ''
	reply_post_id = 0
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		if user is not None:
			localcache = TwLocalCache(uid=cu.uid)
			acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
			clientinfo = service.get_user_clientinfo(user['id'])
			if not is_valid_token(acc_token):
				form.msg = '本服务无法提交数据除非获得你的授权，请前往“欢迎页”开始验证和授权。'
			else:
				if len(request.forms)>0:
					try:
						reply_post_id = int(request.forms['reply_post_id'])
					except:
						reply_post_id = 0
					content = request.forms['content']
					if content:
						result = send_post(clientinfo, acc_token, content, reply_to=reply_post_id)
						if result:
							form.msg = '已成功发布。'
							form.success = True
						else:
							form.msg = '发布时出现错误。'
					else:
						form.msg = 'Invalid content.'
	else:
		form.msg = 'Access denied.'
	return dict(form_result=form, title='Timeline/Add' if reply_post_id<=0 else 'Timeline/Reply', 
		reply_post_id=reply_post_id, initial_text=content)


@post("/timeline/reply/")
@post("/timeline/reply")
@view("post")
@auth_required()
def show_reply_form():
	try:
		reply_post_id = int(request.forms['pid'])
	except:
		reply_post_id = 0
	reply_username = request.forms.get('screen_name') or ''
	form = Form()
	return dict(form_result=form, title='Timeline/Reply', 
		reply_post_id=reply_post_id, initial_text='@%s ' % reply_username)


@post("/timeline/retweet/")
@post("/timeline/retweet")
@view("post")
@auth_required()
def do_retweet_post():
	try:
		rt_post_id = int(request.forms['pid'])
	except:
		rt_post_id = 0
	try:
		channel = int(request.forms['channel'])
	except:
		channel = 0
	try:
		tw_userid = int(request.forms['tw_userid'])
	except:
		tw_userid = 0
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		if user is not None:
			acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
			clientinfo = service.get_user_clientinfo(user['id'])
			localcache = TwLocalCache(uid=cu.uid)
			retweet_post(clientinfo, acc_token, post_id=rt_post_id)
			if channel==1:
				redirect('/timeline/i')
			elif channel==2 and tw_userid>0:
				redirect('/timeline/user/%s' % tw_userid)
			else:
				redirect('/timeline')
	return ''
# ----------------


@get("/follow/:tw_userid#\d+#")
@get("/follow/:tw_userid#\d+#/")
@auth_required()
def follow_user(tw_userid):
	tw_userid = int(tw_userid)
	if tw_userid>0:
		# twitter_follow_user(
		cu = CookieUser(request=request, response=response)
		if cu.authenticated:
			service = UserDb()
			user = service.get_user(cu.uid)
			if user is not None:
				localcache = TwLocalCache(uid=cu.uid)
				localcache.del_user(tw_userid=tw_userid)
				acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
				clientinfo = service.get_user_clientinfo(user['id'])
				tw_user = twitter_follow_user(clientinfo, acc_token, user_id=tw_userid)
				if tw_user is not None:
					if tw_user.has_key('following'):
						if not tw_user['following']:
							# return 'still following... failure'
							tw_user['following'] = True
					else:
						return '%s' % tw_user
					localcache.add_user(tw_user)
					redirect("/timeline/user/%s" % tw_userid)
	return 'Failed.'


@get("/unfollow/:tw_userid#\d+#")
@get("/unfollow/:tw_userid#\d+#/")
@auth_required()
def unfollow_user(tw_userid):
	tw_userid = int(tw_userid)
	if tw_userid>0:
		# twitter_follow_user(
		cu = CookieUser(request=request, response=response)
		if cu.authenticated:
			service = UserDb()
			user = service.get_user(cu.uid)
			if user is not None:
				localcache = TwLocalCache(uid=cu.uid)
				localcache.del_user(tw_userid=tw_userid)
				acc_token = oauth.OAuthToken(user['tw_acctoken'], user['tw_acctokensecret'])
				clientinfo = service.get_user_clientinfo(user['id'])
				tw_user = twitter_unfollow_user(clientinfo, acc_token, user_id=tw_userid)
				if tw_user is not None:
					if tw_user.has_key('following'):
						if tw_user['following']:
							# return 'still following... failure'
							tw_user['following'] = False
					else:
						return '%s' % tw_user
					localcache.add_user(tw_user)
					redirect("/timeline/user/%s" % tw_userid)
	return 'Failed.'


@get("/timeline/fetchall/")
@get("/timeline/fetchall")
@auth_required()
def retreive_new_items_count():
	cu = CookieUser(request=request, response=response)
	service = UserDb()
	user = service.get_user(cu.uid)
	if user is not None:
		clientinfo = service.get_user_clientinfo(user['id'])
		new_items_count = 0
		new_items_count += fetch_all_posts(clientinfo, user)
		# new_items_count += fetch_my_posts(user)
		return '%s' % new_items_count
	return '0'

class MyJsonEncoder(json.JSONEncoder):	
	def default(self, obj):
		if isinstance(obj, datetime.datetime):
			#return 'datetime.datetime'
			return obj.strftime("%a %b %d %H:%M:%S %%s %Y") % '+0080'
		return '%s' % type(obj)

def retreive_top_items(channel, since_id):
	cu = CookieUser(request=request, response=response)
	if cu.authenticated:
		service = UserDb()
		user = service.get_user(cu.uid)
		if user is not None:
			clientinfo = service.get_user_clientinfo(user['id'])
			fetch_all_posts(clientinfo, user)
			lc = TwLocalCache(uid=cu.uid)
			items = lc.get_posts(channel=channel, since_id=since_id)
			for p in items:
				localize_post(p)
			json_items_str = ''
			try:
				json_items_str = json.dumps(items, cls=MyJsonEncoder)
			except:
				return '"json.dumps" failed: \n%s' % traceback.format_exc()
			return json_items_str
	return ''


@get("/timeline/since/:since_id#\d+#/")
@get("/timeline/since/:since_id#\d+#")
@auth_required()
def retreive_home_top_items(since_id):
	return retreive_top_items(0, since_id)


@get("/timeline/i/since/:since_id#\d+#/")
@get("/timeline/i/since/:since_id#\d+#")
@auth_required()
def retreive_my_top_items(since_id):
	return retreive_top_items(1, since_id)





