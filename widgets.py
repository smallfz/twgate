# -*- coding: utf8 -*-

def smart_encode(text):
	if isinstance(text, unicode):
		return text.encode('utf-8', 'ignore')
	return text

class Form(object):

	def __init__(self, msg='', success=False):
		self.msg = smart_encode(msg)
		self.success = success
	
	def __str__(self):
		html=[]
		if self.msg:
			if self.success:
				html.append('<span class="success">')
			else:
				html.append('<span class="fail">')
			html.append(self.msg)
			html.append('</span>')
		return ''.join(html)


class PageMark(object):

	def __init__(self, offset=0, pagesize=0, 
		linkpatten='<a href="?offset=%s">%s</a>', separator=' ', current_count=0):
		self.offset = offset
		if self.offset < 0:
			self.offset = 0
		self.pagesize = pagesize
		if self.pagesize < 0:
			self.pagesize = 0
		self.separator = separator
		self.linkpatten = linkpatten
		self.current_count = current_count
		self.go_first = False

	def __str__(self):
		self.go_first = True if self.current_count<=0 else False
		html = []
		if self.offset>=0 and self.pagesize>0:
			marks = range(2, int(self.offset/self.pagesize) +1)
			p_off = 0
			html.append(self.linkpatten % (p_off, '&laquo;First'))
			for i in marks:
				p_off = self.offset - i*self.pagesize
				html.append(self.linkpatten % (p_off, i))
			if self.current_count>0:
				p_off = self.offset + self.pagesize
				html.append(self.linkpatten % (p_off, 'Next&raquo;'))
		else:
			if self.go_first:
				html.append(self.linkpatten % (0, '&laquo;First'))
		return self.separator.join(html)







