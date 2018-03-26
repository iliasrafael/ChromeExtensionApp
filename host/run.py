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
		return "reversed"

	return ""

def check_url(url):
	global report

	#u = urlparse(url)
	spl = url.split('/')
	u = ''.join(spl[2])
	with open("blacklist.txt") as f:
		for line in f:
			if line.strip() == u:
				#print u+" -- "+line
				return True
	return False

def update_calls(i, callees, CallExpression):
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
		elif i.count("install") >0:
			callees.append("install")
		elif i.count("webstore") >0:
			callees.append("webstore")
		elif i.count("query") >0:
			callees.append("query")

	
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
	install_extension = False
	DoS = False

	l = dict_generator(tree)

	for i in l:
		#print str(i)
		for j in i:
			#URL:
			url = isURL(str(j).strip())
			if url != "":
				#report += url+"\n"
				if url == "reversed":
					report += "Wanring! URL reversed.\n"
					url = str(j).strip()[::-1]
				if check_url(url):
					report += "Wanring! Blacklisted URL: "+url+"\n"
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

	print str(CallExpression)
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
		elif callees.count("chrome") > 0 and callees.count("webstore") > 0 and callees.count("install") > 0:
			install_extension = True
		elif callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("query") > 0:
			DoS = True

	#Uninstallation prevention
	if listener and remove_tab and extension_tab:
		print "Warning! Extension tab blocked."
	# HTTP response header security options
	if http_header and remove_security and security_option:
		print "Warning! Security options are changed."
	#Extension installation
	if install_extension:
		print "Warning! Extension installation."
	#DoS
	if DoS and remove_tab:
		print "Warning! DoS detected."


def Main():
	from pyjsparser.parser import PyJsParser

	f = open("input7.txt", 'rb')
	x = f.read()
	f.close()

	p = PyJsParser()
	tree = p.parse(x)

	#check_js(tree)
	for i in dict_generator(tree):
		print str(i)

	#print report

if __name__ == '__main__':
	Main()