import QtQuick 1.1
import QtWebKit 1.0
import com.nokia.meego 1.0

Page {
	id: oauthPage
	anchors.margins: rootWin.pageMargin

	Column {
		spacing: 10
		anchors.centerIn: parent
		anchors.verticalCenterOffset: 40
		width: 480;

		WebView {
			id: oauthWebView;
			settings.javascriptEnabled: true;
			width: parent.width;
			height: 400;
		}
	
		Button {
			text: "Done";
			onClicked: {
				Qt.quit();
			}
			width: parent.width;
		}
	}
}
