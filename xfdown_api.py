#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division
import cPickle as pickle
import socket
import os, sys, stat
cachefile=os.path.expanduser('~/.xfdown.cache')

origGetAddrInfo = socket.getaddrinfo
try:
  with open(cachefile, "rb") as f:
    dnscache=pickle.load(f)
except:
  dnscache={}

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
  if dnscache.has_key(host):
    return dnscache[host]
  else:
    dns=origGetAddrInfo(host, port, family, socktype, proto, flags)
    dnscache[host]=dns
    pickle.dump(dnscache, open(cachefile, "wb") , True)
    return dns

socket.getaddrinfo = getAddrInfoWrapper

import subprocess
try:
    import urllib as parse
    import urllib2 as request
    import cookielib as cookiejar
except:
    from urllib import parse,request
    from http import cookiejar
    raw_input=input
import random,time
import json,os,sys,re,hashlib

def _(string):
    try:
        return string.decode("u8")
    except:
        return string

def _print(str):
    print (_(str)).encode("utf-8","ignore")

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(sys.executable)
    else:
        module_path = os.path.dirname(os.path.abspath(__file__))
    return module_path
module_path=get_module_path()

def hexchar2bin(hex):
    arry= bytearray()
    for i in range(0, len(hex), 2):
        arry.append(int(hex[i:i+2],16))
    return arry

def get_gtk(strs):
    hash = 5381
    for i in strs:
        hash += (hash << 5) + ord(i)
    return hash & 0x7fffffff;

class LWPCookieJar(cookiejar.LWPCookieJar):
    def save(self, filename=None, ignore_discard=False, ignore_expires=False,userinfo=None):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        if not os.path.exists(filename):
          f=open(filename,'w')
          f.close()
        f = open(filename, "r+")
        try:
            if userinfo:
                f.seek(0)
                f.write("#LWP-Cookies-2.0\n")
                f.write("#%s\n"%userinfo)
            else:
                f.seek(len(''.join(f.readlines()[:2])))
            f.truncate()
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))
        finally:
            f.close()



class XF:
    _player="totem"

    __cookiepath = os.path.expanduser('~/.xfdown.cookie')
    __configpath = os.path.expanduser('~/.xfdown.config')
    __verifyimg  = os.path.expanduser('~/.xfdown.verify.jpg')
    __RE=re.compile("(\d+) *([^\d ]+)?")


    def online_v(self,lists):
      num=lists[0]
      self.gethttp([num])
      filename=_(self.filename[num])
      cmd=['wget', '-c', '-O', filename, '--header', 'Cookie:FTN5K=%s'%self.filecom[num], self.filehttp[num]]

      subprocess.Popen(cmd,cwd=_(self._downpath))
      time.sleep(5)
      cmd=['xdg-open', filename]
      subprocess.Popen(cmd,cwd=_(self._downpath))


    def download(self,lists):
        self.gethttp(lists)
        cmds=[]
        for i in lists:
            cmd=['aria2c', '-c', '-s10', '-x10', '--header', 'Cookie: FTN5K=%s'%self.filecom[i], '%s'%self.filehttp[i]]

            cmds.append(cmd)

        for i in cmds:
            subprocess.Popen(i,cwd=self._downpath).wait()
            try:
                subprocess.Popen(["notify-send","xfdown: 下载完成!"])
            except:
                if os.name=='posix':
                  _print("notify-send error,you should have libnotify-bin installed.")


    def __preprocess(self,password=None,verifycode=None,hashpasswd=None):

        if not hashpasswd:
            self.hashpasswd=self.__md5(password)

        I=hexchar2bin(self.hashpasswd)
        if sys.version_info >= (3,0):
          H = self.__md5(I + bytes(verifycode[2],encoding="ISO-8859-1"))
        else:
          H = self.__md5(I + verifycode[2])
        G = self.__md5(H + verifycode[1].upper())

        return G
        
    def __md5(self,item):
        if sys.version_info >= (3,0):
            try:
              item=item.encode("u8")
            except:
              pass
        return hashlib.md5(item).hexdigest().upper()

    def __init__(self):
        self.cookieJar=LWPCookieJar(self.__cookiepath)
        cookieload=False

        if os.path.isfile(self.__cookiepath):
            try:
                self.cookieJar.load(ignore_discard=True, ignore_expires=True)
                cookieload=True
            except:
                pass
                
        opener = request.build_opener(request.HTTPCookieProcessor(self.cookieJar))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0'),("Referer","http://lixian.qq.com/main.html")]
        request.install_opener(opener)
        
        if not cookieload:
            self.Login(True)
    def __request(self,url,data=None,savecookie=False):
        """
            请求url
        """
        if data:
            data = parse.urlencode(data).encode('utf-8')
            fp=request.urlopen(url,data)
        else:
            fp=request.urlopen(url)
        try:
            str = fp.read().decode('utf-8')
        except UnicodeDecodeError:
            str = fp.read()
        if savecookie == True:
            if hasattr(self,"pswd"):
                self.cookieJar.save(ignore_discard=True, ignore_expires=True,userinfo="%s#%s"%(self.__qq,self.hashpasswd))
            else:
                self.cookieJar.save(ignore_discard=True, ignore_expires=True)

        fp.close()
        return str
    def __getverifycode(self):

        urlv = 'http://check.ptlogin2.qq.com/check?uin=%s&appid=567008010&r=%s'%(self.__qq,random.Random().random())

        str = self.__request(url = urlv)
        verify=eval(str.split("(")[1].split(")")[0])
        verify=list(verify)
        if verify[0]=='1':
            imgurl="http://captcha.qq.com/getimage?aid=567008010&r=%s&uin=%s"%(random.Random().random(),self.__qq)
            f=open(self.__verifyimg,"wb")
            fp = request.urlopen(imgurl)
            f.write(fp.read())
            f.close()
            try:
                subprocess.Popen(['xdg-open', self.__verifyimg])
            except:
                _print("请打开%s查看验证码"%self.__verifyimg)
            print("请输入验证码：")
            vf=raw_input("vf # ").strip()
            verify[1]=vf
            
        return verify

    def __load_config(self):

        os.chmod(self.__configpath , stat.S_IREAD|stat.S_IWRITE)
        config_file=open(self.__configpath)
        config=json.load(config_file)
        return config


    def __save_config(self):
        self.__load_config()
        config={"qq":self.__qq, "password":self.pswd}
        config_file=open(self.__configpath,"w")
        json.dump(config,config_file)
        config_file.close()
        os.chmod(self.__configpath , stat.S_IREAD|stat.S_IWRITE)


    def __request_login(self):

        urlv="http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s"%(self.__qq,self.passwd,self.__verifycode[1])+"&aid=567008010&u1=http%3A%2F%2Flixian.qq.com%2Fmain.html&h=1&ptredirect=1&ptlang=2052&from_ui=1&dumy=&fp=loginerroralert&action=2-10-&mibao_css=&t=1&g=1"
        str = self.__request(url = urlv)
        if str.find(_('登录成功')) != -1:
            self.__getlogin()
            self.__save_config()
            return True
        elif str.find(_('验证码不正确')) != -1:
            self.__getverifycode()
            self.Login(False,True)
        elif str.find(_('不正确')) != -1:
            _print('你输入的帐号或者密码不正确，请重新输入。')
            self.Login(True)
        else:
            #print('登录失败')
            _print(str)
            self.Login(True)

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
        self.__request(url ="http://lixian.qq.com/handler/log_handler.php",data={'cmd': 'stat'},savecookie=True)
        urlv = 'http://lixian.qq.com/handler/lixian/do_lixian_login.php'
        f=open(self.__cookiepath)
        fi = re.compile('skey="([^"]+)"')
        skey = fi.findall("".join(f.readlines()))[0]
        f.close()
        str = self.__request(url =urlv,data={"g_tk":get_gtk(skey)},savecookie=True)
        return str

    def getlist(self):
            """
            得到任务名与hash值
            """
            urlv = 'http://lixian.qq.com/handler/lixian/get_lixian_items.php'
            res = self.__request(urlv, {'page': 0, 'limit': 200})
            res = json.JSONDecoder().decode(res)
            result = []
            if res["msg"]==_('未登录!'):
                res=json.JSONDecoder().decode(self.__getlogin())
                if res["msg"]==_('未登录!'):
                    self.Login()
                else:
                    return self.getlist()
            else:
                self.filename = []
                self.filehash = []
                self.filemid = []
                if not res["data"]:
                    return result
                #res['data'].sort(key=lambda x: x["file_name"])
                # _print ("序号\t大小\t进度\t文件名")
                for num in range(len(res['data'])):
                    index=res['data'][num]
                    self.filename.append(index['file_name'].encode("u8"))
                    self.filehash.append(index['hash'])
                    size=index['file_size']
                    status=index['dl_status']
                    fileurl=index['file_url']
                    tasktype=index['task_type']
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
                    item=(size,percent,_(self.filename[num]),status,tasktype,fileurl)
                    result.append(item)
            return result

    def gethttp(self,filelist):
      """
      获取任务下载连接以及FTN5K值
      """
      urlv = 'http://lixian.qq.com/handler/lixian/get_http_url.php'
      self.filehttp = [''] * len(self.filehash)
      self.filecom = [''] * len(self.filehash)
      for num in filelist:
        data = {'hash':self.filehash[num],'filename':self.filename[num],'browser':'other'}
        str = self.__request(urlv,data)
        self.filehttp[num]=(re.search(r'\"com_url\":\"(.+?)\"\,\"',str).group(1))
        self.filecom[num]=(re.search(r'\"com_cookie":\"(.+?)\"\,\"',str).group(1))
       

    def deltask(self,lists):
        urlv = 'http://lixian.qq.com/handler/lixian/del_lixian_task.php'

        for i in lists:
            data={'mids':self.filemid[i]}
            ret=json.loads(self.__request(urlv,data))
            if ret['ret']== -1:
                self.Login()

                    
    def __addtask(self):
        _print ("请输入下载地址:")
        url=raw_input()
        filename=self.getfilename_url(url)
        data={"down_link":url,\
                "filename":filename,\
                "filesize":0,\
                }
        urlv="http://lixian.qq.com/handler/lixian/add_to_lixian.php"
        str = self.__request(urlv,data)


                    
    def Login(self,needinput=False,verify=False):
        if not needinput and not verify:
            if os.path.isfile(self.__configpath):
                config=self.__load_config()
                self.__qq=config['qq']
                self.pswd=config['password']
        if not hasattr(self,"pswd") or needinput:
            self.__qq = raw_input('QQ：')
            import getpass
            self.pswd= getpass.getpass('PASSWD: ')
            self.pswd = self.pswd.strip()
        self.__qq = self.__qq.strip()
        self.__verifycode = self.__getverifycode()
        if not hasattr(self,"hashpasswd") or needinput:
            self.passwd = self.__preprocess(
                self.pswd,
                self.__verifycode
            )
        else:
            self.passwd = self.__preprocess(
                verifycode=self.__verifycode ,
                hashpasswd=self.hashpasswd
            )
        _print ("登录中...")
        self.__request_login()
