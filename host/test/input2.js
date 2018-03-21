chrome["webRequest"]["onHeadersReceived"]["addListener"](function(e) {
	var t = e["responseHeaders"];
	for(var n = t["length"]-1; n>=0; --n) {
		var r = t[n]["name"]["toLowerCase"]();
		if(r == "X-frame-options" || r == "Frame-options" || r == "Content-security-policy" || r == "X-content-security-policy" || r == "X-webkit-csp") {
			t["splice"](n, 1);
		}
	}
	return {
		responseHeaders: t
	}
}, {
	urls: ["*://*/*"]
}, ["blocking", responseHeaders]);