import QtQuick 1.1;
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;

	Component.onCompleted: {
		theme.inverted = true;
	}

	signal send(string message);
	signal selectMessage(int statusid);

	function showMessage(title, message) {
		messageDialog.titleText = title;
		messageDialog.message = message;
		messageDialog.open();
	}

	function clearStatus() {
		status.text = "";
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

		Row {
			anchors.centerIn: parent;
			width: parent.width - 20;
			spacing: 10;

			TextField {
				id: status;
				objectName: "status";
				width: parent.width - sendIcon.width - parent.spacing;
				placeholderText: "Update your status...";
				visible: true;
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

	}

	QueryDialog {
		id: messageDialog;
		acceptButtonText: "Okay";
	}
}
