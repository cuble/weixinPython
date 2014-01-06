import xml.etree.ElementTree as ET
import timeHelper

RESPONSE_TEXT_TEMPLATE = '''
<xml>
<ToUserName><![CDATA[{TO_USER}]]></ToUserName>
<FromUserName><![CDATA[{FROM_USER}]]></FromUserName>
<CreateTime>{TIME_STEMP}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{RESPONSE_CONTENT}]]></Content>
</xml>
'''  

class msgHandler:
    MSG_WELCOME = ""
    MSG_HELP = ""
    def __init__(self, data):
        self.data = data
        
    def response(self):

        dataDict = self.xmlToDict(self.data)
        print dataDict
        responseDict = self.responseDictFromInputDict(dataDict)
        text = self.responseXML(responseDict)
        
        return text
    
    
    def xmlToDict(self, xmlText):
        xmlDict = {}
        itemlist = ET.fromstring(xmlText)
        for child in itemlist:
            xmlDict[child.tag] = child.text
        return xmlDict
    
    def responseXML(self, dataDict):
        text = RESPONSE_TEXT_TEMPLATE 
        for key, value in dataDict.items():
            parameter = '{%s}' % key
            text = text.replace(parameter, value)
        return text
    
    def responseDictFromInputDict(self, dataDict):
        responseDict = {}
        responseDict['TO_USER'] = dataDict['FromUserName']
        responseDict['FROM_USER'] = dataDict['ToUserName']
        responseDict['TIME_STEMP'] = str(timeHelper.unixTimeStamp())
        if dataDict['MsgType'] == 'event':
            text = u'欢迎您关注云称客户端\n我为您提供记录和查询体重信息的服务'
        else:
            text = u'你好，系统尚在测试中……您刚才说的是：' + dataDict['Content']
        responseDict['RESPONSE_CONTENT'] = text.encode('UTF-8')
        return responseDict

