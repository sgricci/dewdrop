#!/usr/bin/env python
import pygtk
pygtk.require('2.0')

import gtk

from about import About
from noteWindow import NoteWindow
from dapi import DAPI
from config import Config
import notify
import sys
from shot import Shot
import pkg_resources
import time
import appindicator

class DewDrop:
	def __init__(self, app):
		self._app = app
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
		
		self.statusIcon = appindicator.Indicator('Dewdrop', app_icon, appindicator.CATEGORY_APPLICATION_STATUS)
		self.statusIcon.set_status(appindicator.STATUS_ACTIVE)
		self.init_menu()
		self.dapi = DAPI()
		self.dapi.auth(self._app._cfg.get('email'), self._app._cfg.get('passhash'))
		gtk.main()

	def init_menu(self):
		menu = gtk.Menu()
		takescreenshot = gtk.MenuItem("Capture Screenshot...")
		uploadfile = gtk.MenuItem("Upload a file...")
		createnote = gtk.MenuItem("Create note...")
		about = gtk.MenuItem("About")
		logout = gtk.MenuItem("Logout")
		quit = gtk.MenuItem("Quit DewDrop")
		separator = gtk.SeparatorMenuItem()
		separator.show()
		createnote.show()
		uploadfile.show()
		about.show()
		logout.show()
		quit.show()
		takescreenshot.show()
		
		takescreenshot.connect("activate", self.take_screenshot)
		createnote.connect("activate", self.create_note)
		uploadfile.connect("activate", self.upload_file)
		logout.connect("activate", self.logout)
		quit.connect("activate", self.quit)
		about.connect("activate", self.about)

		menu.append(takescreenshot)
		menu.append(uploadfile)
		menu.append(createnote)
		menu.append(separator)
		menu.append(about)
		menu.append(logout)
		menu.append(quit)
		self.statusIcon.set_menu(menu)
	
	def create_note(self, widget):
		note = NoteWindow(self._app)
		note.show()

	def upload_file(self, widget):
		chooser = gtk.FileChooserDialog(title="Dewdrop - Upload file", action=gtk.FILE_CHOOSER_ACTION_OPEN,
				buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

		response = chooser.run()
		if response == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()
			rtn = self.dapi.upload(filename)
			if rtn.is_error():
				print rtn.get_message()

			notify.show(rtn.get_message()['shortlink'])

			clip = gtk.clipboard_get()

			clip.set_text(rtn.get_message()['shortlink'])
			clip.store()
		elif response == gtk.RESPONSE_CANCEL:
			print 'Closed, no files selected'
			chooser.destroy()

	def take_screenshot(self, widget):
		shot = Shot()
		shot.start()
		time.sleep(0.5)
		screenshot = gtk.gdk.Pixbuf.get_from_drawable(
			gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, shot.width, shot.height),
			gtk.gdk.get_default_root_window(),
			gtk.gdk.colormap_get_system(),
			shot.sX, shot.sY, 0, 0, shot.width, shot.height)
		filename = "/tmp/droplr.png"
		screenshot.save(filename, "png")
		rtn = self.dapi.upload(filename)
		if rtn.is_error():
			print rtn.get_message()

		notify.show(rtn.get_message()['shortlink'])

		clip = gtk.clipboard_get()

		clip.set_text(rtn.get_message()['shortlink'])
		clip.store()


	def quit(self, widget):
		sys.exit(0)

	def about(self, widget):
		about = About()
		about.show()

	def logout(self, widget):
		self.statusIcon.set_visible(False)
		self._app.logout()

	def right_click_event(self, icon, button, time):
		self.menu = gtk.Menu()
		
		takescreenshot = gtk.MenuItem("Capture Screenshot...")
		about = gtk.MenuItem("About")
		logout = gtk.MenuItem("Logout")
		quit = gtk.MenuItem("Quit DewDrop")
		
		takescreenshot.connect("activate", self.take_screenshot)
		logout.connect("activate", self.logout)
		quit.connect("activate", self.quit)
		about.connect("activate", self.about)

		menu.append(takescreenshot)
		menu.append(gtk.MenuItem())
		menu.append(about)
		menu.append(logout)
		menu.append(quit)

		menu.show_all()

		menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)
