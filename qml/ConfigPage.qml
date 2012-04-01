import QtQuick 1.1
import com.nokia.meego 1.0

Page {
	id: configPage
	anchors.margins: rootWin.pageMargin

	Column {
		spacing: 10
		anchors.centerIn: parent
		anchors.verticalCenterOffset: 40
		width: 400
	
		Button {
			text: "Login"
			onClicked: {
				rootWin.openFile("OAuthPage.qml");
			}
			width: parent.width
		}
	}
}
