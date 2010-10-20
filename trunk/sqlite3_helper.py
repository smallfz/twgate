# -*- coding: utf-8 -*-
# ----------------------------------------
# Database Interface (sqlite3)
# 2010/8/22 Small.fz@gmail.com
# @copyright bluemask.net
# ----------------------------------------

import sqlite3
import os

class CursorReader(object):
	def __init__(self, cursor, columns = []):
		self.cur = cursor
		self.row = None
		self.columns = columns
	
	def get_column(self, index):
		if self.columns is not None:
			if len(self.columns):
				return self.columns[index]
		return '%s' % index

	def read(self):
		row = self.cur.fetchone()
		if row is not None:
			self.row = {}
			# print row
			for i in range(0, len(row)):
				self.row[self.get_column(i)] = row[i]
			return True
		self.row = None
		return False

class Connection(object):

	def connect(self):
		if self.conn is None:
			self.conn = sqlite3.connect(self.path)
			self.conn.text_factory = lambda t: unicode(t, "utf-8", "ignore")
			self.cur = self.conn.cursor()
	
	def __init__(self, path):
		self.path = path
		self.conn = None
		self.cur = None
		self.lastsql = ''
		self.connect()
	
	def safecheck(self, obj):
		if obj is None:
			return ''
		if isinstance(obj, str) or isinstance(obj, unicode):
			return "'%s'" % obj.replace("'", "''")
		return self.safecheck('%s' % obj)
	
	def build_sql(self, *args):
		if len(args)>0:
			sql = args[0]
			if len(args)>1:
				parameters = args[1:]
				safe_parameters = []
				for p in parameters:
					safe_parameters.append(self.safecheck(p))
				sql = sql % tuple(safe_parameters)
			return sql
		return ''

	def execute(self, *args):
		sql = self.build_sql(*args)
		if len(sql)>0:
			self.connect()
			self.conn.execute(sql)
			self.lastsql = sql
			self.conn.commit()
	
	@property
	def lastrowid(self):
		rs = self.read('select last_insert_rowid() as lastrowid') # or 'select @@identity'
		if len(rs)>0:
			return rs[0]['lastrowid']
		return 0
	
	def execute_reader(self, sql):		
		self.connect()
		self.cur.execute(sql)
		col_desc = self.cur.description
		cols = [c[0] for c in col_desc]
		reader = CursorReader(self.cur, columns = cols)
		return reader
	
	def read(self, *args):
		sql = self.build_sql(*args)
		if len(sql)>0:
			reader = self.execute_reader(sql)
			result = []
			while reader.read():
				result.append(reader.row)
			return result
		return []
	
	def get_tables(self):
		return [t['name'] for t in self.read("select name from sqlite_master where type='table'")]
	
	def close(self):
		if self.cur:
			self.cur.close()
		if self.conn:
			self.conn.close()
		self.cur = None
		self.conn = None




