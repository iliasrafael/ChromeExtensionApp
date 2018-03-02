#!/usr/bin/env python

from pyjsparser.parser import PyJsParser
from HTMLParser import HTMLParser

import sys
import os, shutil
from os import walk

reload(sys)
sys.setdefaultencoding('utf-8')

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

#Static analysis functions:
#URL:
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

	l = dict_generator(tree)
	for i in l:
		for j in i:
			#URL:
			url = isURL(str(j).strip())
			if url != "":
				#print url
				if check_url(url):
					print "Blacklisted URL: "+url
					#print report
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

	#print str(CallExpression)
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

	#Uninstallation prevention
	if listener and remove_tab and extension_tab:
		print "Warning! Extension tab blocked."
	# HTTP response header security options
	if http_header and remove_security and security_option:
		print "Warning! Security options are changed."
	#Extension installation
	if install_extension:
		print "Warning! Extension installation."

class MyHTMLParser(HTMLParser):
	isScript = False
	def handle_starttag(self, tag, attrs):
		global report
		
		if tag == "script":
			self.isScript = True
			print "Start tag: "+tag
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
			print data
			parser = PyJsParser()
			tree = parser.parse(data)

			check_js(tree)
			print report





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
			print report

			report = ""
			print "File "+jsfile+" parsed successfully."

		parser2 = MyHTMLParser()
		for htmlfile in html:
			print "Parsing file "+htmlfile+" ..."
			with open(htmlfile, 'r') as readfile:
				data = readfile.read().decode('utf-8')
			tree = parser2.feed(data)

			print "File "+htmlfile+" parsed successfully."
			#result = tree.to_ecma()
			
			print report
			report = ""

	except Exception, e:
		print e
	

if __name__ == '__main__':
	Main()