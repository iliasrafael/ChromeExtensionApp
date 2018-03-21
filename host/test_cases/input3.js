chrome.webRequest.onBeforeRequest.addListener(
	function(details) {
		var url = details.url;
		for(var i = 0; i < ibneler.length; i++) {
			if(url.indexOf(ibneler.length[i]) > -1) {
				return {
					cancel: true
				};
			}
		}
	}, {
		urls: ["<all_urls>"]
	}, ["blocking"]);