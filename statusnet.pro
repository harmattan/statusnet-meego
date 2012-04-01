TEMPLATE = lib
TARGET = statusnet-client
DEPENDPATH += . 
INCLUDEPATH += .  \
	 /usr/include/libsynccommon \
	 /usr/include/libsyncprofile \
	 /usr/include/meegotouchevents 

LIBS += -lsyncpluginmgr -lsyncprofile

CONFIG += debug plugin meegotouchevents meegotouch

QT += dbus network gui

#input
HEADERS += \
	syncfw-plugin/StatusNetSyncFWPlugin.h 
SOURCES += \
	syncfw-plugin/StatusNetSyncFWPlugin.cpp 

QMAKE_CXXFLAGS = -Wall \
	-g \
	-Wno-cast-align \
	-O2 -finline-functions 

#install
target.path = /usr/lib/sync/ 

client.path = /etc/sync/profiles/client 
client.files = syncfw-plugin/xml/statusnet.xml

sync.path = /etc/sync/profiles/sync
sync.files = syncfw-plugin/xml/sync/*

service.path = /etc/sync/profiles/service
service.files = syncfw-plugin/xml/service/*

duidesktop.path = /usr/share/duicontrolpanel/desktops/
duidesktop.files = duicontrolpanel/desktop/*

duiuidesc.path = /usr/share/duicontrolpanel/uidescriptions/
duiuidesc.files = duicontrolpanel/uidescriptions/*

statusnet.path = /usr/share/statusnet-meego/
statusnet.files = statusnet-handler.py

statusnetlib.path = /usr/share/statusnet-meego/statusnet/
statusnetlib.files = statusnet/*

oauthlib.path = /usr/share/statusnet-meego/oauth/
oauthlib.files = oauth/*

eventfeedlib.path = /usr/share/statusnet-meego/eventfeed/
eventfeedlib.files = eventfeed/*

images.path = /usr/share/statusnet-meego/images/
images.files = images/*

dbus.path = /usr/share/dbus-1/services/
dbus.files = dbus/*

INSTALLS += target client sync service duidesktop duiuidesc statusnet statusnetlib oauthlib eventfeedlib dbus
