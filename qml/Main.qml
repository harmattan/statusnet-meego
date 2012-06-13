import QtQuick 1.1;
import Qt 4.7
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;
	property bool showFetch: true;
	property int currentMessage: -1;
	property bool currentMessageFavourite: false;

	Component.onCompleted: {
		theme.inverted = true;
	}

	signal back();
	signal refresh();
	signal fetchMore();
	signal send(string message);
	signal selectMessage(int statusid, int conversationid);
	signal linkClicked(string link);
	signal repeat(int statusid);
	signal favourite(int statusid);
	signal unfavourite(int statusid);

	function showMessage(title, message) {
		messageDialog.titleText = title;
		messageDialog.message = message;
		messageDialog.open();
	}

	function startWorking() {
		indicator.running = true;
		indicator.visible = true;
	}

	function stopWorking() {
		indicator.running = false;
		indicator.visible = false;
	}

	function clearStatus() {
		status.text = "";
	}

	function setStatusPlaceholder(placeholder) {
		status.placeholderText = placeholder;
	}

	function showBack() {
		backIcon.visible = true;
		menuIcon.visible = false;
		rootWin.showFetch = false;
	}

	function hideBack() {
		backIcon.visible = false;
		menuIcon.visible = true;
		rootWin.showFetch = true;
	}

	function openFile(file) {
		var component = Qt.createComponent(file);
		if (component.status == Component.Ready) {
			pageStack.push(component);
		} else {
			console.log("Error loading component:", component.errorString());
		}
	}

	BusyIndicator {
		id: indicator
		platformStyle: BusyIndicatorStyle { size: "large" }
		running:  false;
		anchors.centerIn: parent;
	}

	Menu {
		id: toolMenu
		content: MenuLayout {

			MenuItem {
				text: "Refresh"
				onClicked: rootWin.refresh();
			}

			MenuItem {
				text: "About"
				onClicked: rootWin.showMessage("StatusNet for MeeGo", "Author: Mike Sheldon (elleo@gnu.org)\n\nLicense: GPL 3.0 or later\n\nFeel free to follow me, @mikesheldon, on identi.ca if you think you need more friends :)")
			}

			MenuItem {
				text: "Privacy Policy"
				onClicked: rootWin.showMessage("Privacy Policy", "This application stores information required for authenticating with third party services (either in the form of a username and password, or an OAuth token). This information is only ever transmitted to the services you have authorised. The application also sends messages to users on these services (at your request), these messages are never stored permanently by the application and are only sent directly to the services you have authorised.");
			}
		}
	}

	ToolBarLayout {
		id: commonTools;
		visible: true;
	}

	/* Display row outside of toolbar, otherwise text input doesn't get pushed up when onscreen keyboard appears */
	Row {
		anchors.bottom: parent.bottom;
		anchors.margins: 10;
		width: parent.width - 20;
		x: 8;
		spacing: 10;

		Image {
			id: menuIcon
			height: status.height;
			fillMode: Image.PreserveAspectFit;
			smooth: true;
			source: "image://theme/icon-m-toolbar-view-menu-white";
			MouseArea {
				anchors.fill: parent;
				onClicked: toolMenu.open();
			}
		}
			
		Image {
			id: backIcon
			height: status.height;
			width: menuIcon.width;
			fillMode: Image.PreserveAspectFit;
			smooth: true;
			visible: false;
			source: "image://theme/icon-m-toolbar-back-white";
			MouseArea {
				anchors.fill: parent;
				onClicked: {
					rootWin.back();
					rootWin.hideBack();
				}
			}
		}

		TextField {
			id: status;
			objectName: "status";
			width: parent.width - sendIcon.width - menuIcon.width - parent.spacing - parent.spacing;
			placeholderText: "Update your status...";
			visible: true;

			Keys.onReturnPressed: {
				rootWin.send(status.text);
			}
		}

		Image {
			id: sendIcon;
			height: status.height;
			fillMode: Image.PreserveAspectFit;
			smooth: true;
			source: "image://theme/icon-m-content-sms-inverse";
			MouseArea {
				anchors.fill: parent;
				onClicked: {
					rootWin.send(status.text);
				}
			}
		}
	}


	QueryDialog {
		id: messageDialog;
		acceptButtonText: "Okay";
	}
}
