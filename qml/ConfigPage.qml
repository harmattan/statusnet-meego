import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: configPage;
	anchors.margins: rootWin.pageMargin;

	Component.onCompleted: {
		if (rootWin.api_path == "https://identi.ca/api") {
			serverSelection.selectedIndex = 0;
		} else {
			serverSelection.selectedIndex = 1;
			customServer.text = rootWin.api_path;
			customServer.visible = true;
			username.visible = true;
			username.text = rootWin.username;
			password.visible = true;
			password.text = rootWin.password;
			loginButton.text = "Login";
		}
	}

	SelectionDialog {
		id: serverSelection;
		titleText: "StatusNet Service";
		selectedIndex: 0;

		model: ListModel {
			ListElement { name: "Identi.ca"; }
			ListElement { name: "Custom service"; }
		}

		onAccepted: {
			if (selectedIndex == 1) {
				customServer.visible = true;
				username.visible = true;
				password.visible = true;
				loginButton.text = "Login";
			} else {
				customServer.visible = false;
				username.visible = false;
				password.visible = false;
				loginButton.text = "Login via OAuth";
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

		TextField {
			id: customServer;
			width: parent.width;
			placeholderText: "API URL for custom service";
			visible: false;
		}

		TextField {
			id: username;
			width: parent.width;
			placeholderText: "Username";
			visible: false;
		}

		TextField {
			id: password;
			width: parent.width;
			echoMode: TextInput.PasswordEchoOnEdit;
			placeholderText: "Password";
			visible: false;
		}

		Button {
			id: loginButton;
			text: "Login via OAuth";
			width: parent.width;
			onClicked: {
				if (serverSelection.selectedIndex == 0) {
					rootWin.oauthLogin("https://identi.ca/api");
				} else if (serverSelection.selectedIndex == 1) {
					rootWin.login(customServer.text, username.text, password.text);
				}
			}
		}
	}
}
