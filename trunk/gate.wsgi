#
# for apache mod_wsgi
#

import os, sys

os.chdir(os.path.dirname(__file__))
os.chdir('/home/small/www/twgate')
sys.path.append('/home/small/www/twgate')

import bottle
from gate import *

application = bottle.default_app()

