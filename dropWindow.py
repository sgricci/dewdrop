#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import pkg_resources
import sys
from urlparse import urlparse
import re
import urllib
import cairo
import gobject
from math import pi
import dewdrop

class DropWindow:

	TARGET_TYPE_TEXT = 80
	TARGET_TYPE_JPG = 81
	TARGET_TYPE_PNG = 82
	TARGET_TYPE_GIF = 83
	
	targets = [ ( "text/plain", 0, TARGET_TYPE_TEXT ), 
	( "image/jpeg", 0, TARGET_TYPE_JPG ), 
	( "image/png", 0, TARGET_TYPE_PNG ), 
	( "image/gif", 0, TARGET_TYPE_GIF ) ]

	def __init__(self, app):
		self.app = app

		self.builder = gtk.Builder()

		self.builder.add_from_string(pkg_resources.resource_string(__name__, "data/ui/drop.glade"))
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
		scaled_buf = loader.get_pixbuf().scale_simple(40, 40, gtk.gdk.INTERP_BILINEAR)
		self.builder.get_object('dropImage').set_from_pixbuf(scaled_buf)
		

		self.dialog = self.builder.get_object('dropWindow')
		self.dialog.set_keep_above(True)
		self.dialog.set_modal(False)

		# setup drop signal handling
		self.dialog.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP, self.targets, gtk.gdk.ACTION_COPY)
		self.dialog.connect('drag_data_received', self.handle_data)

		screen = self.dialog.get_screen()
		rgba = screen.get_rgba_colormap()

		# setup painting of transparent background
		self.dialog.set_app_paintable(True)
		self.dialog.set_colormap(rgba)
		self.dialog.connect('expose-event', self.expose)

		# setup click to move of the drop window
		self.dialog.add_events(gtk.gdk.BUTTON_PRESS_MASK)
		self.dialog.connect('button-press-event', self.clicked)

		self.dialog.show()
		
		# Using the screen of the Window, the monitor it's on can be identified
		monitor = screen.get_monitor_at_window(screen.get_active_window())
		monitor = screen.get_monitor_geometry(monitor)

		# setup the position
		dropzone = self.app._cfg.get('dropzone')

		if dropzone == 'custom':
			self.dialog.move(self.app._cfg.get('x'), self.app._cfg.get('y'))
		elif dropzone == 'tl':
			# top left
			self.dialog.move(0, 0)
		elif dropzone == 'tm':
			# top middle
			self.dialog.move((monitor.width / 2) - 30, 0)
		elif dropzone == 'tr':
			# top right
			self.dialog.move(monitor.width - 30, 0)
		elif dropzone == 'ml':
			# middle left
			self.dialog.move(0, (monitor.height / 2) -30)
		elif dropzone == 'mr':
			# middle right
			self.dialog.move(monitor.width - 30, (monitor.height / 2) -30)
		elif dropzone == 'bl':
			# bottom left
			self.dialog.move(0, monitor.height -30)
		elif dropzone == 'bm':
			# bottom middle
			self.dialog.move((monitor.width / 2) - 30, monitor.height -30)
		elif dropzone == 'br':
			# bottom right
			self.dialog.move(monitor.width - 30, monitor.height -30)

		# ugly timeout to connect to movement signal after initial movement
		gobject.timeout_add(100, self.timeout)
		

	def timeout(self):
		self.dialog.connect('configure-event', self.moved)

	def show(self):
		gtk.main()

	def hide(self):
		self.dialog.destroy()

	def exit(self, widget, data=None):
		self.dialog.destroy()
		gtk.main_quit()
		sys.exit()

	def expose(self, widget, event):
		cr = widget.window.cairo_create()

		# Sets the operator to clear which deletes everything below where an object is drawn
		cr.set_operator(cairo.OPERATOR_CLEAR)
		# Makes the mask fill the entire window
		cr.rectangle(0.0, 0.0, *widget.get_size())
		# Deletes everything in the window (since the compositing operator is clear and mask fills the entire window
		cr.fill()
		# Set the compositing operator back to the default
		cr.set_operator(cairo.OPERATOR_OVER)

		# setup for drawing rounded rectangle
		x,y = (5, 5)
		w,h = widget.get_size()
		w -= 10
		h -= 10
		radius = 4
		degrees = pi / 180
		
		# draw filled rounded rectangle adapted from http://cairographics.org/samples/rounded_rectangle/
		cr.set_source_rgba(0.27,0.26,0.24,0.75)
		cr.arc(x + w - radius, y + radius, radius, -90 * degrees, 0 * degrees)
		cr.arc(x + w - radius, y + h - radius, radius, 0 * degrees, 90 * degrees)
		cr.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)  # ;o)
		cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
		cr.close_path()
		cr.fill()

		# draw outline
		cr.set_source_rgba(0.49,0.49,0.46,0.8)
		cr.set_line_width(0.3)
		cr.arc(x + w - radius, y + radius, radius, -90 * degrees, 0 * degrees)
		cr.arc(x + w - radius, y + h - radius, radius, 0 * degrees, 90 * degrees)
		cr.arc(x + radius, y + h - radius, radius, 90 * degrees, 180 * degrees)  # ;o)
		cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
		cr.close_path()
		cr.stroke()


	def clicked(self, widget, event):
		# enable moving of window on click
		self.dialog.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

	def moved(self, widget, event):
		# save custom position to config 
		x,y = widget.get_position()
		self.app._cfg.set('dropzone', 'custom')
		self.app._cfg.set('x', x)
		self.app._cfg.set('y', y)
		self.app._cfg.save()
		

	# from django https://code.djangoproject.com/browser/django/trunk/django/core/validators.py#L47
	def is_valid_url(self, url):
	    regex = re.compile(
	        r'^https?://'  # http:// or https://
	        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
	        r'localhost|'  # localhost...
	        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
	        r'(?::\d+)?'  # optional port
	        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	    return url is not None and regex.search(url)


	def handle_data(self, widget, context, x, y, selection, targetType, time):
	    if targetType == self.TARGET_TYPE_TEXT:
	    	if self.is_valid_url(selection.data):
	    		# create link
	    		link = selection.data
	        	self.app.dew.create_link_and_notify(link)
	        else:
	        	text = selection.data.strip()
	        	url = urlparse(text)
	        	if url.scheme == 'file':
	        		# upload file
	        		filename = urllib.url2pathname(text)[7:]
	        		self.app.dew.upload_file_and_notify(filename)
	        	else:
	        		# create note
	        		self.app.dew.create_note_and_notify(text)

	    elif targetType == self.TARGET_TYPE_JPG or targetType == self.TARGET_TYPE_PNG or targetType == self.TARGET_TYPE_GIF:
	    	self.handle_image(targetType, selection.data)

	def handle_image(self, targetType, data):
		filename = "/tmp/droplr"
		if targetType == self.TARGET_TYPE_JPG:
			filename += ".jpg"
		elif targetType == self.TARGET_TYPE_PNG:
			filename += ".png"
		elif targetType == self.TARGET_TYPE_GIF:
			filename += ".gif"
		temp_file = open(filename, 'wb')
		temp_file.write(data)
		temp_file.close()
		self.app.dew.upload_file_and_notify(filename)

