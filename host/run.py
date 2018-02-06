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

def Main():
    from pyjsparser.parser import PyJsParser

    f = open("input1.txt", 'rb')
    x = f.read()
    f.close()

    p = PyJsParser()
    res = p.parse(x)

    #pprint(res)
    l = dict_generator(res)
    #for i in l:
    #    print i

    '''
    CallExpression = []
    callees = []
    extension_tab = False
    remove_tab = False
    listener = False

    for i in l:
        #if isinstance(i, list):

        if i.count("CallExpression") > 0:
            print "->"+str(callees)
            if callees:
                CallExpression.append(callees)
                print CallExpression
                callees = []
            print "-->"+str(CallExpression)
        elif i.count("callee") > 0 and i.count("name") > 0:
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
        elif i.count("chrome://chrome/extensions/") or i.count("chrome://chrome/extensions") or i.count("chrome://extensions/") or i.count("chrome://extensions"):
            extension_tab = True

    print callees
    if callees:
        CallExpression.append(callees)
        callees = []

    print CallExpression
    while CallExpression:
        callees = CallExpression.pop()
        if callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("onUpdated") > 0 and callees.count("addListener") > 0:
            listener = True
        elif callees.count("chrome") > 0 and callees.count("tabs") > 0 and callees.count("remove") > 0:
            remove_tab = True

    if listener and remove_tab and extension_tab:
        print "asfadgfsdg"
    '''

if __name__ == '__main__':
	Main()