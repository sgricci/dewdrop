#!/usr/bin/env python

import simplejson as json
import os
import sys

class Config:
	def __init__(self):
		# Check if file exists
		path = os.path.expanduser("~/.dewdrop/")
		if not os.path.exists(path):
			# Create Path
			os.makedirs(path)

		self.path = ("%s%s" % (path, "config"))
		self.data = {}
		if os.path.exists(self.path):
			self.load()

	def load(self):
		f = file(self.path, 'r')
		data = f.read()
		f.close()
		self.data = json.loads(data)

	def set(self, name, val):
		self.data[name] = val;

	def get(self, name):
		if name in self.data:
			return self.data[name]
		return None

	def save(self):
		f = file(self.path, 'w')
		f.write(json.dumps(self.data))
		f.close()
