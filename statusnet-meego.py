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
import sys, datetime, pprint, os, os.path, urllib2, gconf, signal, threading


class StatusNetMeego(QtCore.QObject):


	onAddStatus = QtCore.Signal(list, QtCore.QAbstractListModel)
	onDoneWorking = QtCore.Signal()


	def __init__(self, parent=None):
		super(StatusNetMeego, self).__init__(parent)
		self.app = QtGui.QApplication(sys.argv)
		self.app.setApplicationName("StatusNet")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.statuses = {}
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
			username = self.client.get_string('/apps/ControlPanel/Statusnet/username')
			password= self.client.get_string('/apps/ControlPanel/Statusnet/password')
			self.statusNet = StatusNet(self.api_path, username, password)

		self.cacheDir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		self.timelineModel = TimelineModel()
		self.onAddStatus.connect(self.addStatus)
		self.onDoneWorking.connect(self.doneWorking)
		self.view = QtDeclarative.QDeclarativeView()
		self.view.setSource("qml/Main.qml")
		self.rootObject = self.view.rootObject()
		self.context = self.view.rootContext()
		self.context.setContextProperty('timelineModel', self.timelineModel)
		self.rootObject.openFile("TimelinePage.qml")
		self.rootObject.send.connect(self.send)
		self.rootObject.back.connect(self.back)
		self.rootObject.refresh.connect(self.updateTimeline)
		self.rootObject.selectMessage.connect(self.showStatus)
		self.view.showFullScreen()
		self.latest = -1
		self.updateTimeline()
		# Update every 10 minutes
		timer = QtCore.QTimer(self)
		timer.timeout.connect(self.updateTimeline)
		timer.start(600000)
		sys.exit(self.app.exec_())


	def updateTimeline(self):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._updateTimeline)
		thread.start()


	def _updateTimeline(self):
		statuses = self.statusNet.statuses_home_timeline(self.latest)
		if len(statuses) > 0:
			self.latest = statuses[0]['id']
			statuses.reverse()
			for status in statuses:
				self.onAddStatus.emit(status, self.timelineModel)
		self.onDoneWorking.emit()


	def doneWorking(self):
		self.rootObject.stopWorking()


	def addStatus(self, status, model):
		self.statuses[status['id']] = status
		icon = statusnetutils.getAvatar(status['user']['profile_image_url'], self.cacheDir)
		creationtime = statusnetutils.getTime(status['created_at'])
		status = Status(status['user']['name'], status['text'], icon, status['id'], status['statusnet_conversation_id'], creationtime.strftime("%c"))
		model.add(status)


	def showStatus(self, statusid, conversationid):
		self.rootObject.startWorking()
		self.replyingTo = statusid
		self.conversation = conversationid
		status = self.statuses[statusid]
		self.rootObject.setStatusPlaceholder("Reply to %s..." % status['user']['name'])
		conversationModel = TimelineModel()
		self.context.setContextProperty('timelineModel', conversationModel)
		thread = threading.Thread(target=self._showStatus, args=(status,conversationid,conversationModel))
		thread.start()


	def _showStatus(self, status, conversationid, conversationModel):
		conversation = self.statusNet.statusnet_conversation(conversationid)
		for status in conversation:
			self.onAddStatus.emit(status, conversationModel)
		self.onDoneWorking.emit()

	
	def back(self):
		self.replyingTo = None
		self.conversation = None
		self.rootObject.setStatusPlaceholder("Update your status...")
		self.context.setContextProperty('timelineModel', self.timelineModel)


	def send(self, status):
		try:
			if self.replyingTo:
				self.statusNet.statuses_update(status, in_reply_to_status_id=self.replyingTo)
				self.showStatus(self.replyingTo, self.conversation)
			else:
				self.statusNet.statuses_update(status)
				self.updateTimeline()
			self.rootObject.clearStatus()
		except Exception, err:
			self.rootObject.showMessage("Problem sending message", err.message)



class Status(QtCore.QObject):


	def __init__(self, title, text, avatar, statusid, conversationid, time):
		self.title = title
		self.text = text
		self.avatar = avatar
		self.statusid = statusid
		self.conversationid = conversationid
		self.time = time


class TimelineModel(QtCore.QAbstractListModel):


	TITLE_ROLE = QtCore.Qt.UserRole + 1
	TEXT_ROLE = QtCore.Qt.UserRole + 2
	AVATAR_ROLE = QtCore.Qt.UserRole + 3
	ID_ROLE = QtCore.Qt.UserRole + 4
	CID_ROLE = QtCore.Qt.UserRole + 5
	TIME_ROLE = QtCore.Qt.UserRole + 6


	def __init__(self, parent=None):
		super(TimelineModel, self).__init__(parent)
		self._data = []
		keys = {}
		keys[TimelineModel.TITLE_ROLE] = 'title'
		keys[TimelineModel.TEXT_ROLE] = 'text'
		keys[TimelineModel.AVATAR_ROLE] = 'avatar'
		keys[TimelineModel.ID_ROLE] = 'statusid'
		keys[TimelineModel.CID_ROLE] = 'conversationid'
		keys[TimelineModel.TIME_ROLE] = 'time'
		self.setRoleNames(keys)


	def rowCount(self, index):
		return len(self._data)


	def data(self, index, role):
		 if not index.isValid():
			 return None

		 if index.row() > len(self._data):
			 return None

		 status = self._data[index.row()]

		 if role == TimelineModel.TITLE_ROLE:
			 return status.title
		 elif role == TimelineModel.TEXT_ROLE:
			 return status.text
		 elif role == TimelineModel.AVATAR_ROLE:
			 return status.avatar
		 elif role == TimelineModel.ID_ROLE:
			 return status.statusid
		 elif role == TimelineModel.CID_ROLE:
			 return status.conversationid
		 elif role == TimelineModel.TIME_ROLE:
			 return status.time
		 else:
			 return None


	def add(self, status):
		self.beginInsertRows(QtCore.QModelIndex(), 0, 0) #notify view about upcoming change        
		self._data.insert(0, status)
		self.endInsertRows() #notify view that change happened



if __name__ == "__main__":
	StatusNetMeego()
