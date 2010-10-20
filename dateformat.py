#!/usr/bin/python

import re
from datetime import datetime, timedelta

def str_to_local_date(s):
	m = re.search(r'([a-zA-Z]{2,4}\s[a-zA-Z]{2,4}\s\d+\s\d+\:\d+\:\d+\s)([+-]\d+)\s(\d{4}$)', s)
	if m is not None:
		z = m.group(2).strip()
		z = int(z)
		s = '%s %s' % (m.group(1).strip(), m.group(3))
		dd = timedelta(hours=8-z)
		d = datetime.strptime(s, '%a %b %d %H:%M:%S %Y')
		return d+dd
	return None
	# return datetime.strptime(s, '%a %b %d %H:%M:%S %% %Y')

if __name__=='__main__':
	s= 'Sat Oct 02 19:15:53 +0000 2010'	
	print str_to_local_date(s)
