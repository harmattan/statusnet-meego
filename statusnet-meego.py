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

from statusnet import StatusNet
import statusnetutils
from oauthkeys import oauth_consumer_keys, oauth_consumer_secrets 
from PySide import QtCore, QtGui, QtDeclarative
import sys, datetime, pprint, os, os.path, urllib2, gconf, signal


class StatusNetMeego():


	def __init__(self):
		self.app = QtGui.QApplication(sys.argv)
		self.app.setApplicationName("StatusNet")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.client = gconf.client_get_default()
		self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
		if not self.api_path:
			import statusnetlogin
			statusnetlogin.StatusNetLogin()
		if self.api_path in oauth_consumer_keys:
			key = oauth_consumer_keys[self.api_path]
			secret = oauth_consumer_secrets[self.api_path]
			oauth_token = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token")
			oauth_token_secret = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token_secret")
			self.statusNet = StatusNet(self.api_path, auth_type="oauth", consumer_key=key, consumer_secret=secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
		else:
			self.username = self.client.get_string('/apps/ControlPanel/Statusnet/username')
			self.password= self.client.get_string('/apps/ControlPanel/Statusnet/password')
			self.statusNet = StatusNet(self.api_path, self.username, self.password)

		self.cacheDir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		self.view = QtDeclarative.QDeclarativeView()
		self.view.setSource("qml/Main.qml")
		self.rootObject = self.view.rootObject()
		self.rootObject.openFile("TimelinePage.qml")
		self.view.showFullScreen()
		print "Updating timeline..."
		self.updateTimeline()
		sys.exit(self.app.exec_())


	def updateTimeline(self):
		statuses = self.statusNet.statuses_home_timeline()
		for status in statuses:
			self.showStatus(status)


	def showStatus(self, status):
		icon = statusnetutils.getAvatar(status['user']['profile_image_url'], self.cacheDir)


if __name__ == "__main__":
	StatusNetMeego()
