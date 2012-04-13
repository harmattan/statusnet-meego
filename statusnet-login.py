#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Mike Sheldon <elleo@gnu.org>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys, gconf, signal
from PySide import QtCore, QtGui, QtDeclarative
from statusnet import StatusNet
from oauth import oauth
from oauthkeys import oauth_consumer_keys, oauth_consumer_secrets
import subprocess


class StatusNetLogin():


	def __init__(self):
		self.app = QtGui.QApplication(sys.argv)
		self.app.setApplicationName("StatusNet")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.client = gconf.client_get_default()
		self.view = QtDeclarative.QDeclarativeView()
		self.view.setSource("/opt/statusnet-meego/qml/Configuration.qml")
		self.rootObject = self.view.rootObject()
		self.rootObject.setApiPath(self.client.get_string("/apps/ControlPanel/Statusnet/api_path"))
		self.rootObject.setUsername(self.client.get_string("/apps/ControlPanel/Statusnet/username"))
		self.rootObject.setPassword(self.client.get_string("/apps/ControlPanel/Statusnet/password"))
		self.rootObject.openFile("ConfigPage.qml")
		self.rootObject.login.connect(self.login)
		self.rootObject.oauthLogin.connect(self.oauthLogin)
		self.rootObject.oauthDone.connect(self.oauthDone)
		self.view.showFullScreen()
		sys.exit(self.app.exec_())


	def login(self, api_path, username, password):
		if api_path[:4] != 'http':
			api_path = 'http://' + api_path
		self.api_path = api_path
		self.client.set_string("/apps/ControlPanel/Statusnet/api_path", api_path)
		try:
			self.statusNet = StatusNet(api_path, username, password)
			self.client.set_string("/apps/ControlPanel/Statusnet/username", username)
			self.client.set_string("/apps/ControlPanel/Statusnet/password", password)
			self.success()
		except Exception as e:
			self.rootObject.showMessage("Login failed", e.message)
	

	def oauthLogin(self, api_path):
		self.api_path = api_path
		self.client.set_string("/apps/ControlPanel/Statusnet/api_path", self.api_path)
		self.key = oauth_consumer_keys[self.api_path]
		self.secret = oauth_consumer_secrets[self.api_path]
		self.statusNet = StatusNet(self.api_path, use_auth=False, auth_type="oauth", consumer_key=self.key, consumer_secret=self.secret)
		self.statusNet.consumer = oauth.OAuthConsumer(str(self.key), str(self.secret))
		request_tokens_raw = self.statusNet.oauth_request_token()
		self.request_tokens = {}
		for item in request_tokens_raw.split("&"):
			key, value = item.split("=")
			self.request_tokens[key] = value
		request_token = self.request_tokens["oauth_token"]
		oauth_url = "%s/oauth/authorize?oauth_token=%s" % (self.api_path, request_token)
		QtGui.QDesktopServices.openUrl(oauth_url)
		self.rootObject.openFile("OAuthPage.qml")


	def oauthDone(self, verifier):
		access_tokens_raw = self.statusNet.oauth_access_token(self.request_tokens["oauth_token"], self.request_tokens["oauth_token_secret"], verifier)
		access_tokens = {}
		for item in access_tokens_raw.split("&"):
			key, value = item.split("=")
			access_tokens[key] = value
			
		self.statusNet.oauth_token = access_tokens['oauth_token']
		self.statusNet.oauth_token_secret = access_tokens['oauth_token_secret']
		try:
			self.statusNet.token = oauth.OAuthToken(str(self.statusNet.oauth_token), str(self.statusNet.oauth_token_secret))
			self.client.set_string("/apps/ControlPanel/Statusnet/oauth_token", self.statusNet.oauth_token)
			self.client.set_string("/apps/ControlPanel/Statusnet/oauth_token_secret", self.statusNet.oauth_token_secret)
			self.success()
		except:
			self.rootObject.showMessage("Login failed", e.message)
			self.rootObject.openFile("ConfigPage.qml")


	def success(self):
		self.rootObject.showMessage("Log in successful!", "If you've only just installed StatusNet for MeeGo you'll need to restart your phone before messages will start appearing in your events feed.")
		self.rootObject.messageAccepted.connect(self.confirmed)


	def confirmed(self):
		self.app.exit(2)


if __name__ == "__main__":
	StatusNetLogin()
