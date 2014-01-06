# -*- coding: UTF-8 -*-

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
    MSG_WELCOME = u'欢迎您关注云称客户端\n我为您提供记录和查询体重信息的服务\n了解详情请发送“帮助”或“？”'
    MSG_HELP = '''
本系统功能如下：
  发送“记录体重 您的体重”或“jltz 您的体重”，本系统将记录您的体重数据
  发送“记录身高 您的身高”或“jlsg 您的身高”， 本系统将记录您的身高
  发送“查询”或“cx”，本系统将回复您最近一次的体重和身高数据
  您还可以发送发送“查询一周”或“cxyz”，“查询一月”或“cxyy”
'''
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
            text = self.MSG_WELCOME
        else:
            text = self.MSG_HELP
        responseDict['RESPONSE_CONTENT'] = text.encode('UTF-8')
        return responseDict

