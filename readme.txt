
To install the extension you have to:
	-Go to chrome://extensions/ and check the box for Developer mode in the top right.
	-Click the Load unpacked extension button and select the (unzipped) folder of the extension.

To install the native messaging host (on Windows) you have to:
	-Run install_host.bat script in the host directory.
	-This script installs the native messaging host for the current user, by creating a registry key HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.google.chrome.app and setting its default value to the full path to host\com.google.chrome.app-win.json .
	If you want to install the native messaging host for all users, change HKCU to HKLM.
	-Note that you need to have python installed.

To install python module requests you have to run this command in your terminal: 
	pip install requests.
