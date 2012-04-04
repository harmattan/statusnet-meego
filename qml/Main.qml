import QtQuick 1.1;
import com.nokia.meego 1.0;

PageStackWindow {
	id: rootWin;
	property int pageMargin: 16;

	Component.onCompleted: {
		theme.inverted = true;
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
