# -*- coding: UTF-8 -*-
import urllib2, urllib, cookielib, re, time
import random
import sqlite3
import threading

class Robot:
    def __init__(self, forumUrl, userName, password, proxy = None):
        self.forumUrl = forumUrl
        self.userName = userName
        self.password = password
        self.formhash = ''
        self.isLogon = False
        self.isSign = False
        self.xq = ''

        self.conn = None
        self.cur = None
        self.InitDB()

        self.jar = cookielib.CookieJar()
        if not proxy:
            openner = urllib2.build_opener(
        urllib2.HTTPCookieProcessor(self.jar))
        else:
            openner = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.jar), 
            urllib2.ProxyHandler({'http' : proxy}))
        urllib2.install_opener(openner)
    def login(self):
        url = self.forumUrl + "/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&inajax=1";
        postData = urllib.urlencode({
        'username': self.userName, 
        'password': self.password, 
        'answer': '', 
        'cookietime': '2592000', 
        'handlekey': 'ls', 
        'questionid': '0',
        'quickforward': 'yes', 
        'fastloginfield': 'username'
        })
        req = urllib2.Request(url,postData)
        content = urllib2.urlopen(req).read()
        if self.userName in content:
            self.isLogon = True
            print 'login success!'
            self.initFormhashXq()
        else:
            print 'login faild!'

    def getOneTitle(self):
        result = urllib2.urlopen(self.forumUrl + '/forum.php')
        reglink = r"href=\"(http\:\/\/rs\.xidian\.edu\.cn\/forum\.php\?mod=viewthread&tid=6796.+?)\""
        link = re.findall(re.compile(reglink),result.read())
        print link[0]
        return link[0]

    def getTid(self,link):
        tidPage=urllib2.urlopen(link).read()
        tidnum=re.search('\d{6}',link)
        print tidnum.group()
        return tidnum.group()

    def getFid(self,link):
        tidPage=urllib2.urlopen(link).read()
        fid =re.search('<input\s*type="hidden"\s*name="srhfid"\s*value="([\w\W]+?)"\s*\/>',tidPage)
        print fid.group(1)
        return fid.group(1)
 
    def initFormhashXq(self):
        content = urllib2.urlopen(self.forumUrl + '/plugin.php?id=dsu_paulsign:sign')
        content = content.read()
        rows = re.findall(r'<input\s*type="hidden"\s*name="formhash"\s*value="([\w\W]+?)"\s*\/>', content)
        if len(rows)!=0:
            self.formhash = rows[0]
            print 'formhash is: ' + self.formhash
        else:
            print 'none formhash!'

    def InitDB(self):
        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()
        sql = '''create table if not exists rspost (
            fid text,
            tid text,
            replied integer)'''
        self.cur.execute(sql)
        self.conn.commit()
 
    def reply(self, fid,tid,msg):
        query = "select * from rspost where fid='%s' and tid='%s'" % (fid,tid)
        self.cur.execute(query)
        if self.cur.fetchone():
            print 'Skip! Article:%s is already replied...' % tid
        #http://rs.xidian.edu.cn/forum.php?mod=post&action=reply&fid=%s&tid=%s&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1' % (fid.group(1),tidnum.group())
        #url = self.forumUrl + '/forum.php?mod=post&action=reply&fid=41&tid={}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'.format(tid)
        else:
            url = self.forumUrl+'/forum.php?mod=post&action=reply&fid=%s&tid=%s&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1' % (fid,tid)
            postData = urllib.urlencode({
            'formhash': self.formhash, 
            'message': msg, 
            'subject': '', 
            'posttime':int(time.time()) 
            })
            req = urllib2.Request(url,postData)
            insert = "insert into rspost values ('%s', '%s', '%d')" % (fid, tid, 1)
            self.cur.execute(insert)
            self.conn.commit()
            content = urllib2.urlopen(req).read()
            #print content
            #if u'发布成功' in content:
            print 'reply success!'
            #else:
            #    print 'reply faild!'
def loop():
    robot = Robot('http://rs.xidian.edu.cn', 'cutoutsy', 'letxxcw1z_h')
    replylist = [
            u'不错，支持一下.......',
            u'已阅，顶一下.......',
            u'顶一个...........',
            u'路过帮顶........',
            u'沙发，沙发.....',
            u'我的沙发........',
            u'我来了.........',
            u'沙发是我的......',
            u'我来看看.......',
            u'前排，前排........'
    ]
    content = random.choice(replylist)
    content = content.encode('utf-8')
    robot.login()
    link = robot.getOneTitle()
    tid = robot.getTid(link)
    fid = robot.getFid(link)
    robot.reply(fid,tid,content)
    global t
    t = threading.Timer(10.0,loop)
    t.start()


if __name__ == '__main__':
    t = threading.Timer(10.0,loop)
    t.start()
 #   robot = Robot('http://rs.xidian.edu.cn', 'cutoutsy', 'letxxcw1z_h')
#     replylist = [
#            u'不错，支持一下.......',
#            u'已阅，顶一下.......',
#            u'顶一个...........',
#            u'路过帮顶........',
#            u'沙发，沙发.....',
#            u'我的沙发........',
#            u'我来了.........',
#            u'沙发是我的......',
#            u'我来看看.......',
#            u'提着水桶到处转，哪里有水哪里灌'
#    ]
#    content = random.choice(replylist)
#    content = content.encode('utf-8')
#    robot.login()
#    link = robot.getOneTitle()
#    tid = robot.getTid(link)
#    fid = robot.getFid(link)
#    robot.reply(fid,tid,content)