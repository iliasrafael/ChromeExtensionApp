from pprint import pprint

def dict_generator(indict, pre=None):
	pre = pre[:] if pre else []
	if isinstance(indict, dict):
		for key, value in indict.items():
			if isinstance(value, dict):
				for d in dict_generator(value, pre + [key]):
					yield d
			elif isinstance(value, list) or isinstance(value, tuple):
				for v in value:
					for d in dict_generator(v, pre + [key]):
						yield d
			else:
				yield pre + [key, value]
	else:
		yield indict

report = ""

def isURL(s):
	if s.startswith("http://") or s.startswith("https://"):
		return s
	if s[::-1].startswith("http://") or s[::-1].startswith("https://"):
		return s[::-1]

	return ""

def check_url(url):
	global report

	#u = urlparse(url)
	spl = url.split('/')
	u = ''.join(spl[2])
	with open("blacklist.txt") as f:
		for line in f:
			if line.strip() == u:
				#report += u+" -- "+line
				return True
	return False

def check_js(tree):
	global report

	CallExpression = []
	callees = []
	extension_tab = False
	remove_tab = False
	listener = False
	security_option = False
	http_header = False
	remove_security = False

	l = dict_generator(tree)
	for i in l:
		for j in i:
			#URL:
			url = isURL(str(j).strip())
			if url != "":
				report += url+"\n"
				if check_url(url):
					report += "Blacklisted URL: "+url+"\n"
					#report += report+"\n"
					#report = ""

		k = [str(item).lower() for item in i]

		update_calls(i, callees, CallExpression)
		if i.count("CallExpression") > 0:
			if callees:
				CallExpression.append(callees)
				callees = []
		elif i.count("chrome://chrome/extensions/") > 0 or i.count("chrome://chrome/extensions") > 0 or i.count("chrome://extensions/") > 0 or i.count("chrome://extensions") > 0:
			extension_tab = True
		elif k.count("x-frame-options") > 0 or k.count("frame-options") > 0 or k.count("content-security-policy") > 0 or k.count("x-content-security-policy") > 0 or k.count("x-webkit-csp") > 0:
			security_option = True

	if callees:
		CallExpression.append(callees)
		callees = []

	report += str(CallExpression)+"\n"
	while CallExpression:
		callees = CallExpression.pop()
		if callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("onUpdated") > 0 and callees.count("addListener") > 0:
			listener = True
		elif callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("remove") > 0:
			remove_tab = True
		elif callees.count("chrome") > 0 and callees.count("webRequest") > 0 and callees.count("onHeadersReceived") > 0 and callees.count("addListener") > 0:
			http_header = True
		elif callees.count("splice") > 0:
			remove_security = True

	if listener and remove_tab and extension_tab:
		report += "Warning! Extension tab blocked."+"\n"

	if http_header and remove_security and security_option:
		report += "Warning! Security options are changed."+"\n"

def update_calls(i, callees, CallExpression):
	
	#Uninstallation and HTTP response header security options:
	
	if i.count("callee") > 0 and (i.count("name") > 0 or i.count("value") > 0):
		if i.count("addListener") > 0:
			callees.append("addListener")
		elif i.count("onUpdated") > 0:
			callees.append("onUpdated")
		elif i.count("tabs") > 0:
			callees.append("tabs")
		elif i.count("chrome") > 0:
			callees.append("chrome")
		elif i.count("remove") > 0:
			callees.append("remove")
		elif i.count("onHeadersReceived") > 0:
			callees.append("onHeadersReceived")
		elif i.count("webRequest") > 0:
			callees.append("webRequest")
		elif i.count("splice") > 0:
			callees.append("splice")

	

def Main():
	from pyjsparser.parser import PyJsParser

	f = open("input1.txt", 'rb')
	x = f.read()
	f.close()

	p = PyJsParser()
	tree = p.parse(x)

	check_js(tree)

	print report

if __name__ == '__main__':
	Main()