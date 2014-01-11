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
    MSG_HELP = u'''本系统接受的命令有：
  -sg您的身高（厘米）,如sg165
  -tz您的体重（公斤），如tz50
  -也可以输入：身高165，体重50
  -“查询”或“cx”，查询您最近一次的体重和身高数据
  -“查询一周”或“cxyz”，
  -“查询一月”或“cxyy”
'''
    MSG_IMPLEMENTING = u'功能实现中，请明天再试'
    MSG_SUCCESS = [u'存储完成', u'我存好了，随时来查哦',u'搞定，收工']
    MSG_ERROR_TZ_NULL = u'体重数据不对，命令格式是：tz数字'
    MSG_ERROR_SG_NULL = u'身高数据不对，命令格式是：sg数字'
    def __init__(self, user, reqMsg):
        self.req = reqMsg.lower().replace(u'，',',')
        self.db = yunchengdb(user)
        self.response = self.MSG_HELP
        self._handle_req()

    def _decode_command(self, cmd):
        decodedResult = {}
        for i in xrange(len(cmd)):
            if cmd[i].isdigit():
                decodedResult[cmd[:i].strip()] = float(cmd[i:])
                break
        if not decodedResult:
            self.command[cmd] = ''
        else:
            self.command.update(decodedResult)


    def _get_command(self):
        self.command = {}
        cmds = self.req.split(',')
        for cmd in cmds:
            self._decode_command(cmd)
        try:
            print self.command
        except:
            pass
    
    def _verify_command(self):
        data = {}
        for cmd in self.command:
            if cmd == 'tz' or cmd == u'体重' or cmd == '体重':
                if 'TiZhong' in data:
                    self.response = u"查询命令不能和存储命令同时使用"
                    return False
                data.update({'TiZhong':self.command[cmd]})
            elif cmd == 'sg' or cmd == u'身高' or cmd == '身高':
                if 'ShenGao' in data:
                    self.reponse = u"查询命令不能和存储命令同时使用"
                    return False
                data.update({'ShenGao':self.command[cmd]})
            elif cmd == 'cx' or cmd == u'查询' or cmd == '查询':
                if 'ShenGao' in data or 'TiZhong' in data:
                    self.response = u"查询命令不能和存储命令同时使用"
                    return False
                data = {'TiZhong': '', 'ShenGao': ''}
                self._cx_handle()
                return True
            else:
                print 'unrecognized command:{}'.format(cmd)
                self.response = u"不支持命令{} \n".format(cmd)
                self.response+= self.MSG_HELP
                return False
        self.db.store_dict(data)
        self.response = self._get_success_response() 
        return True
        

    def _handle_req(self):
        try:
            self._get_command()
            if not self._verify_command():
                return
        except Exception as inst:
            print inst
            
    def _get_success_response(self):
        import random
        return self.MSG_SUCCESS[random.randint(0,len(self.MSG_SUCCESS)-1)]
            
    def _tz_handle(self, cmd):
        if self.command[cmd]:
            data = {'TiZhong':self.command[cmd]}
            self.db.store_dict(data)
            self.response = self._get_success_response() 
        else:
            self.response = self.MSG_ERROR_TZ_NULL
        
    def _sg_handle(self, cmd):
        if self.command[cmd]:
            data = {'ShenGao':self.command[cmd]}
            self.db.store_dict(data)
            self.response = self._get_success_response()
        else:
            self.response = self.MSG_ERROR_SG_NULL 
        
    def _cx_handle(self):
        data = {'TiZhong': '', 'ShenGao': ''}
        self.db.query_dict(data)
        print data
        response = u'您在{}的记录是：'.format(data['DateTime'])
        if data['ShenGao']:
            response += u'身高{}厘米'.format(data['ShenGao'])
        if data['TiZhong']:
            if response: response += ','
            response += u'体重{}公斤'.format(data['TiZhong'])
        self.response = response

import os
import sqlite3
class yunchengdb:
    def __init__(self, dbName):
        dbPath = os.path.join(os.getcwd(), 'DB')
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
            
    def __del__(self):
        self.conn.close()
        
    
    def store_dict(self, dictData):
        sg = tz = ''
        print dictData
        if 'ShenGao' in dictData:
            sg = dictData['ShenGao']
        if 'TiZhong' in dictData:
            tz = dictData['TiZhong']
        timestamp = timeHelper.unixTimeStamp()
        print '''INSERT INTO shencai (timestamp, ShenGao, TiZhong) VALUES({},'{}','{}')'''.format(timestamp,sg,tz)
        self.c.execute('''INSERT INTO shencai (timestamp, ShenGao, TiZhong) VALUES({},'{}','{}')'''.format(timestamp,sg,tz))
        self.conn.commit()
    
    def query_dict(self, dictData):
        self.c.execute('''SELECT * from shencai ORDER BY id DESC LIMIT 1''')
        id,timestamp,sg,tz = self.c.fetchone()
        print id, timestamp,sg,tz
        dictData['ShenGao'] = sg
        dictData['TiZhong'] = tz
        dictData['DateTime'] = timeHelper.timestamp2datetime(timestamp)

    
    def _create_db(self):
        self.c.execute('''CREATE TABLE shencai
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp INTEGER, ShenGao text, TiZhong text)''')
        self.c.execute('''CREATE INDEX dateIndex ON shencai(timestamp)''')
        self.conn.commit()
        
    def close_db(self):
        self.conn.close()
