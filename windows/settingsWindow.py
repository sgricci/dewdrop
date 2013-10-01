#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import pkg_resources
import sys

class SettingsWindow:
	def __init__(self, app):
		self.app = app

		self.builder = gtk.Builder()

		self.builder.add_from_string(pkg_resources.resource_string(__name__, "/data/ui/settings.glade"))
		self.builder.connect_signals(self)

		loader = gtk.gdk.PixbufLoader('png')
		loader.write(pkg_resources.resource_string(__name__, "/resources/icon/dewdrop-128-black.png"))
		loader.close()
		icons = gtk.IconTheme()
		app_icon = "tray"
		try:
			assert icons.has_icon(app_icon)
		except AssertionError:
			app_icon = "/tmp/tray.png"
			icon = pkg_resources.resource_string(__name__, '/resources/tray/white.png')
			f = open(app_icon, "w")
			f.write(icon)
			f.close()

		dropzone = self.app._cfg.get('dropzone')

		#self.orig_dropzone = dropzone

		name = "btnHide"

		if dropzone == "custom":
			name = "btnCustom"
			#self.orig_x = self.app._cfg.get('x')
			#self.orig_x = self.app._cfg.get('y')
		elif dropzone == "tl":
			name = "btnTopLeft"
		elif dropzone == "tm":
			name = "btnTopMiddle"
		elif dropzone == "tr":
			name = "btnTopRight"
		elif dropzone == "ml":
			name = "btnMiddleLeft"
		elif dropzone == "mr":
			name = "btnMiddleRight"
		elif dropzone == "bl":
			name = "btnBottomLeft"
		elif dropzone == "bm":
			name = "btnBottomMiddle"
		elif dropzone == "br":
			name = "btnBottomRight"

		self.builder.get_object(name).set_active(True)

		self.builder.get_object('settingsWindow').set_focus(self.builder.get_object(name))
		self.builder.get_object('settingsWindow').set_modal(False)
		self.builder.get_object('settingsWindow').set_icon_from_file(app_icon)
		self.builder.get_object('settingsWindow').show()
		self.builder.get_object('settingsWindow').connect('destroy', lambda x: gtk.main_quit())


	def show(self):
		gtk.main()

	def exit(self, widget, data=None):
		#self.app._cfg.set('dropzone', self.orig_dropzone)
		#self.app._cfg.set('x', self.orig_x)
		#self.app._cfg.set('y', self.orig_y)

		self.builder.get_object('settingsWindow').destroy()
		gtk.main_quit()
		sys.exit()

	def save(self, widget, data=None):
		hide_button = self.builder.get_object('btnHide')

		active = [btn for btn in hide_button.get_group() if btn.get_active()][0]

		name = gtk.Buildable.get_name(active)

		dropzone = "hide"

		if name == 'btnCustom':
			dropzone = "custom"

			# try to get the current position
			x = self.app._cfg.get('x')
			y = self.app._cfg.get('y')
			if hasattr(self.app.dew, 'drop'):
				x,y = self.app.dew.drop.dialog.get_position()
			else:
				if x is None:
					x = 0
				if y is None:
					y = 0
			self.app._cfg.set('x', x)
			self.app._cfg.set('y', y)
		else:
			self.app._cfg.set('x', None)
			self.app._cfg.set('y', None)
			if name == 'btnTopLeft':
				dropzone = "tl"
			elif name == 'btnTopMiddle':
				dropzone = "tm"
			elif name == 'btnTopRight':
				dropzone = "tr"
			elif name == 'btnMiddleLeft':
				dropzone = "ml"
			elif name == 'btnMiddleRight':
				dropzone = "mr"
			elif name == 'btnBottomLeft':
				dropzone = "bl"
			elif name == 'btnBottomMiddle':
				dropzone = "bm"
			elif name == 'btnBottomRight':
				dropzone = "br"

		self.app._cfg.set('dropzone', dropzone)
		self.app._cfg.save()
		self.builder.get_object('settingsWindow').destroy()
		#refresh dropzone
		self.app.dew.show_hide_drop()

		
