TEMPLATE = lib
TARGET = statusnet-client
DEPENDPATH += . 
INCLUDEPATH += .  \
	 /usr/include/libsynccommon \
	 /usr/include/libsyncprofile \
	 /usr/include/meegotouchevents

LIBS += -lsyncpluginmgr -lsyncprofile

CONFIG += debug plugin meegotouchevents  

QT += dbus network
QT -= gui

#input
HEADERS += \
	StatusNetSyncFWPlugin.h 
SOURCES += \
	StatusNetSyncFWPlugin.cpp 

QMAKE_CXXFLAGS = -Wall \
	-g \
	-Wno-cast-align \
	-O2 -finline-functions 

#install
target.path = /usr/lib/sync/ 

client.path = /etc/sync/profiles/client 
client.files = xml/statusnet.xml

sync.path = /etc/sync/profiles/sync
sync.files = xml/sync/*

service.path = /etc/sync/profiles/service
service.files = xml/service/*

INSTALLS += target client sync service
