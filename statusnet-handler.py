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
import sys, datetime, pprint, os, os.path, urllib2, gconf


class StatusNetHandler():


	def __init__(self):
		self.app = QCoreApplication(sys.argv)

		self.client = gconf.client_get_default()
		self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
		self.latest = self.client.get_int('/apps/ControlPanel/Statusnet/latest')
		if not self.api_path:
			return
		if self.api_path in oauth_consumer_keys:
			print "Using oauth"
			key = oauth_consumer_keys[self.api_path]
			secret = oauth_consumer_secrets[self.api_path]
			oauth_token = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token")
			oauth_token_secret = self.client.get_string("/apps/ControlPanel/Statusnet/oauth_token_secret")
			self.statusNet = StatusNet(self.api_path, auth_type="oauth", consumer_key=key, consumer_secret=secret, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)
		else:
			print "Using basic auth"
			self.username = self.client.get_string('/apps/ControlPanel/Statusnet/username')
			self.password= self.client.get_string('/apps/ControlPanel/Statusnet/password')
			self.statusNet = StatusNet(self.api_path, self.username, self.password)

		self.cacheDir = QDesktopServices.storageLocation(QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		self.eventService = EventFeedService('statusnet', 'StatusNet')
		self.eventService.add_refresh_action()
		self.updateTimeline()


	def updateTimeline(self):
		statuses = self.statusNet.statuses_home_timeline(self.latest)
		for status in statuses:
			self.showStatus(status)
		if len(statuses) > 0:
			self.client.set_int('/apps/ControlPanel/Statusnet/latest', statuses[0]['id'])


	def showStatus(self, status):
		icon = statusnetutils.getAvatar(status['user']['profile_image_url'], self.cacheDir)
		title = "%s on StatusNet" % status['user']['name']
		# Strip out offset
		timestr = status['created_at'][:-10] + status['created_at'][-4:]
		offset = status['created_at'][-10:-5]
		creationtime = datetime.datetime.strptime(timestr, "%a %b %d %H:%M:%S %Y")
		tz = TimeZone()
		tz.setOffsetStr(offset)
		creationtime.replace(tzinfo=tz)
		item = EventFeedItem(icon, title, creationtime)
		item.set_body(status['text'])
		item.set_url(self.api_path.replace("/api", "/notice") + "/" + str(status['id']))
		self.eventService.add_item(item)


class TimeZone(datetime.tzinfo):


	def setOffsetStr(self, offset):
		hours = int(offset[:3])
		minutes = int(offset[3:5])
		self.offset = datetime.timedelta(hours=hours, minutes=minutes)


	def utcoffset(self, dt):
		return self.offset




if __name__ == "__main__":
	StatusNetHandler()
