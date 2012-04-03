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

		Label {
			text: "Please enter the authorisation code provided in the browser window."
			width: parent.width;
		}

		TextField {
			id: verifier;
			placeholderText: "Authorisation code"
			width: parent.width;
		}

		Button {
			id: doneButton;
			text: "Done";
			onClicked: {
				rootWin.oauthDone(verifier.text)
			}
			width: parent.width;
		}
	}
}
