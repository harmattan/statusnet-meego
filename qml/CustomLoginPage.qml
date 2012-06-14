import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: customLoginPage;
	anchors.margins: rootWin.pageMargin;
	tools: commonTools;

	Component.onCompleted: {
		rootWin.showBack();
		username.text = rootWin.username;
		password.text = rootWin.password;
		customServer.text = rootWin.api_path;
	}

	Column {
		spacing: 40;
		anchors.centerIn: parent;
		width: 440;

		TextField {
			id: customServer;
			width: parent.width;
			placeholderText: "API URL for custom service";
		}

		TextField {
			id: username;
			width: parent.width;
			placeholderText: "Username";
		}

		TextField {
			id: password;
			width: parent.width;
			echoMode: TextInput.PasswordEchoOnEdit;
			placeholderText: "Password";
		}

		Button {
			id: loginButton;
			text: "Login";
			width: parent.width;
			onClicked: {
				rootWin.login(customServer.text, username.text, password.text);
			}
		}
	}
}
