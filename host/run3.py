#!/usr/bin/env python

from pyjsparser.parser import PyJsParser
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
	callees = []
	Vars = []
	decs = []
	elems = []
	keys = []

	extension_tab = False
	remove_tab = False
	tab_listener = False
	web_listener = False
	security_option = False
	http_header = False
	remove_security = False
	install_extension = False
	uninstall_extension = False
	DoS = False
	cpu = False
	displays = False
	sessions = False
	forms = False
	XMLHttpRequest = False
	send = False
	redirect = False
	cancel = False
	block = False

	l = dict_generator(tree)
	for i in l:
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

		#Gather call expressions
		if i.count("CallExpression") > 0:
			if callees:
				CallExpression.append(callees)
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
		CallExpression.append(callees)
		callees = []

	while CallExpression:
		callees = CallExpression.pop()

		# chrome.tabs.onUpdated.addListener / chrome.tabs.onCreated.addListener
		if callees.count("chrome") > 0 and callees.count("tabs") > 0 and (callees.count("onUpdated") > 0 or callees.count("onCreated") > 0) and callees.count("addListener") > 0:
			tab_listener = True

		# chrome.webRequest.onBeforeRequest.addListener
		elif callees.count("chrome") > 0 and callees.count("webRequest") > 0 and callees.count("onBeforeRequest") > 0 and callees.count("addListener") > 0:
			web_listener = True

		#chrome.tabs.remove
		elif callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("remove") > 0:
			remove_tab = True

		#chrome.webRequest.onHeadersReceived.addListener
		elif callees.count("chrome") > 0 and callees.count("webRequest") > 0 and callees.count("onHeadersReceived") > 0 and callees.count("addListener") > 0:
			http_header = True

		#responseHeaders.splice
		elif callees.count("splice") > 0:
			remove_security = True

		#chrome.webstore.install
		elif callees.count("chrome") > 0 and callees.count("webstore") > 0 and callees.count("install") > 0:
			install_extension = True

		#chrome.management.uninstall
		elif callees.count("chrome") > 0 and callees.count("management") > 0 and callees.count("uninstall") > 0:
			uninstall_extension = True

		#chrome.tabs.query
		elif callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("query") > 0:
			DoS = True

		#chrome.system.cpu
		elif callees.count("chrome") > 0 and callees.count("system") > 0 and callees.count("cpu") > 0:
			cpu = True

		#chrome.system.display
		elif callees.count("chrome") > 0 and callees.count("system") > 0 and callees.count("display") > 0:
			displays = True

		#chrome.sessions.getDevices
		elif callees.count("chrome") > 0 and callees.count("sessions") > 0 and callees.count("getDevices") > 0:
			sessions = True

		#new XMLHttpRequest
		elif callees.count("XMLHttpRequest") > 0:
			XMLHttpRequest = True

		#XMLHttpRequest.send
		elif callees.count("send") > 0:
			send = True

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
	if tab_listener and remove_tab and extension_tab:
		print "Warning! Extension tab blocked."
	#HTTP response header security options
	if http_header and remove_security and security_option:
		print "Warning! Security options are changed."
	#Extension installation
	if install_extension:
		print "Warning! Extension installation."
	#Extension uninstallation
	if uninstall_extension:
		print "Warning! Extension uninstallation."
	#DoS
	if DoS and remove_tab:
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
	if forms and XMLHttpRequest and send:
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
			parser = PyJsParser()
			tree = parser.parse(data)

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
		parser = PyJsParser()
		for jsfile in js:
			print "Parsing file "+jsfile+" ..."
			with open(jsfile, 'r') as readfile:
				data = readfile.read().decode('utf-8')
			tree = parser.parse(data)

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