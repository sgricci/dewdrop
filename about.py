#!/usr/bin/env python

import pygtk
pygtk.require('2.0')

import gtk
import pkg_resources

import version

class About:
	def __init__(self):
		self.about = gtk.AboutDialog()
		self.about.set_program_name("DewDrop")
		self.about.set_version(version.get_version())
		self.about.set_copyright("(c) Steve Gricci")
		self.about.set_comments("DewDrop is a Droplr client for Linux\n\nApplication Icon used under CC-Attribution-NonCommercial license from http://dapinographics.com")
		self.about.set_website("http://dewdropapp.tumblr.com")
		loader = gtk.gdk.PixbufLoader('png')
		loader.write(pkg_resources.resource_string(__name__, "resources/icons/icon.png"))
		loader.close()
		self.about.set_logo(loader.get_pixbuf())
	def show(self):
		self.about.run()
		self.about.destroy()
