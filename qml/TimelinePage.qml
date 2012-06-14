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
		cacheBuffer: 100;
		footer: Rectangle { 
				id: fetchButton;
				width: parent.width;
				color: "#000";
				height: 64;
				visible: rootWin.showFetch;
				Label {
					text: "Fetch more...";
					anchors.centerIn: parent;
				}
				MouseArea {
					anchors.fill: parent;
					onClicked: {
						rootWin.fetchMore();
					}
				}
			}
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
				height: 48;
				width: 48;
			}

			Image {
				id: delegateAvatarBorder;
				anchors.centerIn: statusDelegateAvatar.center;
				height: statusDelegateAvatar.height;
				width: statusDelegateAvatar.width;
				smooth: true;
				source: "file:///opt/statusnet-meego/images/avatarborder.png";
			}

			Label {
				id: statusDelegateTitle;
				width: parent.width - statusDelegateAvatar.width - 20 - 32; 
				font.bold: true;
				font.pixelSize: 20;
				anchors.top: statusDelegateAvatar.top;
				anchors.left: statusDelegateAvatar.right;
				anchors.leftMargin: 16;
				text: model.title;
			}

			Image {
				id: statusDelegateFavourite;
				visible: model.favourite;
				anchors.left: statusDelegateTitle.right;
				anchors.top: statusDelegateTitle.top;
				source: "image://theme/icon-s-common-favorite-mark-inverse";
				smooth: true;
				height: 28;
				width: 28;
			}

			Label {
				id: statusDelegateText;
				width: parent.width - statusDelegateAvatar.width - 20;
				font.pixelSize: 20;
				anchors.top: statusDelegateTitle.bottom;
				anchors.left: statusDelegateAvatar.right;
				anchors.leftMargin: 16;
				text: model.text;
				onLinkActivated: {
					rootWin.linkClicked(link);
				}
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
				z: -1;
				onClicked: {
					rootWin.selectMessage(model.statusid, model.conversationid);
					rootWin.showBack();
				}
				onPressAndHold: {
					rootWin.currentStatus = model.statusid;
					rootWin.currentStatusFavourite = model.favourite;
					rootWin.currentStatusFollowing = model.following;
					rootWin.currentUsername = model.title;
					rootWin.currentUserId = model.userid;
					statusMenu.open();
				}
			}

		}

	}

	Menu {
		id: statusMenu
		anchors.bottomMargin: commonTools.height;
		content: MenuLayout {

			MenuItem {
				text: "Repeat this message"
				onClicked: rootWin.repeat(rootWin.currentStatus);
			}

			MenuItem {
				text: rootWin.currentStatusFavourite ? "Unfavourite this message" : "Favourite this message"
				onClicked: {
					if (rootWin.currentStatusFavourite) {
						rootWin.unfavourite(rootWin.currentStatus);
					} else {
						rootWin.favourite(rootWin.currentStatus);
					}
				}
			}

			MenuItem {
				text: rootWin.currentStatusFollowing ? "Unfollow this user" : "Follow this user"
				onClicked: {
					if (rootWin.currentStatusFollowing) {
						rootWin.unfollow(rootWin.currentUserId, rootWin.currentUsername);
					} else {
						rootWin.follow(rootWin.currentUserId, rootWin.currentUsername);
					}
				}
			}
		}
	}

}
