#include "StatusNetSyncFWPlugin.h"
#include <libsyncpluginmgr/PluginCbInterface.h>
#include <LogMacros.h>
#include <QTimer>
#include <QDateTime>
#include <QMap>
#include <QUrl>
#include <meventfeed.h> 

extern "C" StatusNetSyncFWPlugin* createPlugin(const QString& aPluginName, 
		const Buteo::SyncProfile& aProfile,
		Buteo::PluginCbInterface *aCbInterface) {
	 return new StatusNetSyncFWPlugin(aPluginName, aProfile, aCbInterface);
}

extern "C" void destroyPlugin(StatusNetSyncFWPlugin*aClient) {
	 delete aClient;
}

StatusNetSyncFWPlugin::StatusNetSyncFWPlugin(const QString& aPluginName, 
					 const Buteo::SyncProfile& aProfile,
					 Buteo::PluginCbInterface *aCbInterface) :
					 ClientPlugin(aPluginName, aProfile, aCbInterface) {
	FUNCTION_CALL_TRACE;
}

StatusNetSyncFWPlugin::~StatusNetSyncFWPlugin() {
		  FUNCTION_CALL_TRACE;
}

bool StatusNetSyncFWPlugin::init() {
	 FUNCTION_CALL_TRACE;

	//The sync profiles can have some specific key/value pairs this info
	//can be accessed by this method.
	iProperties = iProfile.allNonStorageKeys();

	//return false - if error 
	//syncfw will call this method first if the plugin is able to initialize properly 
	//and its ready for sync it should return 'true' in case of any error return false.
	return true;
}

bool StatusNetSyncFWPlugin::uninit() {
	FUNCTION_CALL_TRACE;
	// called before unloading the plugin , the plugin should clean up 
	return true;
}

bool StatusNetSyncFWPlugin::startSync() {
	FUNCTION_CALL_TRACE;

	// This method is called after init(), the plugin is expected to return 
	// either true or false based on if the sync was started successfully or 
	// it failed for some reason
	//call appropriate slots based on the status of operation success/failed...
	//updateFeed Its just a helper function. 
	QTimer::singleShot(60000, this, SLOT(updateFeed()));
	
	return true;
}

void StatusNetSyncFWPlugin::abortSync(Sync::SyncStatus aStatus) {
	FUNCTION_CALL_TRACE;
	Q_UNUSED(aStatus);
	// This method is called if used cancels the 
	// sync in between , with the applet use case 
	// it should not ideally happen as there is no UI
	// in case of device sync and accounts sync we have 
	// a cancel button 
}

bool StatusNetSyncFWPlugin::cleanUp() {
	FUNCTION_CALL_TRACE;

	// this method is called in case of account being deleted
	// or the profile being deleted from UI in case of applet
	// it will not be called ....need to check as if there 
	// can be any use case for this
	return true;
}

Buteo::SyncResults StatusNetSyncFWPlugin::getSyncResults() const {
		  FUNCTION_CALL_TRACE;
		  return iResults;
}

void StatusNetSyncFWPlugin::connectivityStateChanged(Sync::ConnectivityType aType,
					 bool aState) {
	FUNCTION_CALL_TRACE;
	// This function notifies of the plugin of any connectivity related state changes
	LOG_DEBUG("Received connectivity change event:" << aType << " changed to " << aState);
	if ((aType == Sync::CONNECTIVITY_INTERNET) && (aState == false)) {
		 // Network disconnect!!
	}
}

void StatusNetSyncFWPlugin::syncSuccess() {
	FUNCTION_CALL_TRACE;
	updateResults(Buteo::SyncResults(QDateTime::currentDateTime(), Buteo::SyncResults::SYNC_RESULT_SUCCESS, Buteo::SyncResults::NO_ERROR));
	//Notify Sync FW of result - Now sync fw will call uninit and then will unload plugin
	emit success(getProfileName(), "Success!!");
}

void StatusNetSyncFWPlugin::syncFailed() {
	FUNCTION_CALL_TRACE;
	//Notify Sync FW of result - Now sync fw will call uninit and then will unload plugin
	updateResults(Buteo::SyncResults(QDateTime::currentDateTime(),
					  Buteo::SyncResults::SYNC_RESULT_FAILED, Buteo::SyncResults::ABORTED));
	emit error(getProfileName(), "Error!!", Buteo::SyncResults::SYNC_RESULT_FAILED);
}

void StatusNetSyncFWPlugin::updateResults(const Buteo::SyncResults &aResults) {
	FUNCTION_CALL_TRACE;
	iResults = aResults;
	iResults.setScheduled(true);
}

void StatusNetSyncFWPlugin::updateFeed() {
	FUNCTION_CALL_TRACE;
	bool success = false;

	FILE* output = popen("/usr/share/statusnet/statusnet-hander.py", "r");
	success = true;
	pclose(output);
	
	if(success)
		syncSuccess();
	else
		syncFailed();	 
}
