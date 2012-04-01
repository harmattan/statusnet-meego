import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: configPage;
	anchors.margins: rootWin.pageMargin;

	SelectionDialog {
		id: serverSelection;
		titleText: "StatusNet Service";
		selectedIndex: 0;

		model: ListModel {
			ListElement { name: "Identi.ca (with SSL)"; }
			ListElement { name: "Identi.ca (without SSL)"; }
			ListElement { name: "Custom service"; }
		}

		onAccepted: {
			if (selectedIndex == 2) {
				customServer.visible = true;
			} else {
				customServer.visible = false;
			}
		}

	}
	
	Column {
		spacing: 40;
		anchors.centerIn: parent;
		width: 440;

		Button {
			text: serverSelection.model.get(serverSelection.selectedIndex).name;
			width: parent.width;
			onClicked: {
				serverSelection.open();
			}
		}

		TextArea {
			id: customServer;
			width: parent.width;
			placeholderText: "API URL for custom service";
			visible: false;
		}

		Button {
			text: "Login";
			width: parent.width;
			onClicked: {
				if (serverSelection.selectedIndex == 0) {
					rootWin.login("https://identi.ca/api");
				} else if (serverSelection.selectedIndex == 1) {
					rootWin.login("http://identi.ca/api");
				} else if (serverSelection.selectedIndex == 2) {
					rootWin.login(customServer.text);
				}
				rootWin.openFile("OAuthPage.qml");
			}
		}
	}
}
