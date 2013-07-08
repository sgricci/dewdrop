#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import hashlib
import sys
import pkg_resources

class LoginWindow:
	def __init__(self, app):
		self.app = app

		self.builder = gtk.Builder()
		self.builder.add_from_string(pkg_resources.resource_string(__name__, "../data/ui/login.glade"))
		self.builder.connect_signals(self)
		loader = gtk.gdk.PixbufLoader('png')
		loader.write(pkg_resources.resource_string(__name__, "../resources/icon/dewdrop_256.png"))
		loader.close()
		icons = gtk.IconTheme()
		app_icon = "tray"
		try:
			assert icons.has_icon(app_icon)
		except AssertionError:
			app_icon = "/tmp/tray.png"
			icon = pkg_resources.resource_string(__name__, '../resources/tray/32/dewdrop_32_100.png')
			f = open(app_icon, "w")
			f.write(icon)
			f.close()
		self.builder.get_object('loginWindow').set_icon_from_file(app_icon)
		self.builder.get_object('loginImage').set_from_pixbuf(loader.get_pixbuf())
		self.builder.get_object('loginWindow').show()
		self.builder.get_object('loginWindow').connect('destroy', lambda x: gtk.main_quit())
		
	def show(self):
		gtk.main()

	def exit(self, widget, data=None):
		self.builder.get_object('loginWindow').destroy()
		gtk.main_quit()
		sys.exit(0)

	def sign_in(self, widget, data=None):
		email = self.builder.get_object('txtEmail').get_text()
		password = self.builder.get_object('txtPassword').get_text()

		if not email or not password:
			self.builder.get_object('lblMessage').set_text("Please fill out both fields")
			return False

		passhash = hashlib.sha1(password).hexdigest()
		del password
		rtn = self.app.test_credentials(email, passhash)
		if rtn == True:
			self.app._cfg.set('email', email)
			self.app._cfg.set('passhash', passhash)
			self.app._cfg.save()
			self.builder.get_object('loginWindow').destroy()
			self.app.start()
		else:
			self.builder.get_object('lblMessage').set_text(rtn.get_message())
