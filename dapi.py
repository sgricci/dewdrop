#!/usr/bin/env python

from libdroplr import Droplr, Droplr_Request
import version

class DAPI:
	def __init__(self):
		self.d = Droplr()
		self.d.set_application_name('DewDrop')
		self.d.set_application_version(version.get_version())

	def auth(self, email, passhash):
		self.d.set_authentication(email, passhash)

	def upload(self, filename):
		return self.d.create_file(filename)

	def note(self, text, content_type):
		return self.d.create_note(text, content_type)

	def link(self, link, privacy):
		return self.d.create_link(link, privacy)

	def drops(self):
		return self.d.list_drops()	

	def account_details(self):
		return self.d.account_details()
