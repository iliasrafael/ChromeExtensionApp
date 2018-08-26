chrome.webRequest.onBeforeRequest.addListener(function (details) {
    if (details.url == "https://file you want to replace.js") {
      return {
        redirectUrl: "https://www.replacement file.js"
      };
    }
}, {
    urls: ["https://URL YOU WANT TO MITM/"]
}, ["blocking"]);
