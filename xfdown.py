#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import subprocess
try:
    import urllib as parse
    import urllib2 as request
    import cookielib as cookiejar
except:
    from urllib import parse,request
    from http import cookiejar
import random,time
import json,os,sys,re,hashlib
import getopt




try:
    raw_input
except:
    raw_input=input
def _(string):
    try:
        return string.decode("u8")
    except:
        return string

def _print(str):
    print (_(str))
def get_module_path():
        if hasattr(sys, "frozen"):
            module_path = os.path.dirname(sys.executable)
        else:
            module_path = os.path.dirname(os.path.abspath(__file__))
        return module_path
module_path=get_module_path()

def hexchar2bin(str):
        arr = []
        for i in range(0, len(str) , 2):
            arr.append("\\x" + str[i:i+2])
        arr="".join(arr)
        exec("temp = '" + arr + "'");
        return temp


class LWPCookieJar(cookiejar.LWPCookieJar):
    def save(self, filename=None, ignore_discard=False, ignore_expires=False,userinfo=None):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        f = open(filename, "a+")
        try:
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

    _player="totem"

    __cookiepath = '%s/cookie'%module_path
    __verifyimg  = '%s/verify.jpg'%module_path
    __RE=re.compile("(\d+) *([^\d ]+)?")
    def __preprocess(self,password=None,verifycode=None,hashpasswd=None):

        if not hashpasswd:
            self.hashpasswd=self.__md5(password)

        I=hexchar2bin(self.hashpasswd)

        H = self.__md5(I + verifycode[2])
        G = self.__md5(H + verifycode[1].upper());

        return G


    def __md5(self,str):
        return hashlib.md5(str).hexdigest().upper()


    def start(self):
        self.cookieJar=LWPCookieJar(self.__cookiepath)

        cookieload=False

        if os.path.isfile(self.__cookiepath):
            try:
                self.cookieJar.load(ignore_discard=True, ignore_expires=True)
                cookieload=True
            except:
                pass
                

        opener = request.build_opener(request.HTTPCookieProcessor(self.cookieJar))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        request.install_opener(opener)
        

        if cookieload:
            self.main()
        else:
            self.__Login(True)
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

        str = self.__request(url = urlv, savecookie=False)
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


    def __request_login(self):

        urlv="http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s"%(self.__qq,self.passwd,self.__verifycode[1])+"&aid=567008010&u1=http%3A%2F%2Flixian.qq.com%2Fmain.html&h=1&ptredirect=1&ptlang=2052&from_ui=1&dumy=&fp=loginerroralert&action=2-10-&mibao_css=&t=1&g=1"
        str = self.__request(url = urlv,savecookie=True)
        if str.find(_('登录成功')) != -1:
            self.__getlogin()
            self.main()
        elif str.find(_('验证码不正确')) != -1:
            self.__getverifycode()
            self.__Login(False,True)
        elif str.find(_('不正确')) != -1:
            _print('你输入的帐号或者密码不正确，请重新输入。')
            self.__Login(True)
        else:
            #print('登录失败')
            _print(str)
            self.__Login(True)

    def main(self):
        self.__getlist()
        self.__chosetask()

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
        str = self.__request(url =urlv,data={},savecookie=True)
        return str

    def __getlist(self):
            """
            得到任务名与hash值
            """
            urlv = 'http://lixian.qq.com/handler/lixian/get_lixian_list.php'
            res = self.__request(urlv,{},savecookie=False)
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
                res['data'].sort(key=lambda x: x["file_name"])
                _print ("\n===================离线任务列表====================")
                _print ("序号\t大小\t进度\t文件名")
                for num in range(len(res['data'])):
                    index=res['data'][num]
                    self.filename.append(index['file_name'].encode("u8"))
                    self.filehash.append(index['code'])
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
                    _print ("%d\t%s\t%s%%\t%s"%(num+1,size,percent,_(self.filename[num])))
                _print ("=======================END=========================\n")

    def __gethttp(self,filelist):
            """
            获取任务下载连接以及FTN5K值
            """
            urlv = 'http://lixian.qq.com/handler/lixian/get_http_url.php'
            self.filehttp = [''] * len(self.filehash)
            self.filecom = [''] * len(self.filehash)
            for num in filelist:
                num=int(num[0])-1
                data = {'hash':self.filehash[num],'filename':self.filename[num],'browser':'other'}
                str = self.__request(urlv,data)
                self.filehttp[num]=(re.search(r'\"com_url\":\"(.+?)\"\,\"',str).group(1))
                self.filecom[num]=(re.search(r'\"com_cookie":\"(.+?)\"\,\"',str).group(1))
       
    def __chosetask(self):
        _print ("请选择操作,输入回车(Enter)下载任务\nA添加任务,O在线观看,D删除任务,R刷新离线任务列表")
        inputs=raw_input("ct # ")
        if inputs.upper()=="A":
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
        else:
            self.__getdownload()
            self.main()

    def __getdownload(self):
            _print ("请输入要下载的任务序号,数字之间用空格或其他字符分隔.\n输入A下载所有任务:")
            _print ("(数字后跟p只打印下载命令而不下载，比如1p2p3)")
            target=raw_input("dl # ").strip()
            if target.upper()=="A":
                lists=zip(range(1,len(self.filehash)+1) , ['']* len(self.filehash))
            else:
                lists=self.__RE.findall(target)
            if lists==[]:
                _print ("选择为空.")
                self.__chosetask()
                return

            self.__gethttp(lists)
            self.__download(lists)

    def __deltask(self):
        _print ("请输入要删除的任务序号,数字之间用空格,逗号或其他非数字字符号分割.\n输入A删除所有任务:")
        target=raw_input("dt # ").strip()
        if target.upper()=="A":
            lists=zip(range(1,len(self.filehash)+1) , ['']* len(self.filehash))
        else:
            lists=self.__RE.findall(target)
        if lists==[]:
            _print ("选择为空.")
            self.__chosetask()
        urlv = 'http://lixian.qq.com/handler/lixian/del_lixian_task.php'

        for i in lists:
            num=int(i[0])-1
            data={'mids':self.filemid[num]}
            self.__request(urlv,data)
        _print("任务删除完成")

                    
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

    def __online(self):
        _print("输入需要在线观看的任务序号")
        num = int(raw_input())-1
        self.__gethttp([(num+1,'')])
        _print("正在缓冲，马上开始播放")
        filename=_(self.filename[num])
        cmd=['wget', '-c', '-O', filename, '--header', 'Cookie:FTN5K=%s'%self.filecom[num], self.filehttp[num]]

        subprocess.Popen(cmd,cwd=_(self._downpath))
        time.sleep(5)
        cmd=[self._player, filename]
        subprocess.Popen(cmd,cwd=_(self._downpath))

    def __download(self,lists):
        cmds=[]

        for i in lists:
            num=int(i[0])-1
            cmd="aria2c -c -s10 -x10 --header 'Cookie:ptisp=edu; FTN5K=%s' '%s'"%(self.filecom[num],self.filehttp[num])
            if sys.version_info >= (3,0):
                pass
            else:
                cmd=cmd.encode("u8")

            if i[1].upper()=='P':
                print('\n%s'%cmd)
            else:
                cmds.append(cmd)

        """
        调用aria2进行下载

        """
        for i in cmds:
            os.system("cd %s && %s"%(self._downpath,i))
                    
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
            self.__qq = raw_input('QQ：')
            import getpass
            self.pswd=getpass.getpass('PASSWD: ')
            self.pswd = self.pswd.strip()
        self.__qq = self.__qq.strip()
        self.__verifycode = self.__getverifycode()
        if not hasattr(self,"hashpasswd") or needInput:
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


def usage():
    print("QQxf offline download utility (you need aria2 installed to use).\n")
    print("  -h,--help\tshow this usage and exit.")
    print("  -d <dir>,--downloaddir=<dir>\n\tset the download dir.")
    print("  -p <dir>,--player=<dir>\n\tset the player.")
    print("\n\nsee https://github.com/kikyous/xfdown for most newest version and more information")
try:
    xf = XF()
    opts, args = getopt.getopt(sys.argv[1:], "hd:p:", ["help", "downloaddir=","player="])
    for o, v in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-d", "--downloaddir"):
            xf._downpath=os.path.abspath(os.path.expanduser(v))
        elif o in ("-p", "--player"):
            xf._player=v
        else:
            assert False, "unhandled option"
    if not hasattr(xf,"_downpath"):
        xf._downpath = os.path.expanduser("~/下载")
    os.makedirs(xf._downpath) if not os.path.exists(xf._downpath) else None

    xf.start()
except KeyboardInterrupt:
    print (" exit now.")
    sys.exit(2)
except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
