#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid
import urwid.raw_display
import getopt,sys,os,subprocess,thread,time
from xfdown_api import XF


class XFdownUi:
    palette = [
        ('body',         'black',      'light gray', 'standout'),
        ('header',       'black',      'light gray', 'standout'),
        ('footer',       'light gray', 'black'),
        ('button normal','light gray', 'dark blue', 'standout'),
        ('button select','white',      'dark green'),
        ('button disabled','dark gray','dark blue'),
        ('exit',         'white',      'dark cyan'),
        ('key',          'light cyan', 'black', 'underline'),
        ('title',        'white',       'black',)
        ]
    footer_text = [
      ('key', "UP"), ",", ('key', "DOWN"), "上下移动 ,",
      ('key', "SPACE"), "选择项目 ,",
      ('key', "ENTER"), "下载选中项 ,", ('key', "O"),
      "在线播放 ,",
      ('key', "Ctrl+C"), " 退出",
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
        for size ,percent,name in j:
            w = self.create_checkbox()
            self.items.append(w)
            w = urwid.Columns( [('fixed', 4, w), 
                ('fixed',7,urwid.Text(size, align='right')),
                ('fixed',6,urwid.Text(percent+'%', align='right')),
                urwid.Text(name)],1)

            w = urwid.AttrWrap(w, 'button normal', 'button select')
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
      if key in (['enter'],['o']):
        self.selected=self.getSelected()
        if self.selected == []:
          self.setMsg("没有选中项目")
          return 
        self.key=key
        raise urwid.ExitMainLoop()
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
      elif self.key==['o']:
        xf.online_v(self.getSelected())
    

    
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
        xf._downpath = os.path.expanduser("~/下载")
        if not os.path.exists(xf._downpath):
          os.makedirs(xf._downpath)

      XFdownUi().main()
  except KeyboardInterrupt:
    print (" exit now.")
    sys.exit(2)
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
