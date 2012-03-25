#ifndef STATUSNETSYNCFWPLUGIN_H
#define STATUSNETSYNCFWPLUGIN_H

#include <libsyncpluginmgr/ClientPlugin.h>
#include <libsyncprofile/SyncResults.h>

class StatusNetSyncFWPlugin : public Buteo::ClientPlugin
{
	Q_OBJECT;
public:
	StatusNetSyncFWPlugin(const QString& aPluginName,
			const Buteo::SyncProfile& aProfile,
			Buteo::PluginCbInterface *aCbInterface );

	virtual ~StatusNetSyncFWPlugin();
	virtual bool init();
	virtual bool uninit();
	virtual bool startSync();
	virtual void abortSync(Sync::SyncStatus aStatus = Sync::SYNC_ABORTED);
	virtual Buteo::SyncResults getSyncResults() const;
	virtual bool cleanUp();

public slots:
	virtual void connectivityStateChanged(Sync::ConnectivityType aType,
			bool aState);

protected slots:	  
	void syncSuccess();
	void syncFailed();
	void updateFeed();
private:
	void updateResults(const Buteo::SyncResults &aResults);
private:
	QMap<QString, QString>	iProperties;
	Buteo::SyncResults	iResults;
};

extern "C" StatusNetSyncFWPlugin* createPlugin(const QString& aPluginName,
		const Buteo::SyncProfile& aProfile,
		Buteo::PluginCbInterface *aCbInterface);

extern "C" void destroyPlugin(StatusNetSyncFWPlugin *aClient); 

#endif
