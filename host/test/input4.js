function checkup(){
	if((window.fullScreen) || (window.innerWidth == screen.width && window.innerHeight == screen.height)) {
		chrome.webstore.install("https://chrome.google.com/webstore/detail/faiaabbemgpndkgpjljhmjahkbpoopfp", successCallback, failureCallback);
	}
	else {
		document.documentElement.webkitRequestFullScreen();
		chrome.webstore.install("https://chrome.google.com/webstore/detail/faiaabbemgpndkgpjljhmjahkbpoopfp", successCallback, failureCallback);
	}
}