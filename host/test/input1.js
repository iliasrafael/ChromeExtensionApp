chrome.tabs.onUpdated.addListener(
function(tabid, x, tab){
	if(tab.url == 'chrome://chrome/extensions' ||
	tab.url == 'opera://extensions' ||
	tab.url == 'chrome://extensions/') {
		chrome.tabs.remove(tab.id);
	}
} );