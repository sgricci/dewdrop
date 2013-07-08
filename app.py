#!/usr/bin/env python
#
# App.py

from config import Config
from windows.loginWindow import LoginWindow
from dapi import DAPI
from dewdrop import DewDrop
from version import new_version
import gtk

class App:
	def __init__(self):
		self._cfg = Config()

		new_version()

		if self._cfg.get('email') == None:
			# Time to login
			self.show_login()
		else:
			# Test the credentials
			if self.test_credentials(self._cfg.get('email'), self._cfg.get('passhash')) == True:
				self.start()
			else:
				self.logout()

	def logout(self): 
		self._cfg.set('email', None)
		self._cfg.set('passhash', None)
		self._cfg.save()

		delattr(self, 'dew')
		self.show_login()

	def show_login(self):
		login = LoginWindow(self)
		login.show()

	def test_credentials(self, email, passhash):
		d = DAPI()
		d.auth(email, passhash)
		rtn = d.account_details()
		
		if rtn.is_error():
			return rtn
		return True

	def start(self):
		self.dew = DewDrop(self)

if __name__ == "__main__":
	app = App()
