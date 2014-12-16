#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urwid
import urwid.raw_display
import getopt,sys,os,subprocess,thread,time
from xfdown_api import XF


class XFdownUi:
    palette = [
        ('body',         '',      '', 'standout'),
        ('header',       'black',      'light gray', 'standout'),
        ('footer',       'light gray', 'black'),
        ('button normal','', '', 'standout'),
        ('button downloading','dark blue', '', 'standout'),
        ('button checking','yellow', '', 'standout'),
        ('button select','white',      'dark green'),
        ('button disabled','dark gray','dark blue'),
        ('exit',         'white',      'dark cyan'),
        ('key',          'light cyan', 'black', 'underline'),
        ('title',        'white',       'black',)
        ]
    footer_text = [
      ('key', "UP或K"), ",", ('key', "DOWN或J"), "上下移动 ,",
      ('key', "SPACE"), "选择项目 ,",
      ('key', "ENTER"), "下载项目 ,",
      ('key', "D"),     "删除项目 ,",
      ('key', "O"),     "在线播放 ,",
      ('key', "Q"),     " 退出",
    ]
        
    def create_checkbox(self, g=None, name='', font=None, fn=None):
        w = urwid.CheckBox(name, False ,False, on_state_change=fn)
        w.font = font
        return w

    def setup_view(self):
        # ListBox
        l = []
        self.items = []
        j = xf.getlist()
        for size,percent,name,status,tasktype,fileurl in j:
            w = self.create_checkbox()
            self.items.append(w)
            w = urwid.Columns( [('fixed', 4, w), 
                ('fixed',7,urwid.Text(size, align='right')),
                ('fixed',6,urwid.Text(percent+'%', align='right')),
                urwid.Text(name)],1)

            if status == 12:
                w = urwid.AttrWrap(w, 'button normal', 'button select')
            elif status == 6:
                w = urwid.AttrWrap(w, 'button downloading', 'button select')
            elif status == 8:
                w = urwid.AttrWrap(w, 'button checking', 'button select')

            l.append(w)

        w = urwid.ListBox(urwid.SimpleListWalker(l))
        
        # Frame
        self.listbox = urwid.AttrWrap(w, 'body')
        hdr = urwid.Text("XFdown Tui Beta\nhttps://github.com/kikyous/xfdown")
        hdr = urwid.AttrWrap(hdr, 'header')
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),'footer')
        w = urwid.Frame(header=hdr, body=self.listbox ,footer=self.footer)

        return w


    def setMsg(self,text=None):
      if text:
        self.footer.set_align_mode('right')
        self.footer.set_text(text)
        thread.start_new_thread(self.setMsg,())
      else:
        time.sleep(2)
        self.footer.set_align_mode('left')
        self.footer.set_text(self.footer_text)

    def getSelected(self):
        selected=[]
        for index,item in enumerate(self.items):
          if item.get_state():
            selected.append(index)
        return selected


    def input_filter(self,key,raw):
      if key in (['enter'],['o'],['d']):
        self.selected=self.getSelected()
        if self.selected == []:
          self.setMsg("没有选中项目")
          return 
        self.key=key
        raise urwid.ExitMainLoop()
      elif key==['q']:
        self.key=key
        raise urwid.ExitMainLoop()
      elif key in (['j'],['k']):
        if key==['j']:
	  key=['down']
        elif key==['k']:
	  key=['up']
	return key
      else:
        return key
    def main(self):
        self.view= self.setup_view()
        self.loop = urwid.MainLoop(self.view, self.palette, 
            input_filter = self.input_filter)
        self.loop.run()
        self.work()

    def work(self):
      if self.key==['enter']:
        xf.download(self.getSelected())
      elif self.key==['d']:
        xf.deltask(self.getSelected())
        self.main()
      elif self.key==['o']:
        xf.online_v(self.getSelected())
      elif self.key==['q']:
        print (" exit now.")
        exit(0)
    
if '__main__'==__name__:
  def usage():
    print("QQxf offline download utility (you need aria2 installed to use).\n")
    print("  -h,--help\tshow this usage and exit.")
    print("  -d <dir>,--downloaddir=<dir>\n\tset the download dir.")
    print("  -p <player>,--player=<player>\n\tset the player.")
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
        import locale
        if 'zh_CN' in locale.getdefaultlocale():
          xf._downpath = os.path.expanduser("~/下载")
        else:
          xf._downpath = os.path.expanduser("~/Downloads")
      if not os.path.exists("%s"%xf._downpath):
        os.makedirs("%s"%xf._downpath)

      XFdownUi().main()
  except KeyboardInterrupt:
    print (" exit now.")
    sys.exit(2)
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
