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
from oauthkeys import oauth_consumer_keys, oauth_consumer_secrets 
from PySide.QtCore import QCoreApplication
from PySide.QtGui import QDesktopServices
from eventfeed import EventFeedService, EventFeedItem
import statusnetutils
import dbus, dbus.service, dbus.mainloop, dbus.glib
import sys, datetime, os, os.path, urllib2, gconf, signal, threading


class StatusNetHandler(dbus.service.Object):


	def __init__(self):
		dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
		session_bus = dbus.SessionBus(dbus_main_loop)
		bus_name = dbus.service.BusName("com.mikeasoft.statusnet", bus=session_bus)
		dbus.service.Object.__init__(self, object_path="/synchronize", bus_name=bus_name)

		self.app = QCoreApplication(sys.argv)
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		self.client = gconf.client_get_default()
		self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
		self.latest = self.client.get_int('/apps/ControlPanel/Statusnet/latest')
		self.eventService = EventFeedService('statusnet', 'StatusNet')
		self.eventService.local_name = "com.mikeasoft.statusnet.eventcallback"
		self.eventService.DEFAULT_INTF = "com.mikeasoft.statusnet.eventcallback"
		if not self.api_path:
			return
		self.cacheDir = QDesktopServices.storageLocation(QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		sys.exit(self.app.exec_())


	def login(self):
		if self.api_path in oauth_consumer_keys:
			key = oauth_consumer_keys[self.api_path]
			secret = oauth_consumer_secrets[self.api_path]
			oauth_token = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token")
			oauth_token_secret = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token_secret")
			self.statusNet = StatusNet(self.api_path, auth_type="oauth", consumer_key=key, consumer_secret=secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
		else:
			username = self.client.get_string('/apps/ControlPanel/Statusnet/username')
			password = self.client.get_string('/apps/ControlPanel/Statusnet/password')
			self.statusNet = StatusNet(self.api_path, username, password)


	@dbus.service.method("com.mikeasoft.statusnet")
	def refresh(self):
		thread = threading.Thread(target=self.updateTimeline)
		thread.start()


	def updateTimeline(self):
		self.login()
		statuses = self.statusNet.statuses_home_timeline(self.latest)
		for status in statuses:
			self.showStatus(status)
		if len(statuses) > 0:
			self.client.set_int('/apps/ControlPanel/Statusnet/latest', statuses[0]['id'])
		self.app.exit()


	def showStatus(self, status):
		if status['text'] == None:
			# HTML only message
			return
		icon = statusnetutils.getAvatar(status['user']['profile_image_url'], self.cacheDir)
		title = "%s on StatusNet" % status['user']['name']
		creationtime = statusnetutils.getTime(status['created_at'])
		item = EventFeedItem(icon, title, creationtime)
		item.set_body(status['text'])
		item.set_action_data(status['id'], status['statusnet_conversation_id'])
		self.eventService.add_item(item)



if __name__ == "__main__":
	StatusNetHandler()
