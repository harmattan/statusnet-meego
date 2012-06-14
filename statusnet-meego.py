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
import dbus, dbus.service, dbus.mainloop, dbus.glib
import sys, datetime, os, os.path, urllib2, gconf, signal, threading
import subprocess


class Signals(QtCore.QObject):


	onAddStatus = QtCore.Signal(list, QtCore.QAbstractListModel, bool)
	onDoneWorking = QtCore.Signal()
	onDoneSending = QtCore.Signal()
	onDoneMessage = QtCore.Signal(str, str, bool)
	onDoneFavourite = QtCore.Signal(int, bool)
	onUpdateFollowing = QtCore.Signal(int, bool)
	onError = QtCore.Signal(str, str)


	def __init__(self, parent=None):
		super(Signals, self).__init__(parent)


class StatusNetMeego(dbus.service.Object):


	def __init__(self):
		self.app = QtGui.QApplication(sys.argv)
		self.app.setApplicationName("StatusNet")
		signal.signal(signal.SIGINT, signal.SIG_DFL)

		self.signals = Signals()

		self.statuses = {}
		self.favourites = {}
		self.replyingTo = None

		self.client = gconf.client_get_default()
		self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
		if not self.api_path:
			ret = subprocess.call(["/usr/bin/invoker", "--type=e", "-s", "/opt/statusnet-meego/statusnet-login.py"])
			if ret == 2:
				self.api_path = self.client.get_string('/apps/ControlPanel/Statusnet/api_path')
			else:
				# Quit if the user just closed the configuration applet without setting up login details
				return

		self.login()

		self.cacheDir = QtGui.QDesktopServices.storageLocation(QtGui.QDesktopServices.CacheLocation)
		if not os.path.exists(self.cacheDir):
			os.mkdir(self.cacheDir)
		self.timelineModel = TimelineModel()
		self.signals.onAddStatus.connect(self.addStatus)
		self.signals.onDoneWorking.connect(self.doneWorking)
		self.signals.onDoneSending.connect(self.doneSending)
		self.signals.onDoneMessage.connect(self.doneMessage)
		self.signals.onDoneFavourite.connect(self.doneFavourite)
		self.signals.onUpdateFollowing.connect(self.updateFollowing)
		self.signals.onError.connect(self.error)
		self.view = QtDeclarative.QDeclarativeView()
		self.view.setSource("/opt/statusnet-meego/qml/Main.qml")
		self.rootObject = self.view.rootObject()
		self.context = self.view.rootContext()
		self.context.setContextProperty('timelineModel', self.timelineModel)
		self.rootObject.openFile("TimelinePage.qml")
		self.rootObject.send.connect(self.send)
		self.rootObject.back.connect(self.back)
		self.rootObject.refresh.connect(self.updateTimeline)
		self.rootObject.fetchMore.connect(self.fetchMore)
		self.rootObject.selectMessage.connect(self.showStatus)
		self.rootObject.linkClicked.connect(self.openLink)
		self.rootObject.favourite.connect(self.favourite)
		self.rootObject.unfavourite.connect(self.unfavourite)
		self.rootObject.follow.connect(self.follow)
		self.rootObject.unfollow.connect(self.unfollow)
		self.rootObject.repeat.connect(self.repeat)
		self.view.showFullScreen()
		self.latest = -1
		self.earliest = None
		self.updateTimeline()
		# Update every 10 minutes
		timer = QtCore.QTimer(self.signals)
		timer.timeout.connect(self.updateTimeline)
		timer.start(600000)
		dbus_main_loop = dbus.glib.DBusGMainLoop(set_as_default=True)
		session_bus = dbus.SessionBus(dbus_main_loop)
		bus_name = dbus.service.BusName("com.mikeasoft.statusnet.eventcallback", bus=session_bus)
	        dbus.service.Object.__init__(self, object_path="/EventFeedService", bus_name=bus_name)

		sys.exit(self.app.exec_())


	def login(self):
		try:
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
		except:
			ret = subprocess.call(["/usr/bin/invoker", "--type=e", "-s", "/opt/statusnet-meego/statusnet-login.py"])
			if ret == 2:
				self.login()
			else:
				return


	def updateTimeline(self):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._updateTimeline)
		thread.start()


	def _updateTimeline(self):
		statuses = self.statusNet.statuses_home_timeline(self.latest)
		if len(statuses) > 0:
			self.latest = statuses[0]['id']
			if self.earliest == None or self.earliest > statuses[-1]['id']:
				self.earliest = statuses[-1]['id']
			statuses.reverse()
			for status in statuses:
				self.signals.onAddStatus.emit(status, self.timelineModel, False)
		self.signals.onDoneWorking.emit()


	def fetchMore(self):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._fetchMore)
		thread.start()


	def _fetchMore(self):
		statuses = self.statusNet.statuses_home_timeline(max_id=self.earliest-1, count=20)
		if len(statuses) > 0:
			if self.earliest == None or self.earliest > statuses[-1]['id']:
				self.earliest = statuses[-1]['id']
			for status in statuses:
				self.signals.onAddStatus.emit(status, self.timelineModel, True)
		self.signals.onDoneWorking.emit()


	def doneWorking(self):
		self.rootObject.stopWorking()


	def addStatus(self, status, model, addToEnd=False):
		self.statuses[status['id']] = status
		icon = statusnetutils.getAvatar(status['user']['profile_image_url'], self.cacheDir)
		creationtime = statusnetutils.getTime(status['created_at'])
		html = status['statusnet_html'].replace("<a ", "<a style='color: #a0a0a0;' ")
		html = html.replace("&quot;", '"')
		status = Status(status['user']['name'], html, icon, status['id'], status['statusnet_conversation_id'], creationtime.strftime("%c"), status['favorited'], status['user']['following'], status['user']['id'])
		if addToEnd:
			model.addToEnd(status)
		else:
			model.add(status)


	def showStatus(self, statusid, conversationid):
		self.rootObject.startWorking()
		self.replyingTo = statusid
		self.conversation = conversationid
		try:
			status = self.statuses[statusid]
		except:
			status = self.statusNet.statuses_show(statusid)
		self.rootObject.setStatusPlaceholder("Reply to %s..." % status['user']['name'])
		conversationModel = TimelineModel()
		self.context.setContextProperty('timelineModel', conversationModel)
		thread = threading.Thread(target=self._showStatus, args=(status, conversationid, conversationModel))
		thread.start()


	def _showStatus(self, status, conversationid, conversationModel):
		conversation = self.statusNet.statusnet_conversation(conversationid)
		for status in conversation:
			self.signals.onAddStatus.emit(status, conversationModel, False)
		self.signals.onDoneWorking.emit()

	
	def back(self):
		self.replyingTo = None
		self.conversation = None
		self.rootObject.setStatusPlaceholder("Update your status...")
		self.context.setContextProperty('timelineModel', self.timelineModel)


	def send(self, status):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._send, args=(status.encode("utf-8"),))
		thread.start()


	def _send(self, status):
		try:
			if self.replyingTo:
				self.statusNet.statuses_update(status, in_reply_to_status_id=self.replyingTo)
			else:
				self.statusNet.statuses_update(status)
			self.signals.onDoneSending.emit()
		except Exception, err:
			self.signals.onError.emit("Problem sending message", err.message)
			self.signals.onDoneWorking.emit()


	def doneSending(self):
		if self.replyingTo:
			self.showStatus(self.replyingTo, self.conversation)
		else:
			self.updateTimeline()
		self.rootObject.clearStatus()


	def error(self, title, message):
		self.rootObject.showMessage(title, message)


	def openLink(self, link):
		QtGui.QDesktopServices.openUrl(link)


	def favourite(self, statusid):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._favourite, args=(statusid,))
		thread.start()


	def _favourite(self, statusid):
		try:
			self.statusNet.favorites_create(statusid)
			self.signals.onDoneFavourite.emit(statusid, True)
		except Exception, err:
			self.signals.onError.emit("Problem adding favourite", err.message)
			self.signals.onDoneWorking.emit()


	def doneFavourite(self, statusid, favourite):
		idx = self.timelineModel.getIndex(statusid)
		self.timelineModel.setData(idx, favourite, self.timelineModel.FAVOURITE_ROLE)
		self.signals.onDoneWorking.emit()


	def follow(self, userid, username):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._follow, args=(userid, username))
		thread.start()


	def _follow(self, userid, username):
		try:
			self.statusNet.friendships_create(userid)
			self.signals.onDoneMessage.emit("Following new user", "You've started following %s." % username, False)
			self.signals.onUpdateFollowing.emit(userid, True)
		except Exception, err:
			self.signals.onError.emit("Problem following user", err.message)
			self.signals.onDoneWorking.emit()


	def unfollow(self, userid, username):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._unfollow, args=(userid, username))
		thread.start()


	def _unfollow(self, userid, username):
		try:
			self.statusNet.friendships_destroy(userid)
			self.signals.onDoneMessage.emit("Stopped following user", "You've stopped following %s." % username, False)
			self.signals.onUpdateFollowing.emit(userid, False)
		except Exception, err:
			self.signals.onError.emit("Problem stopping following user", err.message)
			self.signals.onDoneWorking.emit()


	def updateFollowing(self, userid, following):
		self.timelineModel.updateFollowing(userid, following)


	def doneMessage(self, title, message, update):
		if update:
			self.updateTimeline()
		else:
			self.signals.onDoneWorking.emit()
		self.rootObject.showMessage(title, message)


	def unfavourite(self, statusid):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._unfavourite, args=(statusid,))
		thread.start()


	def _unfavourite(self, statusid):
		try:
			self.statusNet.favorites_destroy(statusid)
			self.signals.onDoneFavourite.emit(statusid, False)
		except Exception, err:
			self.signals.onError.emit("Problem removing favourite", err.message)
			self.signals.onDoneWorking.emit()


	def repeat(self, statusid):
		self.rootObject.startWorking()
		thread = threading.Thread(target=self._repeat, args=(statusid,))
		thread.start()


	def _repeat(self, statusid):
		try:
			self.statusNet.statuses_retweet(statusid)
			self.signals.onDoneMessage.emit("Message repeated", "The selected message was repeated successfully.", True)
		except Exception, err:
			self.signals.onError.emit("Problem repeating message", err.message)
			self.signals.onDoneWorking.emit()


	@dbus.service.method("com.mikeasoft.statusnet.eventcallback")
	def ReceiveActionData(self, statusid, conversationid):
		self.rootObject.showBack()
		self.view.activateWindow()
		self.view.raise_()
		self.showStatus(int(statusid), int(conversationid))


class Status(QtCore.QObject):


	def __init__(self, title, text, avatar, statusid, conversationid, time, favourite, following, userid):
		self.title = title
		self.text = text
		self.avatar = avatar
		self.statusid = statusid
		self.conversationid = conversationid
		self.time = time
		self.favourite = favourite
		self.following = following
		self.userid = userid


class TimelineModel(QtCore.QAbstractListModel):


	TITLE_ROLE = QtCore.Qt.UserRole + 1
	TEXT_ROLE = QtCore.Qt.UserRole + 2
	AVATAR_ROLE = QtCore.Qt.UserRole + 3
	ID_ROLE = QtCore.Qt.UserRole + 4
	CID_ROLE = QtCore.Qt.UserRole + 5
	TIME_ROLE = QtCore.Qt.UserRole + 6
	FAVOURITE_ROLE = QtCore.Qt.UserRole + 7
	FOLLOWING_ROLE = QtCore.Qt.UserRole + 8
	USERID_ROLE = QtCore.Qt.UserRole + 9


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
		keys[TimelineModel.FAVOURITE_ROLE] = 'favourite'
		keys[TimelineModel.FOLLOWING_ROLE] = 'following'
		keys[TimelineModel.USERID_ROLE] = 'userid'
		self.setRoleNames(keys)


	def rowCount(self, index):
		return len(self._data)


	def data(self, index, role):
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
		elif role == TimelineModel.FAVOURITE_ROLE:
			return status.favourite
		elif role == TimelineModel.FOLLOWING_ROLE:
			return status.following
		elif role == TimelineModel.USERID_ROLE:
			return status.userid
		else:
			return None


	def add(self, status):
		self.beginInsertRows(QtCore.QModelIndex(), 0, 0) #notify view about upcoming change        
		self._data.insert(0, status)
		self.endInsertRows() #notify view that change happened


	def addToEnd(self, status):
		count = len(self._data)
		self.beginInsertRows(QtCore.QModelIndex(), count, count)
		self._data.insert(count, status)
		self.endInsertRows()


	def getIndex(self, statusid):
		for status in self._data:
			if status.statusid == statusid:
				return self._data.index(status)

		return None


	def updateFollowing(self, userid, following):
		for status in self._data:
			if status.userid == userid:
				idx = self._data.index(status)
				self.setData(idx, following, TimelineModel.FOLLOWING_ROLE)


	def setData(self, index, value, role):
		# dataChanged signal isn't obeyed by ListView (QTBUG-13664)
		# so work around it by removing then re-adding rows
		self.beginRemoveRows(QtCore.QModelIndex(), index, index)
		status = self._data.pop(index)
		self.endRemoveRows()
		self.beginInsertRows(QtCore.QModelIndex(), index, index)
		if role == TimelineModel.FAVOURITE_ROLE:
			status.favourite = value
		elif role == TimelineModel.FOLLOWING_ROLE:
			status.following = value
		self._data.insert(index, status)
		self.endInsertRows()


if __name__ == "__main__":
	StatusNetMeego()
