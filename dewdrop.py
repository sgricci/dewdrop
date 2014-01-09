#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import gobject
gobject.threads_init()
from windows.about import About
from windows.noteWindow import NoteWindow
from windows.dropWindow import DropWindow
from windows.settingsWindow import SettingsWindow
from dapi import DAPI
from config import Config
import notify
import sys
from shot import Shot
import pkg_resources
import time
try:
	import appindicator
	USE_APP_INDICATOR = True
except ImportError:
	USE_APP_INDICATOR = False

import base64
import webbrowser
from threading import Thread
import threading
import thread


class DewDrop:
	def __init__(self, app):
		self._app = app
		self._app.dew = self

		icons = gtk.IconTheme()
		app_icon = "tray"
		try:
			assert icons.has_icon(app_icon)
		except AssertionError:
			app_icon = "/tmp/tray.png"
			icon = pkg_resources.resource_string(__name__, 'windows/resources/tray/white.png')
			f = open(app_icon, "w")
			f.write(icon)
			f.close()
		
		if not hasattr(self._app, 'statusIcon'):
			if USE_APP_INDICATOR:
				self._app.statusIcon = appindicator.Indicator('Dewdrop', app_icon, appindicator.CATEGORY_APPLICATION_STATUS)
				self._app.statusIcon.set_status(appindicator.STATUS_ACTIVE)
			else:
				self._app.statusIcon = gtk.StatusIcon()
				self._app.statusIcon.set_from_file(app_icon)

		self.init_menu()


		self.dapi = DAPI()
		self.dapi.auth(self._app._cfg.get('email'), self._app._cfg.get('passhash'))

		self.show_hide_drop()

		gtk.main()


	def init_menu(self):
		menu = gtk.Menu()
		takescreenshot = gtk.MenuItem("Capture Screenshot...")
		uploadfile = gtk.MenuItem("Upload a file...")
		createnote = gtk.MenuItem("Create note...")
		#dropzone = gtk.MenuItem("Show Drop Window")
		settings = gtk.MenuItem("Settings...")
		recent = gtk.MenuItem("Recent Drops")
		about = gtk.MenuItem("About")
		logout = gtk.MenuItem("Logout")
		quit = gtk.MenuItem("Quit DewDrop")

		separator1 = gtk.SeparatorMenuItem()
		separator1.show()
		separator2 = gtk.SeparatorMenuItem()
		separator2.show()

		self.recent = recent

		createnote.show()
		uploadfile.show()
		settings.show()
		recent.show()
		about.show()
		logout.show()
		quit.show()
		takescreenshot.show()
		#dropzone.show()

		takescreenshot.connect("activate", self.take_screenshot)
		createnote.connect("activate", self.create_note)
		uploadfile.connect("activate", self.upload_file)
		#dropzone.connect("activate", self.show_hide_drop)
		settings.connect("activate", self.show_settings)
		recent.connect("activate", self.show_recent)
		logout.connect("activate", self.logout)
		quit.connect("activate", self.quit)
		about.connect("activate", self.about)

		menu.append(takescreenshot)
		menu.append(uploadfile)
		menu.append(createnote)
		#menu.append(dropzone)
		menu.append(settings)
		menu.append(separator1)
		menu.append(recent)
		menu.append(separator2)
		menu.append(about)
		menu.append(logout)
		menu.append(quit)
		if USE_APP_INDICATOR:
			self._app.statusIcon.set_menu(menu)
		else: 
			self._app.statusIcon.connect('popup-menu', self.popup, menu)

		menu.connect("show", self.show_recent)
		return menu

	def popup(self, widget, button, time, data = None):
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, gtk.status_icon_position_menu,
					3, time, self._app.statusIcon)

	def hide(self):
		# close open windows
		window_list = gtk.window_list_toplevels()
		for window in window_list:
			if gtk.WINDOW_TOPLEVEL == window.get_window_type():
				window.destroy()
		if USE_APP_INDICATOR:
			self._app.statusIcon.set_status(appindicator.STATUS_PASSIVE)
			self._app.statusIcon.get_menu().destroy()
		gtk.main_quit()


	def show_recent(self, widget):
		rtn = self.dapi.drops()
		if rtn.is_error():
			print rtn.get_message()
		elif not rtn.get_message():
			return
		else:
			menu = gtk.Menu()

			for drop in rtn.get_message():
				title = drop['title']
				title = (title[:27] + '...') if len(title) > 30 else title

				menuitem = gtk.MenuItem(title)
				menuitem.show()
				menuitem.connect("activate", self.open_drop, drop['shortlink'])
				menu.append(menuitem)

			
			separator = gtk.SeparatorMenuItem()
			separator.show()
			menu.append(separator)

			show_all = gtk.MenuItem("View All Drops")
			show_all.show()
			show_all.connect("activate", self.view_all_drops)
			menu.append(show_all)

			self.recent.set_submenu(menu)
	
	def open_drop(self, widget, link):
		# open link in browser
		webbrowser.open(link)
	
	def view_all_drops(self, widget):
		# open droplr.com in browser
		webbrowser.open("http://droplr.com")

	def upload_file_and_notify(self, filename):
		rtn = self.dapi.upload(filename)
		lock = thread.allocate_lock()
		if rtn.is_error():
			print rtn.get_message()

		gtk.threads_enter()
		try:
			shortlink = self.format_link(rtn.get_message())
			gobject.idle_add(notify.show, shortlink)
			gobject.idle_add(self.copy_to_clipboard, shortlink)
		finally:
			gtk.threads_leave()
		return

	def format_link(self, message):
		if message['privacy'] == 'PUBLIC':
			return message['shortlink']
		return "%s/%s" % (message['shortlink'], message['password'])



	def copy_to_clipboard(self, shortlink):
		clip = gtk.clipboard_get()

		clip.set_text(shortlink)
		clip.store()

	def create_note_and_notify(self, text, content_type='text/plain'):
		rtn = self.dapi.note(text, content_type)
		if rtn.is_error():
			print rtn.get_message()

		notify.show(rtn.get_message()['shortlink'])

		clip = gtk.clipboard_get()

		clip.set_text(rtn.get_message()['shortlink'])
		clip.store()

	def create_link_and_notify(self, link, privacy='PUBLIC'):
		rtn = self.dapi.link(link, privacy)
		if rtn.is_error():
			print rtn.get_message()

		notify.show(rtn.get_message()['shortlink'])

		clip = gtk.clipboard_get()

		clip.set_text(rtn.get_message()['shortlink'])
		clip.store()


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
			try:
				t = Thread(target=self.upload_file_and_notify, args=(filename,)).start()
			except Exception as e:
				print e
				print "Failed to start thread"
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
		try:
			t = Thread(target=self.upload_file_and_notify, args=(filename,)).start()
		except Exception as e:
			print e
			print "Failed to start thread"

	def show_hide_drop(self, widget=None):
		dropzone = self._app._cfg.get('dropzone')

		if hasattr(self, 'drop'):
			self.drop.hide()
			delattr(self, 'drop')

		if dropzone is not None and dropzone != 'hide':
			self.drop = DropWindow(self._app)
			self.drop.show()

	def show_settings(self, widget):
		settings = SettingsWindow(self._app)
		settings.show()



	def about(self, widget):
		about = About()
		about.show()

	def logout(self, widget):
		self.hide()
		self._app.logout()

	def quit(self, widget):
		sys.exit(0)

	# def right_click_event(self, icon, button, time):
	# 	self.menu = gtk.Menu()
		
	# 	takescreenshot = gtk.MenuItem("Capture Screenshot...")
	# 	about = gtk.MenuItem("About")
	# 	logout = gtk.MenuItem("Logout")
	# 	quit = gtk.MenuItem("Quit DewDrop")
		
	# 	takescreenshot.connect("activate", self.take_screenshot)
	# 	logout.connect("activate", self.logout)
	# 	quit.connect("activate", self.quit)
	# 	about.connect("activate", self.about)

	# 	menu.append(takescreenshot)
	# 	menu.append(gtk.MenuItem())
	# 	menu.append(about)
	# 	menu.append(logout)
	# 	menu.append(quit)

	# 	menu.show_all()

	# 	menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)
