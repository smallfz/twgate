# -*- coding: utf8 -*-

import sqlite3_helper as sh
import hashlib
from time import time as now
import datetime

_dbpath = 'users.db'
_publickey = '''34bnm6278c4w630345jk43lkx83402hgvcxfdfsdfasfdaqew
qewf349327weertetytjhjr2xd83ioipovo939475846vbnvjzjghdgkw4345a9r56
6euyyi3761d283iu23d9ou38oipi4ert95bmzutygh38'''

def safe_str(text):
	if text is None:
		return ''
	else:
		return text.replace("'", "''")

class CookieUser(object):
	
	def __init__(self, request=None, response=None):
		self.request = request
		self.response = response
	
	@property
	def uid(self):
		if self.request is not None:
			if self.request.COOKIES.has_key('uid'):
				try:
					return int(self.request.COOKIES['uid'])
				except:
					pass
		return 0
	
	@property
	def username(self):
		if self.request is not None:
			if self.request.COOKIES.has_key('uname'):
				return self.request.COOKIES['uname']
		return ''
	
	@property
	def authenticated(self):
		return self.uid>0 and len(self.username)>0
	
	def save(self, uid, username, keep=False):
		if self.response is not None:
			hashtext = hashlib.md5('%s\n%s\n%s' % (uid, username, _publickey)).hexdigest()
			#expires = int(now()) + (3600*24)*14 # 2 weeks
			#expires_date = datetime.datetime.fromtimestamp(expires)
			cookielifelen = 3600 * 24 * 14 # 2 weeks
			if keep:
				self.response.set_cookie('uid', '%s' % uid, max_age=cookielifelen)
				self.response.set_cookie('uname', username, max_age=cookielifelen)
				self.response.set_cookie('hash', hashtext, max_age=cookielifelen)
			else:
				self.response.set_cookie('uid', '%s' % uid)
				self.response.set_cookie('uname', username)
				self.response.set_cookie('hash', hashtext)
	
	def clear(self):
		if self.response is not None:
			#self.response.delete_cookie('uid')
			#self.response.delete_cookie('uname')
			#self.response.delete_cookie('hash')
			self.response.set_cookie('uid', '')
			self.response.set_cookie('uname', '')
			self.response.set_cookie('hash', '')
	
	def __str__(self):
		return self.username

class UserDb(object):

	def _checktables(self):
		db = sh.Connection(_dbpath)
		alltables = db.get_tables()
		if not 't_users' in alltables:
			db.execute('''
				create table t_users (
					id INTEGER PRIMARY KEY,
					username TEXT,
					passhash TEXT,
					email TEXT,
					regtime INTEGER,
					tw_user TEXT,
					tw_reqtoken TEXT,
					tw_reqtokensecret TEXT,
					tw_acctoken TEXT,
					tw_acctokensecret TEXT,
					sessionkey TEXT
				)
			''')
		if not 't_clientinfo' in alltables:
			db.execute('''
				create table t_clientinfo (
					id INTEGER PRIMARY KEY,
					consumer_key TEXT,
					consumer_secret TEXT,
					tw_userid INTEGER,
					local_userid INTEGER
				)
			''')
		db.close()

	def __init__(self):
		self._checktables()
		self.reguserid = 0
		self.errmsg = ''
	
	def password_hash(self, password):
		return hashlib.md5(password).hexdigest()
	
	def register(self, email, password):
		self.errmsg = ''
		if len(email)>0 and len(password)>0:
			proceed = True
			db = sh.Connection(_dbpath)
			rs = db.read('''select id from t_users where username='%s' ''' % safe_str(email))
			if len(rs)>0:
				proceed = False
				self.errmsg = '用户名已存在。'
			else:
				sql='''insert into t_users (username, passhash, email, regtime, 
				tw_user, tw_reqtoken, tw_reqtokensecret, tw_acctoken, tw_acctokensecret,
				sessionkey) values ('%s', '%s', '%s', %s, '', '', '', '', '', '') 
				''' % (safe_str(email), self.password_hash(password), safe_str(email), now())
				db.execute(sql)
				# self.reguserid = db.lastrowid
			db.close()	
			return proceed
		return False
	
	def login(self, email, password):
		user = None
		db = sh.Connection(_dbpath)
		rs = db.read('''select id, username, passhash, sessionkey, email,
		regtime, tw_user, tw_reqtoken, tw_reqtokensecret, 
		tw_acctoken, tw_acctokensecret 
		 from t_users where username='%s' ''' % safe_str(email))
		if len(rs)>0:
			if rs[0]['passhash'].lower() == self.password_hash(password).lower():
				user = rs[0]
		db.close()
		return user
	
	def change_password(self, uid, newpassword):
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		db.execute('''update t_users set passhash='%s' where id=%s''' % (self.password_hash(newpassword), uid))
		db.close()
	
	def get_user(self, uid):
		try:
			uid = int(uid)
		except:
			uid = 0
		user = None
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_users where id=%s''' % uid)
		if len(rs)>0:
			user = rs[0]
		db.close()
		return user

	def get_user_clientinfo(self, uid):
		try:
			uid = int(uid)
		except:
			uid = 0
		clientinfo = None
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_clientinfo where local_userid=%s limit 0,1''' % uid)
		db.close()
		if len(rs)>0:
			clientinfo = rs[0]
			if len(clientinfo['consumer_key'])<=0 or len(clientinfo['consumer_secret'])<=0:
				#self.errmsg = 'The key or secret is empty.'
				return None
			else:
				clientinfo['Consumer_key'] = clientinfo['consumer_key'].encode('utf-8','ignore')
				clientinfo['Consumer_secret'] = clientinfo['consumer_secret'].encode('utf-8','ignore')
		else:
			#self.errmsg='Empty result.'
			pass
		return clientinfo

	def set_user_clientinfo(self, uid, consumer_key, consumer_secret):
		''' set user's client-info, create it if it's not exist.
		arguments: uid, consumer_key, consumer_secret '''
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_clientinfo where local_userid=%s limit 0,1''' % uid)
		sql=[]
		if len(rs)>0:
			sql.append("update t_clientinfo set ")
			sql.append("consumer_key='%s', consumer_secret='%s' where id=%s" % (safe_str(consumer_key), safe_str(consumer_secret), rs[0]['id']))
			db.execute(''.join(sql))
		else:
			db.execute("delete from t_clientinfo where local_userid=%s" % uid)
			#
			sql.append("insert into t_clientinfo (tw_userid, local_userid, ")
			sql.append("consumer_key, consumer_secret) values (")
			sql.append("%s, %s, '%s', '%s')" % (0, uid, safe_str(consumer_key), safe_str(consumer_secret)))
			db.execute(''.join(sql))
		#self.errmsg = ''.join(sql)
		db.close()

	def get_user_by_email(self, email):
		user = None
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_users where username='%s' ''' % safe_str(email))
		if len(rs)>0:
			user = rs[0]
		db.close()
		return user
	
	def get_user_by_req_token(self, token_key):
		user = None
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_users where tw_reqtoken='%s' ''' % safe_str(token_key))
		if len(rs)>0:
			user = rs[0]
		db.close()
		return user
	
	def get_user_by_sessionkey(self, sessionkey):
		user = None
		if sessionkey:
			db = sh.Connection(_dbpath)
			rs = db.read('''select * from t_users where sessionkey='%s' ''' % safe_str(sessionkey))
			if len(rs)>0:
				user = rs[0]
			db.close()
			return user
		return None
	
	def save_req_token(self, uid, key, secret):
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		db.execute("""update t_users set  
		tw_reqtoken='%s', tw_reqtokensecret='%s' 
		where id=%s""" % (safe_str(key), safe_str(secret), uid))
		db.close()
	
	def save_acc_token(self, uid, key, secret):
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		db.execute("""update t_users set  
		tw_acctoken='%s', tw_acctokensecret='%s' 
		where id=%s""" % (safe_str(key), safe_str(secret), uid))
		db.close()
	
	def generate_new_sessionkey(self, uid, sessionkey):
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		db.execute("""update t_users set  
		sessionkey='%s' 
		where id=%s""" % (sessionkey, uid))
		db.close()
	
	def clear_tokens(self, uid):
		''' delete all oauth tokens '''
		try:
			uid = int(uid)
		except:
			uid = 0
		db = sh.Connection(_dbpath)
		db.execute("""update t_users set tw_user='', 
		tw_reqtoken='', tw_reqtokensecret='',
		tw_acctoken='', tw_acctokensecret='', 
		sessionkey='' 
		where id=%s""" % uid)
		db.close()
	
	def get_users(self):
		db = sh.Connection(_dbpath)
		rs = db.read('''select * from t_users''')
		db.close()
		return rs
















