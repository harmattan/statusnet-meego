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
from PySide.QtCore import QCoreApplication
from PySide.QtGui import QDesktopServices
from eventfeed import EventFeedService, EventFeedItem
import sys, datetime, pprint, os, os.path, urllib2, gconf


class StatusNetHandler():


	def __init__(self):
		self.app = QCoreApplication(sys.argv)

		# Get user details
		self.client = gconf.client_get_default()
		self.username = self.client.get_string('/apps/ControlPanel/Statusnet/username')
		self.password= self.client.get_string('/apps/ControlPanel/Statusnet/password')
		self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
		self.latest = self.client.get_int('/apps/ControlPanel/Statusnet/latest')
		if not self.username or not self.password:
			return
		if not self.api_path:
			self.api_path = "https://identi.ca/api"
		if self.api_path[:4] != "http":
			self.api_path = "http://" + self.api_path

		self.cacheDir = QDesktopServices.storageLocation(QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		self.eventService = EventFeedService('statusnet', 'StatusNet')
		print self.eventService.local_name
		self.eventService.add_refresh_action()
		try:
			self.statusNet = StatusNet(self.api_path, self.username, self.password)
		except Exception, (errmsg):
			sys.exit("ERROR: Couldn't establish connection: %s" % (errmsg))
		self.updateTimeline()


	def updateTimeline(self):
		self.latest = 0
		statuses = self.statusNet.statuses_home_timeline(self.latest)
		for status in statuses:
			self.showStatus(status)
		if len(statuses) > 0:
			self.client.set_int('/apps/ControlPanel/Statusnet/latest', statuses[0]['id'])


	def showStatus(self, status):
		icon = self.getAvatar(status['user']['profile_image_url'])
		title = "%s on StatusNet" % status['user']['name']
		item = EventFeedItem(icon, title, datetime.datetime.strptime(status['created_at'], "%a %b %d %H:%M:%S +0000 %Y"))
		item.set_body(status['text'])
		item.set_url(self.api_path.replace("/api", "/notice") + "/" + str(status['id']))
		self.eventService.add_item(item)


	def getAvatar(self, url):
		filename = url.split("/")[-1]
		imagePath = os.path.join(self.cacheDir, filename)
		if not os.path.exists(imagePath):
			try:
				out = open(imagePath, 'wb')
				out.write(urllib2.urlopen(url).read())
				out.close()
			except Exception, (err):
				print err
				return "/home/developer/MyDocs/src/statusnet/images/statusnet.png"
		return imagePath

	
if __name__ == "__main__":
	StatusNetHandler()
