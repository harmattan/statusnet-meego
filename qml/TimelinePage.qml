import QtQuick 1.1;
import com.nokia.meego 1.0;

Page {
	id: timelinePage;
	anchors.margins: rootWin.pageMargin;

	Column {
		spacing: 40;
		anchors.centerIn: parent;
		width: 440;

		TextArea {
			id: username;
			width: parent.width;
			placeholderText: "Update your status...";
			visible: true;
		}

	}
}
