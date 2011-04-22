#
# for apache mod_wsgi
#

import os, sys

startup_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(startup_dir)
if startup_dir not in sys.path:
	sys.path.append(startup_dir)

import bottle
import gate
bottle.TEMPLATE_PATH.insert(0, os.path.join(startup_dir, 'views'))
application = bottle.default_app()

