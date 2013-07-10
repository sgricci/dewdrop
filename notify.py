#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import pynotify
import pkg_resources

def show(link):
	if not pynotify.init ("summary-body"):
		return False
	icons = gtk.IconTheme()
	app_icon = "dewdrop"
	try:
		assert icons.has_icon(app_icon)
	except AssertionError:
		app_icon = "/tmp/dewdrop.png"
		icon = pkg_resources.resource_string(__name__, 'resources/icon/dewdrop_256.png')
		f = open(app_icon, "w")
		f.write(icon)
		f.close()

	n = pynotify.Notification ("DewDrop", "Upload Complete: %s" % link, app_icon)
	n.show()

def update(link):
	if not pynotify.init ("summary-body"):
		return False
	icons = gtk.IconTheme()
	app_icon = "dewdrop"
	try:
		assert icons.has_icon(app_icon)
	except AssertionError:
		app_icon = "/tmp/dewdrop.png"
		icon = pkg_resources.resource_string(__name__, 'resources/icon/dewdrop_256.png')
		f = open(app_icon, "w")
		f.write(icon)
		f.close()

	n = pynotify.Notification ("DewDrop", "Update Available: %s" % link, app_icon)
	n.show()
