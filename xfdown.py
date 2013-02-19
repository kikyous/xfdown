#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid
import urwid.raw_display
import getopt,sys,os,subprocess,thread,time
from xfdown_api import XF

class DialogExit(Exception):
    def __init__(self, exitcode = 0):
        self.exitcode = exitcode

class ChildDialogExit(DialogExit):
    pass

class MainDialogExit(DialogExit):
    pass

class WindowDisplay(urwid.WidgetWrap):
    palette = [
        ('body',         'black',      'dark blue', 'standout'),
        ('header',       'black',      'light gray', 'standout'),
        ('footer',       'light gray', 'black'),
        ('button normal','light gray', 'dark blue', 'standout'),
        ('button select','white',      'dark green'),
        ('key',          'light cyan', 'black', 'underline'),
        ('title',        'white',      'black'),
        ('border',       'black',      'dark blue'),
        ('shadow',       'white',      'black')
        ]
    parent = None
    def __init__(self, view=None, loop=None):
      self.loop=loop
      self.view=view

      # Call WidgetWrap.__init__ to correctly initialize ourselves
      urwid.WidgetWrap.__init__(self, view)


    def show(self):
        if self.loop is None:
            self.loop = urwid.MainLoop(self.view, self.palette)
            exited = False
            while not exited:
                try:
                    self.loop.run()
                except ChildDialogExit as e:

                    # Determine which dialog has exited
                    # and act accordingly
                    pass
                except MainDialogExit:
                    exited = True
        else:
            self.loop.widget = self.view



class MyCheckBox(urwid.CheckBox):
    def keypress(self, size, key):
        if key == 'enter': return key
        return self.__super.keypress(size, key)

class MyListBox(urwid.ListBox):
  def keypress(self, size, key):
    if key == 'enter':
      ui.do(xf.download)
    elif key == 'm':
      ui.dialog=MenuDialog("菜单", 40, 10, None, ui.loop)
      ui.dialog.show()
    elif key == 'o':
      ui.do(xf.online_v)
    elif key == 'r':
      ui.refresh()
    else:
      return self.__super.keypress(size, key)
class DialogListBox(urwid.ListBox):
  def keypress(self, size, key):
    if key == 'm':
      ui.loop.widget=ui.dialog.parent
    else:
      return self.__super.keypress(size, key)
class XFdownUi(WindowDisplay):
    footer_text = [
      ('key', "UP"), ",", ('key', "DOWN"), "上下移动 ,",
      ('key', "SPACE"), "选择项目 ,",
      ('key', "ENTER"), "下载选中项 ,", ('key', "O"),
      "在线播放 ,",
      ('key', "Ctrl+C"), " 退出",
    ]
    def __init__(self):
      self.view=self.setup_view()
      WindowDisplay.__init__(self,self.view)
        
    def create_checkbox(self, g=None, name='', font=None, fn=None):
        w = MyCheckBox(name, False ,False, on_state_change=fn)
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

        w = MyListBox(urwid.SimpleListWalker(l))
        
        # Frame
        self.listbox = urwid.AttrWrap(w, 'body')
        hdr = urwid.Text("XFdown Tui Beta\nhttps://github.com/kikyous/xfdown")
        hdr = urwid.AttrWrap(hdr, 'header')
        self.footer = urwid.AttrWrap(urwid.Text(self.footer_text),'footer')
        w = urwid.Frame(header=hdr, body=self.listbox ,footer=self.footer)

        return w


    def setMsg(self,text=None,timeout=None):
      if text:
        self.footer.set_align_mode('right')
        self.footer.set_text(text)
        if timeout:
          thread.start_new_thread(self.setMsg,())
      else:
        time.sleep(2)
        self.footer.set_align_mode('left')
        self.footer.set_text(self.footer_text)
      self.loop.draw_screen()

    def getSelected(self):
        selected=[]
        for index,item in enumerate(self.items):
          if item.get_state():
            selected.append(index)
        return selected

    def do(self,work):
        selected=self.getSelected()
        if selected == []:
          self.setMsg("没有选中项目",2)
        else:
          self.work=lambda:work(selected)
          raise MainDialogExit(0)

    def refresh(self):
        self.setMsg("请稍候...")
        self.view= self.setup_view()
        self.loop.widget = self.view

    def init(self):
      self.show()
      self.work()

class MenuItem(urwid.Text):
    """A custom widget for the --menu option"""
    def __init__(self, label, callback=None):
        urwid.Text.__init__(self, label)
        self.state = False
        self.callback=callback
    def selectable(self):
        return True
    def keypress(self,size,key):
        if key == "enter":
            self.state = True
            ui.loop.widget=ui.dialog.parent
            if self.callback:self.callback()
            # raise ChildDialogExit(0)
        return key
    def mouse_event(self,size,event,button,col,row,focus):
        if event=='mouse release':
            self.state = True
            raise ChildDialogExit(0)
        return False
    def get_state(self):
        return self.state
    def get_label(self):
        text, attr = self.get_text()
        return text 
class MenuDialog(WindowDisplay):
    def __init__(self, text, width, height, body=None, loop=None):
      menu_list=[
        MenuItem('全选',lambda:[i.set_state(True) for i in ui.items]),
        MenuItem('反选',lambda:[i.set_state(not i.get_state()) for i in ui.items]),
        MenuItem('下载所选项目',lambda:ui.do(xf.download)),
        MenuItem('在线播放所选(首个)项目',lambda:ui.do(xf.online_v)),
      ]
      menu_list=[ urwid.AttrWrap(i,'button normal', 'button select') for i in menu_list ]
      w = DialogListBox(urwid.SimpleListWalker(menu_list))
      self.frame = urwid.Frame(body=w, focus_part = 'body')
      if text is not None:
          self.frame.header = urwid.Pile( [urwid.Text(text),
              urwid.Divider(u'\u2550')] )
      w = self.frame
      
      # pad area around listbox
      w = urwid.Padding(w, ('fixed left',2), ('fixed right',2))
      w = urwid.Filler(w, ('fixed top',1), ('fixed bottom',1))
      w = urwid.AttrWrap(w, 'header')
      
      # "shadow" effect
      w = urwid.Columns( [w,('fixed', 2, urwid.AttrWrap(
          urwid.Filler(urwid.Text(('border','  ')), "top")
          ,'shadow'))])
      w = urwid.Frame( w, footer = 
          urwid.AttrWrap(urwid.Text(('border','  ')),'shadow'))

      # outermost border area
      w = urwid.Padding(w, 'center', width )
      w = urwid.Filler(w, 'middle', height )
      w = urwid.AttrWrap( w, 'border' )
      if loop:
          # this dialog is a child window
          # overlay it over the parent window
          self.loop = loop
          self.parent = self.loop.widget
          w = urwid.Overlay(w, self.parent, 'center', width+2, 'middle', height+2)
      self.view = w
      
      # Call WidgetWrap.__init__ to correctly initialize ourselves
      WindowDisplay.__init__(self, self.view,self.loop)
    
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

      ui=XFdownUi()
      ui.init()
  except KeyboardInterrupt:
    print (" exit now.")
    sys.exit(2)
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
