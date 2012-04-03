import QtQuick 1.1;
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;
	property string username: "";
	property string password: "";
	property string api_path: "https://identi.ca/api";
	property string url: "";

	Component.onCompleted: {
		theme.inverted = true;
	}

	signal messageAccepted();
	signal login(string api_path, string username, string password);
	signal oauthLogin(string api_path);
	signal oauthDone(string verified);

	function setUsername(newUsername) {
		username = newUsername;
	}

	function setPassword(newPassword) {
		password = newPassword;
	}

	function setApiPath(newApiPath) {
		api_path = newApiPath;
	}

	function setURL(newURL) {
		url = newURL;
	}

	function showMessage(title, message) {
		messageDialog.titleText = title
		messageDialog.message = message
		messageDialog.open()		
	}

	function openFile(file) {
		var component = Qt.createComponent(file);
		if (component.status == Component.Ready) {
			pageStack.push(component);
		} else {
			console.log("Error loading component:", component.errorString());
		}
	}

	ToolBarLayout {
		id: commonTools;
		visible: false;
		ToolIcon { iconId: "toolbar-back"; onClicked: { pageStack.pop(); pause(); } }
	}

	QueryDialog {
		id: messageDialog;
		acceptButtonText: "Okay";
		onAccepted: {
			messageAccepted();
		}
	}
}
