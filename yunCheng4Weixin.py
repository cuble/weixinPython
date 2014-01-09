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
  -sg您的身高（厘米）,如sg165
  -tz您的体重（公斤），如tz50
  -“查询”或“cx”，查询您最近一次的体重和身高数据
  -“查询一周”或“cxyz”，
  -“查询一月”或“cxyy”
'''
    MSG_IMPLEMENTING = u'功能实现中，请明天再试'
    MSG_SUCCESS = [u'存储完成', u'我存好了，随时来查哦',u'搞定，收工']
    def __init__(self, user, reqMsg):
        self.req = reqMsg.lower()
        self.db = yunchengdb(user)
        self.response = self.MSG_HELP
        self._handle_req()

    def _get_command(self):
        self.command = ''
        for i in xrange(len(self.req)):
            if self.req[i].isdigit():
                self.command = self.req[:i].strip()
                if not self.command.startswith('cx'):
                    self.data = int(self.req[i:])
                break
        if self.command == '': 
            self.command = self.req
            self.data = ''
        try:
            print self.command, self.data
        except:
            pass

    def _handle_req(self):
        try:
            self._get_command()
            if self.command == 'tz' or self.command == u'体重' or self.command == '体重':
                self._tz_handle()
            elif self.command == 'sg' or self.command == u'身高' or self.command == '身高':
                self._sg_handle()  
            elif self.command == 'cx' or self.command == u'查询' or self.command == '查询':
                self._cx_handle()
        except Exception as inst:
            print inst
            
    def _get_success_response(self):
        import random
        return self.MSG_SUCCESS[random.randint(0,len(self.MSG_SUCCESS)-1)]
            
    def _tz_handle(self):
        data = {'TiZhong':self.data}
        self.db.store_dict(data)
        self.response = self._get_success_response() 
        
    def _sg_handle(self):
        data = {'ShenGao':self.data}
        self.db.store_dict(data)
        self.response = self._get_success_response() 
        
    def _cx_handle(self):
        data = {'TiZhong': '', 'ShenGao': ''}
        self.db.query_dict(data)
        print data
        response = ''
        if data['ShenGao']:
            response += u'身高：{}厘米'.format(data['ShenGao'])
        if data['TiZhong']:
            if response: response += ','
            response += u'体重：{}公斤'.format(data['TiZhong'])
        self.response = response

import os
import sqlite3
class yunchengdb:
    def __init__(self, dbName):
        dbPath = os.path.join(os.getcwd(), 'DB')
        print dbPath
        if not os.path.isdir(dbPath):
            os.mkdir(dbPath) 
        name = os.path.join(dbPath, dbName+'.db')
        print name
        createNeeded = False
        if not os.path.isfile(name):
            print "First Time Store, Create DB"
            createNeeded = True
        pass
        self.conn = sqlite3.connect(name)
        self.c = self.conn.cursor()
        if createNeeded:
            self._create_db()  
    
    def store_dict(self, dictData):
        sg = tz = ''
        print dictData
        if 'ShenGao' in dictData:
            sg = dictData['ShenGao']
        if 'TiZhong' in dictData:
            tz = dictData['TiZhong']
        print '''INSERT INTO shencai (timestamp, ShenGao, TiZhong) VALUES({},'{}','{}')'''.format(111,sg,tz)
        self.c.execute('''INSERT INTO shencai (timestamp, ShenGao, TiZhong) VALUES({},'{}','{}')'''.format(111,sg,tz))
        self.conn.commit()
    
    def query_dict(self, dictData):
        self.c.execute('''SELECT * from shencai ORDER BY id DESC LIMIT 1''')
        id,timestamp,sg,tz = self.c.fetchone()
        print id, timestamp,sg,tz
        dictData['ShenGao'] = sg
        dictData['TiZhong'] = tz

    
    def _create_db(self):
        self.c.execute('''CREATE TABLE shencai
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp INTEGER, ShenGao text, TiZhong text)''')
        self.c.execute('''CREATE INDEX dateIndex ON shencai(timestamp)''')
        self.conn.commit()
