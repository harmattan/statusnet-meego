import QtQuick 1.1;
import QtWebKit 1.0;
import com.nokia.meego 1.0;

Page {
	id: oauthPage;
	anchors.margins: rootWin.pageMargin;

	Column {
		spacing: 10;
		anchors.centerIn: parent;
		anchors.verticalCenterOffset: 20;
		width: 440;
		height: 800;

		WebView {
			id: oauthWebView;
			settings.javascriptEnabled: true;
			width: parent.width;
			height: parent.height - 135;
			html: "<html><body bgcolor='#000000'></body></html>";
		}

		Button {
			id: doneButton;
			text: "Done";
			onClicked: {
				rootWin.oauthDone()
			}
			width: parent.width;
		}
	}
}
