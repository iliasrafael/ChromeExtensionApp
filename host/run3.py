#!/usr/bin/env python

from esprima import esprima
from HTMLParser import HTMLParser

import sys
import os, shutil
from os import walk

reload(sys)
sys.setdefaultencoding('utf-8')
sys.setrecursionlimit(10000)

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
		if indict == None:
			yield []
		else:
			yield indict

report = ""

#Static analysis functions:
#URL:
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

call_list = ["addListener", "onUpdated", "onCreated", "onBeforeRequest", "tabs", "chrome", "remove", "onHeadersReceived", "webRequest", "splice", "install", "management", "uninstall", "webstore", "query", "system", "cpu", "display", "sessions", "getDevices", "XMLHttpRequest", "send"]

dec_list = ["document", "forms"]

elem_list = ["blocking"]

key_list = ["cancel", "redirectUrl"]

#Check for specific calls, variables, elements and keys
def update_calls(i, callees, decs, elems, keys):

	if i.count("callee") > 0 and (i.count("name") > 0 or i.count("value") > 0):
		for c in call_list:
			if i.count(c) > 0:
				callees.append(c)

	elif i.count("declarations") > 0 and (i.count("name") > 0 or i.count("value") > 0):
		for d in dec_list:
			if i.count(d) > 0:
				decs.append(d)

	elif i.count("elements") > 0 and (i.count("name") > 0 or i.count("value") > 0):
		for e in elem_list:
			if i.count(e) > 0:
				elems.append(e)

	elif i.count("key") > 0 and (i.count("name") > 0 or i.count("value") > 0):
		for k in key_list:
			if i.count(k) > 0:
				keys.append(k)

def check_js(tree):
	global report

	CallExpression = []
	depth = 0
	scope = 0

	callees = []
	Vars = []
	decs = []
	elems = []
	keys = []

	extension_tab = False
	remove_tab = -1
	tab_listener = -1
	web_listener = False
	security_option = False
	http_header = -1
	remove_security = -1
	install_extension = False
	uninstall_extension = False
	DoS = -1
	cpu = False
	displays = False
	sessions = False
	forms = False
	XMLHttpRequest = -1
	send = -1
	redirect = False
	cancel = False
	block = False

	l = dict_generator(tree)
	for i in l:
		#print i
		
		for j in i:
			#URL:
			url = isURL(str(j).strip())
			if url != "":
				#print url+"\n"
				if url == "reversed":
					print "Wanring! URL reversed.\n"
					url = str(j).strip()[::-1]
				if check_url(url):
					print "Wanring! Blacklisted URL: "+url+"\n"
					#print report+"\n"
					#report = ""

		k = [str(item).lower() for item in i]

		update_calls(i, callees, decs, elems, keys)

		#Update scope and depth
		if i.count("CallExpression") > 0:
			if depth > i.count("expression"):
				scope += 1
			depth = i.count("expression")

		#Gather call expressions
		if i.count("ExpressionStatement") > 0:
			if callees:
				temp = [callees, scope]
				CallExpression.append(temp)
				callees = []

		#Gather variable declarations
		elif i.count("VariableDeclarator") > 0:
			if decs:
				Vars.append(decs)
				decs = []

		#Check for extension tab
		elif i.count("chrome://chrome/extensions/") > 0 or i.count("chrome://chrome/extensions") > 0 or i.count("chrome://extensions/") > 0 or i.count("chrome://extensions") > 0:
			extension_tab = True

		#Check for security options
		elif k.count("x-frame-options") > 0 or k.count("frame-options") > 0 or k.count("content-security-policy") > 0 or k.count("x-content-security-policy") > 0 or k.count("x-webkit-csp") > 0:
			security_option = True	

	if callees:
		temp = [callees, scope]
		CallExpression.append(temp)
		callees = []

	#print CallExpression
	while CallExpression:
		callees = CallExpression.pop()

		# chrome.tabs.onUpdated.addListener / chrome.tabs.onCreated.addListener
		if callees[0].count("chrome") > 0 and callees[0].count("tabs") > 0 and (callees[0].count("onUpdated") > 0 or callees[0].count("onCreated") > 0) and callees[0].count("addListener") > 0:
			tab_listener = callees[1]

		# chrome.webRequest.onBeforeRequest.addListener
		elif callees[0].count("chrome") > 0 and callees[0].count("webRequest") > 0 and callees[0].count("onBeforeRequest") > 0 and callees[0].count("addListener") > 0:
			web_listener = True

		#chrome.tabs.remove
		elif callees[0].count("chrome") > 0 and callees[0].count("tabs") > 0 and callees[0].count("remove") > 0:
			remove_tab = callees[1]

		#chrome.webRequest.onHeadersReceived.addListener
		elif callees[0].count("chrome") > 0 and callees[0].count("webRequest") > 0 and callees[0].count("onHeadersReceived") > 0 and callees[0].count("addListener") > 0:
			http_header = callees[1]

		#responseHeaders.splice
		elif callees[0].count("splice") > 0:
			remove_security = callees[1]

		#chrome.webstore.install
		elif callees[0].count("chrome") > 0 and callees[0].count("webstore") > 0 and callees[0].count("install") > 0:
			install_extension = True

		#chrome.management.uninstall
		elif callees[0].count("chrome") > 0 and callees[0].count("management") > 0 and callees[0].count("uninstall") > 0:
			uninstall_extension = True

		#chrome.tabs.query
		elif callees[0].count("chrome") > 0 and callees[0].count("tabs") > 0 and callees[0].count("query") > 0:
			DoS = callees[1]

		#chrome.system.cpu
		elif callees[0].count("chrome") > 0 and callees[0].count("system") > 0 and callees[0].count("cpu") > 0:
			cpu = True

		#chrome.system.display
		elif callees[0].count("chrome") > 0 and callees[0].count("system") > 0 and callees[0].count("display") > 0:
			displays = True

		#chrome.sessions.getDevices
		elif callees[0].count("chrome") > 0 and callees[0].count("sessions") > 0 and callees[0].count("getDevices") > 0:
			sessions = True

		#new XMLHttpRequest
		elif callees[0].count("XMLHttpRequest") > 0:
			XMLHttpRequest = callees[1]

		#XMLHttpRequest.send
		elif callees[0].count("send") > 0:
			send = callees[1]

	while Vars:
		decs = Vars.pop()

		#document.forms
		if decs.count("document") > 0 and decs.count("forms") > 0:
			forms = True

	for el in elems:
		#["blocking"]
		if el == "blocking":
			block = True

	for k in keys:
		if k == "redirectUrl":
			redirect = True
		elif k == "cancel":
			cancel = True

	#Uninstallation prevention
	if (tab_listener == remove_tab != -1) and extension_tab:
		print "Warning! Extension tab blocked."
	#HTTP response header security options
	if (http_header == remove_security != -1) and security_option:
		print "Warning! Security options are changed."
	#Extension installation
	if install_extension:
		print "Warning! Extension installation."
	#Extension uninstallation
	if uninstall_extension:
		print "Warning! Extension uninstallation."
	#DoS
	if DoS == remove_tab != -1:
		print "Warning! DoS detected."
	#User's CPU info
	if cpu:
		print "Warning! User's info monitoring detected (cpu)."
	#User's number of displays
	if displays:
		print "Warning! User's info monitoring detected (displays)."
	#User's sessions info
	if sessions:
		print "Warning! User's info monitoring detected (sessions)."
	#Form submit requests
	if forms and (XMLHttpRequest == send != -1):
		print "Warning! Form submit requests leak."
	#Access to websites blocked
	if web_listener and cancel and block:
		print "Warning! Access to websites blocked."
	#URL MITM
	if web_listener and redirect and block:
		print "Warning! URL redirection (MITM)."


class MyHTMLParser(HTMLParser):
	isScript = False
	def handle_starttag(self, tag, attrs):
		global report
		
		if tag == "script":
			self.isScript = True
			#print "Start tag: "+tag
		#if attrs != None:
		for attr in attrs:
			if attr[1] != None:
				url = isURL(attr[1].strip())
				if url != "":
					if check_url(url):
						print "Blacklisted URL: "+url

	def handle_endtag(self, tag):
		
		if tag == "script":
			self.isScript = False

	def handle_data(self, data):
		
		global report
		if self.isScript:
			#print data
			parser = esprima
			tree = parser.parseScript(data, tolerant=True).toDict()

			check_js(tree)
			#print report





def Main():
	#List all .js files
	global report
	js = []
	html = []
	for (dirpath, dirnames, filenames) in walk('test'):
		for filename in filenames:
			if filename[-3:] == '.js':
				path = dirpath+"/"+filename
				js.append(path)
			elif filename[-5:] == '.html':
				path = dirpath+"/"+filename
				html.append(path)

	try:
		parser = esprima
		for jsfile in js:
			print "Parsing file "+jsfile+" ..."
			with open(jsfile, 'r') as readfile:
				data = readfile.read().decode('utf-8')
			tree = parser.parseScript(data, tolerant=True).toDict()
			#print tree
			check_js(tree)
			#print report

			report = ""
			print "File "+jsfile+" parsed successfully.\n"

		parser2 = MyHTMLParser()
		for htmlfile in html:
			print "Parsing file "+htmlfile+" ..."
			with open(htmlfile, 'r') as readfile:
				data = readfile.read().decode('utf-8')
			tree = parser2.feed(data)

			print "File "+htmlfile+" parsed successfully.\n"
			#result = tree.to_ecma()
			
			#print report
			report = ""

	except Exception, e:
		print e
	

if __name__ == '__main__':
	Main()