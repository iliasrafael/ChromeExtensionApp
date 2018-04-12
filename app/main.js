var port = null;

var getKeys = function(obj){
   var keys = [];
   for(var key in obj){
      keys.push(key);
   }
   return keys;
}


function appendMessage(text) {
  document.getElementById('response').innerHTML += "<p>" + text + "</p>";
}

function updateUiState() {
  if (port) {
    document.getElementById('connect-button').style.display = 'none';
    //document.getElementById('input-text').style.display = 'block';
    document.getElementById('send-message-button').style.display = 'block';
  } else {
    document.getElementById('connect-button').style.display = 'block';
    //document.getElementById('input-text').style.display = 'none';
    document.getElementById('send-message-button').style.display = 'none';
  }
}

function sendNativeMessage() {
  //message = {"text": document.getElementById('input-text').value};
  //var url;
  chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
    var x = tabs[0].url;
    message = {"text": x};
    if (x.startsWith("https://chrome.google.com/webstore/detail")) {
      port.postMessage(x);
      appendMessage("Run analysis for extension: <b>" + JSON.stringify(x.split("/")[5]) + "</b>");
    } else {
      appendMessage("You have to select a chrome extension from webstore.");
    }
    updateUiState();
  });
  
  
}

function onNativeMessage(message) {
  appendMessage("Received message: <b>" + JSON.stringify(message) + "</b>");
}

function onDisconnected() {
  appendMessage("Failed to connect: " + chrome.runtime.lastError.message);
  port = null;
  updateUiState();
}

function connect() {
  var hostName = "com.google.chrome.app";
  appendMessage("Connecting to native messaging host.")
  port = chrome.runtime.connectNative(hostName);
  port.onMessage.addListener(onNativeMessage);
  port.onDisconnect.addListener(onDisconnected);
  //sendNativeMessage();
  updateUiState();
}

document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('connect-button').addEventListener(
      'click', connect);
  document.getElementById('send-message-button').addEventListener(
      'click', sendNativeMessage);
  updateUiState();
});
