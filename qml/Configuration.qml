import QtQuick 1.1
import com.nokia.meego 1.0

PageStackWindow {
	id: rootWin
	property int pageMargin: 16
	initialPage: ConfigPage { }

	function openFile(file) {
	var component = Qt.createComponent(file)
	if (component.status == Component.Ready)
		pageStack.push(component);
	else
		console.log("Error loading component:", component.errorString());
	}
}
