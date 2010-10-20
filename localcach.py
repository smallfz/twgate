# -*- coding: utf8 -*-
import json
from time import time as now
import sqlite3_helper as sh

_dbpath = 'localcache.db'

def safe_str(text):
	if text is None:
		return ''
	else:
		return text.replace("'", "''")

class TwLocalCache(object):

	def _checktables(self, dbpath=_dbpath):
		db = sh.Connection(dbpath)
		alltables = db.get_tables()
		if not 't_posts' in alltables:
			db.execute('''
				create table t_posts (
					localid INTEGER PRIMARY KEY,
					localuserid INTEGER,
					id INTEGER,
					tw_userid INTEGER,					
					json_content TEXT,
					dumptime INTEGER,
					is_mine INTEGER
				)
			''')
		if not 't_users' in alltables:
			db.execute('''
				create table t_users (
					localid INTEGER PRIMARY KEY,
					id INTEGER,
					localuserid INTEGER,
					username TEXT,
					json_content TEXT
				)
			''')
		db.close()

	def __init__(self, uid=0, dbpath=_dbpath):
		self.uid = uid
		self._checktables(dbpath)
	
	def add_post(self, post, channel=0):
		if isinstance(post, dict):
			db = sh.Connection(_dbpath)
			db.execute("delete from t_posts where id=%s and localuserid=%s and is_mine=%s" % (post['id'], self.uid, channel))
			try:
				tw_userid = int(post['user']['id'])
			except:
				tw_userid = 0
			db.execute('''
				insert into t_posts (id, localuserid, json_content, dumptime, is_mine, tw_userid) 
				values (
				%s, %s, '%s', %s, %s, %s
				)
			''' % (post['id'], self.uid, safe_str(json.dumps(post)), int(now()), channel, tw_userid ))
			db.close()
			return True
		return False

	def del_user(self, tw_userid=0):
		if tw_userid>0:
			db = sh.Connection(_dbpath)
			db.execute('delete from t_users where id=%s and localuserid=%s' % (tw_userid, self.uid))
			db.close()

	def add_user(self, user):
		if isinstance(user, dict):
			if user.has_key('id'):
				db = sh.Connection(_dbpath)
				tw_userid = int(user['id'])
				tw_username = user['screen_name']
				rs = db.read('select id from t_users where id=%s and localuserid=%s' % (tw_userid, self.uid))
				if len(rs)<=0:
					#db.execute("delete from t_users where id=%s and localuserid=%s" % (tw_userid, self.uid))
					db.execute('''
						insert into t_users (id, localuserid, username, json_content) 
						values (%s, %s, '%s', '%s')
					''' % (tw_userid, self.uid, safe_str(tw_username), safe_str(json.dumps(user))))
				else:
					db.execute('''
						update t_users set username='%s', json_content='%s'
						where id=%s and localuserid=%s
					''' % (safe_str(tw_username), safe_str(json.dumps(user)), tw_userid, self.uid))
				db.close()
			return True
		return False
	
	def get_user(self, tw_userid=0, tw_username=''):
		if tw_userid>0 or len(tw_username)>0:
			db = sh.Connection(_dbpath)
			sql = []
			sql.append('select * from t_users where localuserid=%s ' % self.uid)
			if tw_userid>0:
				sql.append(' and id=%s' % tw_userid)
			else:
				sql.append(''' and username='%s' ''' % safe_str(tw_username))
			rs = db.read(''.join(sql))
			db.close()
			if len(rs)>0:
				return json.loads(rs[0]['json_content'])
				#return rs[0]
		return None
	
	def get_max_postid(self, channel=0, tw_userid=0):
		db = sh.Connection(_dbpath)
		max_id = 0
		sql=[]
		sql.append('select max(id) as max_id from t_posts where ')
		sql.append("localuserid=%s and is_mine=%s" % (self.uid, channel))
		if tw_userid>0:
			sql.append(' and tw_userid=%s' % tw_userid)
		rs = db.read(''.join(sql))
		if len(rs)>0:
			try:
				max_id = int(rs[0]['max_id'])
			except:
				max_id = 0
		db.close()
		return max_id
	
	def get_max_dumptime(self, channel=0):
		db = sh.Connection(_dbpath)
		max_dumptime = 0
		rs = db.read("select max(dumptime) as mdt from t_posts where localuserid=%s and is_mine=%s" % (self.uid, channel))
		if len(rs)>0:
			try:
				max_dumptime = int(rs[0]['mdt'])
			except:
				max_dumptime = 0
		db.close()
		return max_dumptime
	
	def get_posts(self, channel=0, offset=0, count=30, tw_userid=0, since_id=0):
		results = []
		db = sh.Connection(_dbpath)
		sql=[]
		sql.append('select * from t_posts where localuserid=%s and is_mine=%s ' % (self.uid, channel))
		if tw_userid>0:
			sql.append(' and tw_userid=%s ' % tw_userid)
		if since_id>0:
			sql.append(" and id>%s" % since_id)
			sql.append('order by id desc')
		elif offset>=0 and count>0:
			sql.append('order by id desc')
			sql.append(" limit %s, %s" % (offset, count))
		rs = db.read(''.join(sql))
		if len(rs)>0:
			for row in rs:
				try:
					results.append(json.loads(row['json_content']))
				except:
					pass
		db.close()
		return results









