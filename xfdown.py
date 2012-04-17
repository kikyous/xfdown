#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import hashlib
import subprocess
try:
    import urllib as parse
    import urllib2 as request
    import cookielib as cookiejar
except:
    from urllib import parse,request
    from http import cookiejar
import random,time
import json,os,sys,re
try:
    raw_input
except:
    raw_input=input
def _(string):
    try:
        return string.decode("u8")
    except:
        return string

def get_module_path():
        if hasattr(sys, "frozen"):
            module_path = os.path.dirname(sys.executable)
        else:
            module_path = os.path.dirname(os.path.abspath(__file__))
        return module_path
module_path=get_module_path()

class LWPCookieJar(cookiejar.LWPCookieJar):
    def save(self, filename=None, ignore_discard=False, ignore_expires=False,userinfo=None):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        if not os.path.exists(filename):
            open(filename, "w").close()
        f = open(filename, "rw+")
        try:
            # There really isn't an LWP Cookies 2.0 format, but this indicates
            # that there is extra information in here (domain_dot and
            # port_spec) while still being compatible with libwww-perl, I hope.
            if userinfo:
                f.seek(0)
                f.write("#LWP-Cookies-2.0\n")
                f.write("#%s\n"%userinfo)
            else:
                f.seek(len(''.join(f.readlines()[:2])))
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))
        finally:
            f.close()



class XF:
    """
     Login QQ
    """

    proxy="219.246.90.196:7777"
    __downpath = os.path.expanduser("~/下载")
    try:
        os.makedirs(__downpath)
    except:
        pass

    __headers ={
                'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:13.0) Gecko/20120414 Firefox/13.0a2',\
    }
    __cookiepath = '%s/cookie'%module_path
    __verifyimg  = '%s/verify.jpg'%module_path
    __verifycode = None
    __http = {}
    __RE=re.compile("\d+")
    def __preprocess(self,password=None,verifycode=None,hashpasswd=None):
        """
            QQ密码加密部份
        """
        if hashpasswd:
            return hashlib.md5( (hashpasswd+ (verifycode).upper()).encode('utf-8')).hexdigest().upper()
        else:
            return hashlib.md5( (self.__md5_3((password).encode('utf-8')) + (verifycode).upper()).encode('utf-8')).hexdigest().upper()


    def __md5_3(self,str):
        """
            QQ密码md5_3部份
        """
        self.hashpasswd=hashlib.md5(hashlib.md5(hashlib.md5(str).digest()).digest()).hexdigest().upper()
        return self.hashpasswd
        pass
    def __init__(self):
        """
            初始化模拟进程
        """
        self.__http['cj'] = LWPCookieJar(self.__cookiepath)
        if os.path.isfile(self.__cookiepath):
            self.__http['cj'].load(ignore_discard=True, ignore_expires=True)

        self.__http['opener'] = request.build_opener(request.HTTPCookieProcessor(self.__http['cj']))
        if os.path.isfile(self.__cookiepath):
            self.main()
        else:
            self.__Login(True)
    def __request(self,url,method='GET',data={},savecookie=False):
        """
            请求url
        """
        if (method).upper() == 'POST':
            data = parse.urlencode(data).encode('utf-8')
            self.__http['req'] = request.Request(url,data,headers=self.__headers)
        else:
            self.__http['req'] = request.Request(url=url,headers=self.__headers)
        fp = self.__http['opener'].open(self.__http['req'])
        # print fp.headers
        try:
            str = fp.read().decode('utf-8')
        except UnicodeDecodeError:
            str = fp.read()
        if savecookie == True:
            if hasattr(self,"pswd"):
                self.__http['cj'].save(ignore_discard=True, ignore_expires=True,userinfo="%s#%s"%(self.__qq,self.hashpasswd))
            else:
                self.__http['cj'].save(ignore_discard=True, ignore_expires=True)

        fp.close()
        return str
        pass
    def __getcookies(self,name):
        fp = open(self.__cookiepath)
        fp.seek(130)
        for read in fp.readlines():
            str = read.split(name)
            if len(str) == 2:
                fp.close()
                return str[1].strip()
        fp.close()
        return None
        pass
    def __getverifycode(self):
        """
            @url:http://ptlogin2.qq.com/check?uin=644826377&appid=1003903&r=0.56373973749578
        """


        urlv = 'http://ptlogin2.qq.com/check?uin='+ ('%s' % self.__qq)+'&appid=567008010&r='+ ('%s' % random.Random().random())

        str = self.__request(url = urlv, savecookie=False)
        lists=eval(str.split("(")[1].split(")")[0])
        if lists[0]=='1':
            imgurl="http://captcha.qq.com/getimage?aid=567008010&r=%s&uin=%s&vc_type=%s"%(random.Random().random(),self.__qq,lists[1])
            f=open(self.__verifyimg,"wb")
            fp = self.__http['opener'].open(imgurl)
            f.write(fp.read())
            f.close()
            subprocess.Popen(['xdg-open', self.__verifyimg])
            print("请输入验证码：")
            verify=raw_input("vf # ").strip()
            
        else:
            verify=lists[1]
        return verify
    def __request_login(self):

        urlv = 'http://ptlogin2.qq.com/login?u='+('%s' %  self.__qq) +'&' +  'p=' + ('%s' % self.passwd) +  '&verifycode='+ ('%s' % self.__verifycode) +'&aid=567008010' +  "&u1=http%3A%2F%2Flixian.qq.com%2Fmain.html" +  '&h=1&ptredirect=1&ptlang=2052&from_ui=1&dumy=&fp=loginerroralert'
        str = self.__request(url = urlv,savecookie=True)
        if str.find(_('登录成功')) != -1:
            self.__getlogin()
            self.main()
        elif str.find(_('验证码不正确')) != -1:
            self.__getverifycode()
            self.__Login(False,True)
        elif str.find(_('不正确')) != -1:
#            print str
            print('你输入的帐号或者密码不正确，请重新输入。')
            self.__Login(True)
        else:
            #print('登录失败')
            print str
            self.__Login(True)

    def main(self):
        self.__getlist()
        self.__chosetask()
        self.__getdownload()

    def getfilename_url(self,url):
        url=url.strip()
        filename=""
        if url.startswith("ed2k"):
            arr=url.split("|")
            if len(arr)>=4:
                filename=parse.unquote(arr[2])
        else:
            filename=url.split("/")[-1]
        return filename.split("?")[0]
    def __getlogin(self):
        urlv = 'http://lixian.qq.com/handler/lixian/do_lixian_login.php'
        str = self.__request(url =urlv,method = 'POST',savecookie=True)
        return str
            #登陆旋风，可从str中得到用户信息

    def __getlist(self):
            """
            得到任务名与hash值
            """
            urlv = 'http://lixian.qq.com/handler/lixian/get_lixian_list.php'
            res = self.__request(urlv,'POST',savecookie=False)
            res = json.JSONDecoder().decode(res)
            if res["msg"]==_('未登录!'):
                res=json.JSONDecoder().decode(self.__getlogin())
                if res["msg"]==_('未登录!'):
                    self.__Login()

                else:
                    self.main()
            elif not res["data"]:
                print (_('无离线任务!'))
                self.__addtask()
                self.main()
            else:
                self.filename = []
                self.filehash = []
                self.filemid = []
                print ("\n===================离线任务列表====================")
                print ("序号\t大小\t进度\t文件名")
                for num in range(len(res['data'])):
                    index=res['data'][num]
                    self.filename.append(index['file_name'].encode("u8"))
                    self.filehash.append(index['hash'])
                    size=index['file_size']
                    self.filemid.append(index['mid'])
                    if size==0:
                        percent="-0"

                    else:
                        percent=str(index['comp_size']/size*100).split(".")[0]

                    dw=["B","K","M","G"]
                    for i in range(4):
                        _dw=dw[i]
                        if size>=1024:
                            size=size/1024
                        else:
                            break
                    size="%.1f%s"%(size,_dw)
                    print ("%d\t%s\t%s%%\t%s"%(num+1,size,percent,_(self.filename[num])))
                print ("=======================END=========================\n")

    def __gethttp(self,filelist):
            """
            获取任务下载连接以及FTN5K值
            """
            urlv = 'http://lixian.qq.com/handler/lixian/get_http_url.php'
            self.filehttp = list(range(len(self.filehash)))
            self.filecom = list(range(len(self.filehash)))
            for num in filelist:
                num=int(num)-1
                data = {'hash':self.filehash[num],'filename':self.filename[num],'browser':'other'}
                str = self.__request(urlv,'POST',data)
                self.filehttp[num]=(re.search(r'\"com_url\":\"(.+?)\"\,\"',str).group(1))
                self.filecom[num]=(re.search(r'\"com_cookie":\"(.+?)\"\,\"',str).group(1))
       
    def __chosetask(self):
        print ("请选择操作,输入回车(Enter)下载任务\nA添加任务,O在线观看,D删除任务,R刷新离线任务列表")
        inputs=raw_input("ct # ")
        if inputs=="":
            self.__getdownload()
        elif inputs.upper()=="A":
            self.__addtask()
            self.main()
        elif inputs.upper()=="D":
            self.__deltask()
            self.main()
        elif inputs.upper()=="R":
            self.main()
        elif inputs.upper()=="O":
            self.__online()
            self.main()


    def __getdownload(self):
            print ("请输入要下载的任务序号,数字之间用空格,逗号或其他非数字字符号分割.\n输入A下载所有任务:")
            target=raw_input("dl # ").strip()
            if target.upper()=="A":
                lists=range(1,len(self.filehttp)+1)
            else:
                lists=self.__RE.findall(target)
            if lists==[]:
                print ("选择为空.")
                self.__chosetask()
                return
            #print lists
            self.__gethttp(lists)
            self.__download(lists)

    def __deltask(self):
        print ("请输入要删除的任务序号,数字之间用空格,逗号或其他非数字字符号分割.\n输入A删除所有任务:")
        target=raw_input("dt # ").strip()
        if target.upper()=="A":
            lists=range(1,len(self.filehttp)+1)
        else:
            lists=self.__RE.findall(target)
        if lists==[]:
            print ("选择为空.")
            self.__chosetask()
        urlv = 'http://lixian.qq.com/handler/lixian/del_lixian_task.php'
        for num in lists:
                num=int(num)-1
                data = {'mids':self.filemid[num]}
                str = self.__request(urlv,'POST',data)
        print("任务删除完成")
                    
    def __addtask(self):
        print ("请输入下载地址:")
        url=raw_input()
        filename=self.getfilename_url(url)
        data={"down_link":url,\
                "filename":filename,\
                "filesize":0,\
                }
        urlv="http://lixian.qq.com/handler/lixian/add_to_lixian.php"
        str = self.__request(urlv,'POST',data)

    def __online(self):
        print("输入需要在线观看的任务序号")
        num = int(raw_input())-1
        self.__gethttp([num+1])
        print [self.filename[num]]
        print("正在缓冲，马上开始播放")
        filename=_(self.filename[num])
        arg=['wget', '-c', '-O', filename, '--header', 'Cookie:FTN5K=%s'%self.filecom[num], self.filehttp[num]]

        subprocess.Popen(arg,cwd=_(self.__downpath))
        time.sleep(5)
        arg=['totem', filename]
        subprocess.Popen(arg,cwd=_(self.__downpath))

        #os.system(r'killall wget')

    def __download(self,lists):
            f = open("%s/.xfd"%self.__downpath,'w')
            for num in lists:
                try:
                    num=int(num)-1
                    f.write(self.filehttp[num])
                    f.write("\n  header=Cookie: FTN5K=%s" %self.filecom[num])
                    if hasattr(self,"proxy") and self.proxy:
                        f.write("\n  all-proxy=%s" %self.proxy)
                         
                    f.write("\n  max-conection-per-server=5\n  min-split-size=2097152\n  parameterized-uri=true\n  continue=true\n  split=5\n\n")
                except:
                    print (num+1 ,_(" 任务建立失败!"))
            f.close()
            print("aria2输入文件建立")

            """
            调用aria2进行下载

            """
            # if not hasattr(self,"proxy") or self.proxy==None:
            os.system("cd %s && aria2c -i .xfd"% self.__downpath)
                    
    def __Login(self,needInput=False,verify=False):
        """
        登录
        """
        if not needInput and not verify:
            try:
                f=open(self.__cookiepath)
                line=f.readlines()[1].strip()
                lists=line.split("#")
                self.__qq=lists[1]
                self.hashpasswd=lists[2]
            finally:
                f.close()
        if not hasattr(self,"hashpasswd") or needInput:
            self.__qq = raw_input('QQ号码：')
            self.pswd = raw_input('QQ密码：')
            self.pswd = self.pswd.strip()
        self.__qq = self.__qq.strip()
        self.__verifycode = self.__getverifycode()
        if not hasattr(self,"hashpasswd") or needInput:
            self.passwd = self.__preprocess(
                self.pswd,#密码 \
                '%s' % self.__verifycode  #验证码 \
            )
        else:
            self.passwd = self.__preprocess(
                verifycode='%s' % self.__verifycode ,
                hashpasswd=self.hashpasswd
            )
        print ("登录中...")
        self.__request_login()

try:
    s = XF()
except KeyboardInterrupt:
    print (" exit now.")
    sys.exit()

