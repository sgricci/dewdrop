#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import pkg_resources
import sys

class NoteWindow:
	def __init__(self, app):
		self.app = app

		self.builder = gtk.Builder()

		self.builder.add_from_string(pkg_resources.resource_string(__name__, "data/ui/note.glade"))
		self.builder.connect_signals(self)

		loader = gtk.gdk.PixbufLoader('png')
		loader.write(pkg_resources.resource_string(__name__, "resources/icons/icon.png"))
		loader.close()
		icons = gtk.IconTheme()
		app_icon = "tray"
		try:
			assert icons.has_icon(app_icon)
		except AssertionError:
			app_icon = "/tmp/tray.png"
			icon = pkg_resources.resource_string(__name__, 'resources/tray/tray.png')
			f = open(app_icon, "w")
			f.write(icon)
			f.close()

		self.builder.get_object('noteWindow').set_icon_from_file(app_icon)
		self.builder.get_object('noteWindow').show()
		self.builder.get_object('noteWindow').connect('destroy', lambda x: gtk.main_quit())

	def show(self):
		gtk.main()

	def exit(self, widget, data=None):
		self.builder.get_object('noteWindow').destroy()
		gtk.main_quit()
		sys.exit()