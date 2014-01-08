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
    def __init__(self, data):
        self.data = data
        self.dict = self._xmlToDict(self.data)
        if self.dict['MsgType'] == 'event':
            self.worker = eventHandler(self.dict['FromUserName'],self.dict['Event'])
        else:
            self.worker = txtmsgHandler(self.dict['FromUserName'],self.dict['Content'])

    def response(self):
        responseDict = self.responseDict()
        text = self.responseXML(responseDict)
        return text
    
    
    def _xmlToDict(self, xmlText):
        xmlDict = {}
        itemlist = ET.fromstring(xmlText)
        for child in itemlist:
            xmlDict[child.tag] = child.text
        print xmlDict
        return xmlDict
    
    def responseXML(self, dataDict):
        if dataDict:
            text = RESPONSE_TEXT_TEMPLATE 
            for key, value in dataDict.items():
                parameter = '{%s}' % key
                text = text.replace(parameter, value)
            print text
        else:
            text = ''
        return text
    
    def responseDict(self):
        responseDict = {}
        try:
            responseDict['RESPONSE_CONTENT'] = self.worker.response.encode('UTF-8')
            responseDict['TO_USER'] = self.dict['FromUserName']
            responseDict['FROM_USER'] = self.dict['ToUserName']
            responseDict['TIME_STEMP'] = str(timeHelper.unixTimeStamp())
        except:
            pass
        return responseDict

class eventHandler:
    MSG_WELCOME = u'欢迎您关注云称客户端，我为您提供记录和查询体重信息的服务。了解详情请发送“帮助”或“？”'
    def __init__(self, user, event):
        if event == 'subscribe':
            self.response = self.MSG_WELCOME

class txtmsgHandler:
    MSG_HELP = u'''
本系统接受的命令有：
  -tz您的体重（公斤）,例如tz50
  -sg您的身高（厘米），例如sg165
  -“查询”或“cx”，查询您最近一次的体重和身高数据
  -“查询一周”或“cxyz”，
  -“查询一月”或“cxyy”
'''
    def __init__(self, user, reqMsg):
        self.req = reqMsg
        self.response = self.MSG_HELP
        self._handle_req()

    def _handle_req(self):
        if self.req.startswith('tz') or self.req.startswith(u'体重'):
            self._handle_tz()            
            
    def _handle_tz(self):
        self.response = u'功能实现中，请明天再试'        