#!/usr/bin/env python
import gtk
import cairo
class Shot(gtk.Window):
	def __init__(self):
		super(Shot, self).__init__(gtk.WINDOW_POPUP)

		self.connect("destroy", gtk.main_quit)
		self.connect("button_press_event", self.button_press)
		self.connect("button_release_event", self.button_release)
		self.connect("motion_notify_event", self.motion_notify)
		self.connect("key_press_event", self.key_press)

		mask = gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_MOTION_MASK | gtk.gdk.KEY_PRESS_MASK
		self.set_events(mask)

		self.set_app_paintable(True)
		self.connect('expose-event', self.expose)
		screen = self.get_screen()
		rgba = screen.get_rgba_colormap()
		self.set_colormap(rgba)
		self.set_decorated(False)
		self.move(0,0)
		self.resize(screen.get_width(), screen.get_height())
		self.width = 1
		self.height = 1
		self.x = 0
		self.y = 0
		self.endX = 0
		self.endY = 0
		self.active = False
		self.fullscreen()
		self.set_keep_above(True)

	def expose(self, widget, event):
		cr = widget.window.cairo_create()
		cr.set_operator(cairo.OPERATOR_CLEAR)
		cr.rectangle(event.area)
		cr.fill()
		cr.set_operator(cairo.OPERATOR_OVER)
		try:
			widget.rgba
		except AttributeError:
			widget.rgba=(0.0,0.0,0.0,0.0)
		cr.set_source_rgba(*widget.rgba)
		cr.rectangle(event.area)
		cr.fill()  

	def key_press(self, widget, event):
		print event
		if event.keyval == 65307:
			gtk.main_quit()

	def motion_notify(self, widget, event):
		if not self.active:
			return False
		if event.x_root == self.x or event.y_root == self.y:
			return False

		self.width  = int(event.x_root)
		self.height = int(event.y_root)

		
		self.move(min(self.width, self.x), min(self.height, self.y))
		self.resize(abs(self.x - self.width), abs(self.y - self.height))
		self.queue_draw()
		return True

	def button_release(self, widget, event):
		self.rgba=(0.0,0.0,0.0,0.0)
		self.queue_draw()
		self.move(-10, -10)
		self.resize(10, 10)
		self.endX = event.x
		self.endY = event.y
		self.sX = int(min(self.x, self.width))
		self.sY = int(min(self.y, self.height))
		self.width  = int(abs(self.x - self.width))
		self.height = int(abs(self.y - self.height))
		self.ungrab()
		self.destroy()
		#self.set_cursor(None)
		gtk.main_quit()
	
	def grab(self):
		rootWindow = gtk.gdk.get_default_root_window()
		status = gtk.gdk.keyboard_grab(rootWindow, owner_events=True, time=0L)
		print status

	def ungrab(self):
		gtk.gdk.keyboard_ungrab()

	def button_press(self, widget, event):
		self.rgba=(0.5,0.5,1.0,0.2)
		self.active = True

		self.x = int(event.x)
		self.y = int(event.y)
		self.move(self.x, self.y)
		self.resize(1,1)
		self.queue_draw()
	

	def start(self):
		self.show_all()
		self.show()
		# Mouse and keyboard grab
		#self.grab()
		gtk.main()
		

if __name__ == "__main__":
	s = Shot()
	s.start()
	print s.endX, s.endY
