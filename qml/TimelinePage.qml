import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: timelinePage;
	anchors.margins: rootWin.pageMargin;

	ListView {
		id: timelineView
		height: parent.height - 128;
		width: parent.width;
		model: timelineModel;
		delegate: statusDelegate;
	}

	Component {
		id: statusDelegate;

		Item {
			height: statusDelegateTitle.height + statusDelegateText.height;
			width: timelineView.width;

			Image {
				id: statusDelegateAvatar;
				anchors.left: parent.left;
				source: model.avatar;
			}

			Label {
				id: statusDelegateTitle;
				width: parent.width - statusDelegateAvatar.width;
				font.bold: true;
				anchors.top: statusDelegateAvatar.top;
				anchors.left: statusDelegateAvatar.right;
				text: model.title;
			}

			Label {
				id: statusDelegateText;
				width: parent.width - statusDelegateAvatar.width;
				anchors.top: statusDelegateTitle.bottom;
				anchors.left: statusDelegateAvatar.right;
				text: model.text;
			}
		}
	}

}
