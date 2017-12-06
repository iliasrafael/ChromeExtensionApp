chrome.runtime.onInstalled.addListener(function(){
	var xhttp = new XMLHttpRequest();
	xhttp.open("GET", "https://refraction.tech/calculator/newUser.php?info="+chrome.app.getDetails().id, true);
	xhttp.send();
})