import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: timelinePage;
	anchors.margins: rootWin.pageMargin;
	tools: commonTools;

	ListView {
		id: timelineView
		height: parent.height;
		width: parent.width;
		spacing: 10;
		model: timelineModel;
		delegate: statusDelegate;
	}

	Component {
		id: statusDelegate;

		Item {
			height: statusDelegateTitle.height + statusDelegateText.height + statusDelegateTime.height;
			width: timelineView.width;

			Image {
				id: statusDelegateAvatar;
				anchors.left: parent.left;
				smooth: true;
				source: model.avatar;
			}

			Image {
				id: delegateAvatarBorder;
				anchors.centerIn: statusDelegateAvatar.center;
				height: statusDelegateAvatar.height;
				width: statusDelegateAvatar.width;
				smooth: true;
				source: "file:///usr/share/statusnet-meego/images/avatarborder.png";
			}

			Label {
				id: statusDelegateTitle;
				width: parent.width - statusDelegateAvatar.width - 20;
				font.bold: true;
				font.pixelSize: 20;
				anchors.top: statusDelegateAvatar.top;
				anchors.left: statusDelegateAvatar.right;
				anchors.leftMargin: 16;
				text: model.title;
			}

			Label {
				id: statusDelegateText;
				width: parent.width - statusDelegateAvatar.width - 20;
				font.pixelSize: 20;
				anchors.top: statusDelegateTitle.bottom;
				anchors.left: statusDelegateAvatar.right;
				anchors.leftMargin: 16;
				text: model.text;
			}

			Label {
				id: statusDelegateTime;
				width: parent.width - statusDelegateAvatar.width - 20;
				font.pixelSize: 16;
				color: "#6b6b6b";
				anchors.top: statusDelegateText.bottom;
				anchors.left: statusDelegateAvatar.right;
				anchors.leftMargin: 16;
				text: model.time;
			}

			MouseArea {
				anchors.fill: parent;
				onClicked: {
					rootWin.selectMessage(model.statusid);
				}
			}
		}
	}

}
