import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: configPage;
	anchors.margins: rootWin.pageMargin;
	tools: commonTools;

	Column {
		spacing: 10;
		anchors.centerIn: parent;
		anchors.verticalCenterOffset: -40;
		width: 440;

		Label {
			width: parent.width;
			font.pixelSize: 20;
			text: "Which service would you like to connect to?";
			horizontalAlignment: Text.AlignHCenter;
		}

		Button {
			id: identicaButton;
			text: "Identi.ca";
			width: parent.width;
			onClicked: {
				rootWin.oauthLogin("https://identi.ca/api");
			}
		}

		Label {
			width: parent.width;
			font.pixelSize: 20;
			text: "Or";
			horizontalAlignment: Text.AlignHCenter;
		}

		Button {
			id: customLoginButton;
			text: "A custom server";
			width: parent.width;
			onClicked: {
				rootWin.openFile("CustomLoginPage.qml");
			}
		}
	}

	Column {
		spacing: 10;
		anchors.bottom: parent.bottom;
		anchors.horizontalCenter: parent.horizontalCenter;
		width: 440;
	
		Rectangle {
			width: parent.width - 40;
			anchors.horizontalCenter: parent.horizontalCenter;
			height: 3;
			gradient: Gradient {
				GradientStop { position: 0.0; color: "black" }
				GradientStop { position: 1.0; color: "gray" }
			}
			radius: 10;
		}

		Label {
			width: parent.width;
			font.pixelSize: 20;
			text: "Don't have an account?";
			horizontalAlignment: Text.AlignHCenter;
		}

		Button {
			id: registerButton;
			text: "Sign up with Identi.ca";
			width: parent.width;
			onClicked: {
				rootWin.register();
			}
		}

	}
}
