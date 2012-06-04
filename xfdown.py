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

    __downpath = os.path.expanduser("~/下载")
    try:
        os.makedirs(__downpath)
    except:
        pass

    __cookiepath = '%s/cookie'%module_path
    __verifyimg  = '%s/verify.jpg'%module_path
    __RE=re.compile("(\d+) *([^\d ]+)?")
    def __preprocess(self,password=None,verifycode=None,hashpasswd=None):

        if not hashpasswd:
            hashpasswd=self.__md5(password)

        I=self.EncodePasswd.hexchar2bin(hashpasswd)

        H = self.EncodePasswd.md5(I + verifycode[2])
        G = self.EncodePasswd.md5(H + verifycode[1].upper());

        return G


    def __md5(self,str):
        self.hashpasswd=self.EncodePasswd.md5(str)

        return self.hashpasswd
    def __init__(self):
        self.cookieJar=LWPCookieJar(self.__cookiepath)

        if os.path.isfile(self.__cookiepath):
            self.cookieJar.load(ignore_discard=True, ignore_expires=True)

        opener = request.build_opener(request.HTTPCookieProcessor(self.cookieJar))
        request.install_opener(opener)
        
        self.EncodePasswd=EncodePasswd()

        if os.path.isfile(self.__cookiepath):
            self.main()
        else:
            self.__Login(True)
    def __request(self,url,data=None,savecookie=False,headers={}):
        """
            请求url
        """
        if data:
            data = parse.urlencode(data).encode('utf-8')
            fp=request.urlopen(url,data)
        else:
            fp=request.urlopen(url)
        # print fp.headers
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
            fp = urllib2.urlopen(imgurl)
            f.write(fp.read())
            f.close()
            subprocess.Popen(['xdg-open', self.__verifyimg])
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
            print('你输入的帐号或者密码不正确，请重新输入。')
            self.__Login(True)
        else:
            #print('登录失败')
            print str
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
            self.filehttp = [''] * len(self.filehash)
            self.filecom = [''] * len(self.filehash)
            for num in filelist:
                num=int(num[0])-1
                data = {'hash':self.filehash[num],'filename':self.filename[num],'browser':'other'}
                str = self.__request(urlv,data)
                self.filehttp[num]=(re.search(r'\"com_url\":\"(.+?)\"\,\"',str).group(1))
                self.filecom[num]=(re.search(r'\"com_cookie":\"(.+?)\"\,\"',str).group(1))
       
    def __chosetask(self):
        print ("请选择操作,输入回车(Enter)下载任务\nA添加任务,O在线观看,D删除任务,R刷新离线任务列表")
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
            print ("请输入要下载的任务序号,数字之间用空格或其他字符分隔.\n输入A下载所有任务:")
            print ("(数字后跟p只打印下载命令而不下载，比如1p2p3)")
            target=raw_input("dl # ").strip()
            if target.upper()=="A":
                lists=zip(range(1,len(self.filehash)+1) , ['']* len(self.filehash))
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
            lists=zip(range(1,len(self.filehash)+1) , ['']* len(self.filehash))
        else:
            lists=self.__RE.findall(target)
        if lists==[]:
            print ("选择为空.")
            self.__chosetask()
        urlv = 'http://lixian.qq.com/handler/lixian/del_lixian_task.php'

        for i in lists:
            num=int(i[0])-1
            data={'mids':self.filemid[num]}
            self.__request(urlv,data)
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
        str = self.__request(urlv,data)

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
        cmds=[]

        for i in lists:
            num=int(i[0])-1
            cmd="aria2c -c -s10 -x10 --header 'Cookie:ptisp=edu; FTN5K=%s' '%s'"%(self.filecom[num],self.filehttp[num])
            cmd=cmd.encode("u8")
            if i[1].upper()=='P':
                print('\n%s'%cmd)
            else:
                cmds.append(cmd)

        """
        调用aria2进行下载

        """
        for i in cmds:
            os.system("cd %s && %s"%(self.__downpath,i))
                    
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
            import getpass
            self.pswd=getpass.getpass('QQ密码: ')
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
        print ("登录中...")
        self.__request_login()


class EncodePasswd(object):
    def __init__(self, passwd=None, verifycode=None):
        self.passwd = passwd
        self.verifycode = verifycode
        self.hexcase = 1
        self.b64pad = ''
        self.chrsz = 8
        self.mode = 32

    def str2binl(self, D):
        C = []
        A = (1<<self.chrsz) - 1
        for B in range(0, len(D)*self.chrsz, self.chrsz):
            if len(C) == (B>>5): C.append(0)
            C[B>>5] |= (ord(D[B//self.chrsz])&A)<<(B%32)
        return C

    def binl2hex(self, C):
        B = "0123456789abcdef"
        if self.hexcase: 
            B = "0123456789ABCDEF"
        D = ''
        for A in range(0, len(C)*4, 1):
            D += B[(C[A>>2]>>((A%4)*8+4))&15] + B[(C[A>>2]>>((A%4)*8))&15]
        return D
        
    def md5(self, A):
        return self.hex_md5(A)

    def hex_md5(self, A): 
        return self.binl2hex(self.core_md5(self.str2binl(A), len(A)*self.chrsz))
    
    def str_md5(self, A):
        return self.binl2str(self.core_md5(self.str2binl(A), len(A)*self.chrsz))
    
    def hex_hmac_md5(self, A, B):
        return self.binl2hex(self.core_hmac_md5(A, B))
        
    def b64_hmac_md5(self, A, B):
        return binl2b64(core_hmac_md5(A, B))
    
    def str_hmac_md5(self, A, B):
        return self.binl2str(self.core_hmac_md5(A, B))
       
    def md5_vm_test(self):
        return self.hex_md5('abc') == '900150983cd24fb0d6963f7d28e17f72'
    
    # this is equvalent of >>> in js
    def rsl(self, A, B):
        return (A & 0xFFFFFFFFL) >> B
    
    def jsArraySet(self, list, index, value):
        if index < 0: return
        if len(list) > index:
            list[index] = value
        else:
            for i in range(index-len(list)):
                list.append(0)
            list.append(value)
    def jsArrayGet(self, list, index):
        if len(list) > index:
            return list[index]
        else:
            return 0
    
    def core_md5(self, K, F):
        #K[F>>5] |= 128<<((F)%32)
        self.jsArraySet(K, F>>5, self.jsArrayGet(K, F>>5)|(128<<(F%32)))
        #K[(self.rsl(F+64, 9)<<4)+14] = F
        self.jsArraySet(K, (self.rsl(F+64, 9)<<4)+14, F)
        J=1732584193;
        I=-271733879;
        H=-1732584194;
        G=271733878;
        
        for C in range(0, len(K), 16):
            E=J;
            D=I;
            B=H;
            A=G;
            J=self.md5_ff(J,I,H,G,self.jsArrayGet(K, C+0),7,-680876936);
            G=self.md5_ff(G,J,I,H,self.jsArrayGet(K, C+1),12,-389564586);
            H=self.md5_ff(H,G,J,I,self.jsArrayGet(K, C+2),17,606105819);
            I=self.md5_ff(I,H,G,J,self.jsArrayGet(K, C+3),22,-1044525330);
            J=self.md5_ff(J,I,H,G,self.jsArrayGet(K, C+4),7,-176418897);
            G=self.md5_ff(G,J,I,H,self.jsArrayGet(K, C+5),12,1200080426);
            H=self.md5_ff(H,G,J,I,self.jsArrayGet(K, C+6),17,-1473231341);
            I=self.md5_ff(I,H,G,J,self.jsArrayGet(K, C+7),22,-45705983);
            J=self.md5_ff(J,I,H,G,self.jsArrayGet(K, C+8),7,1770035416);
            G=self.md5_ff(G,J,I,H,self.jsArrayGet(K, C+9),12,-1958414417);
            H=self.md5_ff(H,G,J,I,self.jsArrayGet(K, C+10),17,-42063);
            I=self.md5_ff(I,H,G,J,self.jsArrayGet(K, C+11),22,-1990404162);
            J=self.md5_ff(J,I,H,G,self.jsArrayGet(K, C+12),7,1804603682);
            G=self.md5_ff(G,J,I,H,self.jsArrayGet(K, C+13),12,-40341101);
            H=self.md5_ff(H,G,J,I,self.jsArrayGet(K, C+14),17,-1502002290);
            I=self.md5_ff(I,H,G,J,self.jsArrayGet(K, C+15),22,1236535329);
            J=self.md5_gg(J,I,H,G,self.jsArrayGet(K, C+1),5,-165796510);
            G=self.md5_gg(G,J,I,H,self.jsArrayGet(K, C+6),9,-1069501632);
            H=self.md5_gg(H,G,J,I,self.jsArrayGet(K, C+11),14,643717713);
            I=self.md5_gg(I,H,G,J,self.jsArrayGet(K, C+0),20,-373897302);
            J=self.md5_gg(J,I,H,G,self.jsArrayGet(K, C+5),5,-701558691);
            G=self.md5_gg(G,J,I,H,self.jsArrayGet(K, C+10),9,38016083);
            H=self.md5_gg(H,G,J,I,self.jsArrayGet(K, C+15),14,-660478335);
            I=self.md5_gg(I,H,G,J,self.jsArrayGet(K, C+4),20,-405537848);
            J=self.md5_gg(J,I,H,G,self.jsArrayGet(K, C+9),5,568446438);
            G=self.md5_gg(G,J,I,H,self.jsArrayGet(K, C+14),9,-1019803690);
            H=self.md5_gg(H,G,J,I,self.jsArrayGet(K, C+3),14,-187363961);
            I=self.md5_gg(I,H,G,J,self.jsArrayGet(K, C+8),20,1163531501);
            J=self.md5_gg(J,I,H,G,self.jsArrayGet(K, C+13),5,-1444681467);
            G=self.md5_gg(G,J,I,H,self.jsArrayGet(K, C+2),9,-51403784);
            H=self.md5_gg(H,G,J,I,self.jsArrayGet(K, C+7),14,1735328473);
            I=self.md5_gg(I,H,G,J,self.jsArrayGet(K, C+12),20,-1926607734);
            J=self.md5_hh(J,I,H,G,self.jsArrayGet(K, C+5),4,-378558);
            G=self.md5_hh(G,J,I,H,self.jsArrayGet(K, C+8),11,-2022574463);
            H=self.md5_hh(H,G,J,I,self.jsArrayGet(K, C+11),16,1839030562);
            I=self.md5_hh(I,H,G,J,self.jsArrayGet(K, C+14),23,-35309556);
            J=self.md5_hh(J,I,H,G,self.jsArrayGet(K, C+1),4,-1530992060);
            G=self.md5_hh(G,J,I,H,self.jsArrayGet(K, C+4),11,1272893353);
            H=self.md5_hh(H,G,J,I,self.jsArrayGet(K, C+7),16,-155497632);
            I=self.md5_hh(I,H,G,J,self.jsArrayGet(K, C+10),23,-1094730640);
            J=self.md5_hh(J,I,H,G,self.jsArrayGet(K, C+13),4,681279174);
            G=self.md5_hh(G,J,I,H,self.jsArrayGet(K, C+0),11,-358537222);
            H=self.md5_hh(H,G,J,I,self.jsArrayGet(K, C+3),16,-722521979);
            I=self.md5_hh(I,H,G,J,self.jsArrayGet(K, C+6),23,76029189);
            J=self.md5_hh(J,I,H,G,self.jsArrayGet(K, C+9),4,-640364487);
            G=self.md5_hh(G,J,I,H,self.jsArrayGet(K, C+12),11,-421815835);
            H=self.md5_hh(H,G,J,I,self.jsArrayGet(K, C+15),16,530742520);
            I=self.md5_hh(I,H,G,J,self.jsArrayGet(K, C+2),23,-995338651);
            J=self.md5_ii(J,I,H,G,self.jsArrayGet(K, C+0),6,-198630844);
            G=self.md5_ii(G,J,I,H,self.jsArrayGet(K, C+7),10,1126891415);
            H=self.md5_ii(H,G,J,I,self.jsArrayGet(K, C+14),15,-1416354905);
            I=self.md5_ii(I,H,G,J,self.jsArrayGet(K, C+5),21,-57434055);
            J=self.md5_ii(J,I,H,G,self.jsArrayGet(K, C+12),6,1700485571);
            G=self.md5_ii(G,J,I,H,self.jsArrayGet(K, C+3),10,-1894986606);
            H=self.md5_ii(H,G,J,I,self.jsArrayGet(K, C+10),15,-1051523);
            I=self.md5_ii(I,H,G,J,self.jsArrayGet(K, C+1),21,-2054922799);
            J=self.md5_ii(J,I,H,G,self.jsArrayGet(K, C+8),6,1873313359);
            G=self.md5_ii(G,J,I,H,self.jsArrayGet(K, C+15),10,-30611744);
            H=self.md5_ii(H,G,J,I,self.jsArrayGet(K, C+6),15,-1560198380);
            I=self.md5_ii(I,H,G,J,self.jsArrayGet(K, C+13),21,1309151649);
            J=self.md5_ii(J,I,H,G,self.jsArrayGet(K, C+4),6,-145523070);
            G=self.md5_ii(G,J,I,H,self.jsArrayGet(K, C+11),10,-1120210379);
            H=self.md5_ii(H,G,J,I,self.jsArrayGet(K, C+2),15,718787259);
            I=self.md5_ii(I,H,G,J,self.jsArrayGet(K, C+9),21,-343485551);
            J=self.safe_add(J,E);
            I=self.safe_add(I,D);
            H=self.safe_add(H,B);
            G=self.safe_add(G,A)
            
        if self.mode == 16:
            return [I, H]
        else:
            return [J, I, H, G]
            
    def md5_cmn(self, F, C, B, A, E, D):
        return self.safe_add(self.bit_rol(self.safe_add(self.safe_add(C, F), self.safe_add(A, D)), E), B)
        
    def md5_ff(self, C, B,G, F,A,E,D):
        return self.md5_cmn((B&G)|((~B)&F), C, B, A, E, D)
        
    def md5_gg(self, C,B,G,F,A,E,D):
        return self.md5_cmn((B&F)|(G&(~F)),C,B,A,E,D)
        
    def md5_hh(self, C,B,G,F,A,E,D):
        return self.md5_cmn(B^G^F, C,B,A,E,D)
        
    def md5_ii(self,C,B,G,F,A,E,D):
        return self.md5_cmn(G^(B|(~F)),C,B,A,E,D)
    
    def core_hmac_md5(self, C, F):
        E = self.str2binl(C)
        if len(E) > 16:
            E = self.core_md5(E,len(C)*self.chrsz)
        A = [None]*16
        D = [None]*16
        for B in range(0, 16):
            A[B] = E[B]^909522486
            D[B] = E[B]^1549556828
        G = self.core_md5(A+self.str2binl(F), 512+len(F)*self.chrsz)
        return self.core_md5(D+G, 512+128)    
    
    def safe_add(self, A,D):
        C = (A&65535)+(D&65535)
        B = (A>>16)+(D>>16)+(C>>16)
        return (B<<16)|(C&65535)

    def bit_rol(self, A, B):
        return (A<<B)|self.rsl(A, 32-B)
        
    def binl2str(self, C):
        D = ''
        A = (1<<self.chrsz)-1
        for B in range(0, len(C)*32, self.chrsz):
            D += chr(self.rsl(C[B>>5], B%32)&A)
        return D
        
    def binl2b64(self, D):
        C="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        F = ''
        for B in range(0, len(D)*4, 3):
            E=(((D[B>>2]>>8*(B%4))&255)<<16)|(((D[B+1>>2]>>8*((B+1)%4))&255)<<8)|((D[B+2>>2]>>8*((B+2)%4))&255)
            for A in range(0, 4):
                if B*8+A*6>len(D)*32:
                    F += self.b64pad
                else:
                    F += C[(E>>6*(3-A))&63]
        return F


    def hexchar2bin(self,str):
        arr = []
        for i in range(0, len(str) , 2):
            arr.append("\\x" + str[i:i+2])
        arr="".join(arr)
        exec("temp = '" + arr + "'");
        return temp



try:
    s = XF()
except KeyboardInterrupt:
    print (" exit now.")
    sys.exit()

