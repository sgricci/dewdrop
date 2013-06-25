#!/usr/bin/env python
#
# libdroplr.py -- library for communicating with the Droplr HTTP API
#
# By Steve Gricci, Jan 2013, All rights reserved

import pycurl
import time
import locale
import StringIO
import hashlib
import hmac
import os
import base64
import urllib
import simplejson as json
import mimetypes

class Droplr:
	def __init__(self):
		self._public_key = '<public key here>'
		self._private_key = '<private key here>'
		self.server = '<server name here>'
		self.port = 8069
		self.scheme = 'http'

		self._version = '0.3'

		self.email = None
		self.passhash = None
		self.app_name = None
		self.app_version = None

	def set_authentication(self, email, passhash):
		self.email = email
		self.passhash = passhash

	def set_application_name(self, app_name):
		self.app_name = app_name

	def set_application_version(self, version):
		self.app_version = version

	def get_user_agent(self):
		if (self.app_name != None):
			return "".join(['libdroplr.py/', self._version, ' ', self.app_name, '/', self.app_version])
		return "".join(['libdroplr.py/',self._version])

	def header_date(self):
		locale.setlocale(locale.LC_NUMERIC, '')
		microtime = time.time() * 1000
		return locale.format("%.*f", (0, microtime), False, False)

	def create_request(self, method, uri, params, content_type, data):
		headers = {}
		headers['User-Agent'] = self.get_user_agent()
		headers['Date'] = self.header_date()
		if (content_type != None):
			headers['Content-Type'] = content_type

		return Droplr_Request(method, self.scheme, self.server, self.port, uri, params, headers, data)

	def account_details(self):
		request = self.create_request('GET', '/account', None, None, None)
		request = self.sign_request(request)

		return request.execute()

	def create_file(self, filename):
		content_type = mimetypes.guess_type(filename)[0]
		# read file contents
		f = file(filename, 'rb')
		data = f.read()
		f.close()

		request = self.create_request('POST', '/files', {'filename': base64.b64encode(os.path.basename(filename))}, content_type, data)
		request.headers['Content-Length'] = len(data)
		request = self.sign_request(request)
		return request.execute()


	def list_drops(self):
		request = self.create_request('GET', '/drops', None, None, None)
		request = self.sign_request(request)
		return request.execute()


	def sign_request(self, request):
		request.headers['Authorization'] = self.calculate_signature(request)
		return request

	def calculate_signature(self, request):
		access_key = self.access_key()
		access_secret = self.access_secret()
		string_to_sign = self.create_string_to_sign(request)
		signature = self.calculate_hmac(string_to_sign, access_secret)

		return "droplr %s:%s" % (access_key, signature)

	def access_key(self):
		return base64.b64encode("%s:%s" % (self._public_key, self.email))

	def access_secret(self):
		return "%s:%s" % (self._private_key, self.passhash)

	def create_string_to_sign(self, request):
		if 'Content-Type' in request.headers:
			contentType = request.headers['Content-Type']
		else:
			contentType = "";

		date = request.headers['Date']

		return "%s %s.json HTTP/1.1\n%s\n%s" % (request.method, request.uri, contentType, date)

	def calculate_hmac(self, string_to_sign, access_secret):
		hash = hmac.new(access_secret, string_to_sign, hashlib.sha1).digest()
		return base64.b64encode(hash)

class Droplr_Request:
	def __init__(self, method, scheme, host, port, uri, params, headers, data):
		self.method = method
		self.scheme = scheme
		self.host = host
		self.port = port
		self.uri = uri
		self.params = params
		self.headers = headers
		self.data = data

	def headersForCurl(self):
		headers = []
		for x in self.headers:
			str = ("%s: %s" % (x, self.headers[x]))
			headers.append(str)
		return headers

	def execute(self):
		c = pycurl.Curl()
		c.setopt(pycurl.URL, self.build_url())
		if (self.data != None):
			c.setopt(pycurl.POSTFIELDS, self.data)
		b = StringIO.StringIO()
		c.setopt(pycurl.HTTPHEADER, self.headersForCurl())
		c.setopt(pycurl.WRITEFUNCTION, b.write)
		c.setopt(pycurl.HEADER, True)
		c.setopt(pycurl.CUSTOMREQUEST, self.method)
		c.perform()
		val = b.getvalue()
		response = val.split("\r\n\r\n")
		if not response[1]:
			# Error has occured, do stuff
			headers = self.parse_headers(response[0])
			if 'x-droplr-errordetails' in headers:
				return Droplr_Error(headers)
		if response[1][:4] == 'HTTP':
			response[1] = response[2]
		return Droplr_Response(response[1])

	def parse_headers(self, resp):
		raw_headers = resp.split("\r\n")
		# Get http error code
		headers = {'http_status_code': raw_headers[0].split(" ")[1]}
		del raw_headers[0]
		for i in raw_headers:
			spl = i.split(":")
			headers[spl[0]] = spl[1].strip()
		return headers

	def build_url(self):
		if (self.params == None):
			query = ''
		else :
			query = ('?%s' % urllib.urlencode(self.params))
		return ("%s://%s:%d%s.json%s" % (self.scheme, self.host, self.port, self.uri, query))

	def toString(self):
		return ("Request{method='%s', url='%s'}" % (self.method, self.build_url()))

class Droplr_Response:
	def __init__(self, response):
		self.error = False
		self.message = json.loads(response)

	def get_message(self):
		return self.message

	def is_error(self):
		return self.error


class Droplr_Error(Droplr_Response):
	def __init__(self, headers):
		self.error = True
		self.message = headers['x-droplr-errordetails']
		self.code = headers['x-droplr-errorcode']
		self.status_code = headers['http_status_code']

	def get_message(self):
		return self.message

