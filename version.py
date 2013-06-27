#!/usr/bin/env python

from pkg_resources import parse_version
import pycurl
import StringIO
import simplejson as json
import notify

APP_VERSION = '0.9'
def get_version():
	return APP_VERSION

def new_version():
	# Get current version
	c = pycurl.Curl()
	b = StringIO.StringIO()
	c.setopt(pycurl.URL, "http://dewdrop.deepcode.net/version.php?v=%s" % get_version())
	c.setopt(pycurl.WRITEFUNCTION, b.write)
	c.perform()
	res = json.loads(b.getvalue())
	current = res.get('version')
	if parse_version(current) > parse_version(APP_VERSION):
		# Version is different
		notify.update(res.get('url'))
	return True
