from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
	isScript = False
	def handle_starttag(self, tag, attrs):
		#tkMessageBox.showinfo( "Start tag:", tag)
		if tag == "script":
			self.isScript = True
			print "Start tag: "+tag+"\n"
		

	def handle_endtag(self, tag):
		#tkMessageBox.showinfo( "End tag:", tag)
		if tag == "script":
			self.isScript = False

	def handle_data(self, data):
		#tkMessageBox.showinfo( "Data:", data)
		if self.isScript:
			print data

	def handle_entityref(self, name):
		c = unichr(name2codepoint[name])
		tkMessageBox.showinfo( "Named ent:", c)


def Main():
	from pyjsparser.parser import PyJsParser

	f = open("input11.txt", 'rb')
	x = f.read()
	f.close()

	p = MyHTMLParser()
	res = p.feed(x)

	
	

if __name__ == '__main__':
	Main()