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
	signal register();

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

	function showBack() {
		menuIcon.visible = false;
		backButton.visible = true;
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

	Menu {
		id: toolMenu
		content: MenuLayout {

			MenuItem {
				text: "About"
				onClicked: rootWin.showMessage("StatusNet for MeeGo", "Author: Mike Sheldon (elleo@gnu.org)\n\nLicense: GPL 3.0 or later\n\nFeel free to follow me, @mikesheldon, on identi.ca if you think you need more friends :)")
			}

			MenuItem {
				text: "Privacy Policy"
				onClicked: rootWin.showMessage("Privacy Policy", "This application stores information required for authenticating with third party services (either in the form of a username and password, or an OAuth token). This information is only ever transmitted to the services you have authorised. The application also sends messages to users on these services (at your request), these messages are never stored permanently by the application and are only sent directly to the services you have authorised.");																     }
		}
	}

	ToolBarLayout {
		id: commonTools;
		visible: true;
		ToolIcon {
			id: backButton;
			visible: false;
			iconId: "toolbar-back";
			onClicked: {
				pageStack.pop();
				backButton.visible = false;
				menuIcon.visible = true;
			}
		}

		Image {
			id: menuIcon
			height: status.height;
			fillMode: Image.PreserveAspectFit;
			smooth: true;
			source: "image://theme/icon-m-toolbar-view-menu-white";
			anchors.left: parent.left;
			anchors.leftMargin: 10;
			MouseArea {
				anchors.fill: parent;
				onClicked: toolMenu.open();
			}
		}
	}

	QueryDialog {
		id: messageDialog;
		acceptButtonText: "Okay";
		onAccepted: {
			messageAccepted();
		}
	}
}
