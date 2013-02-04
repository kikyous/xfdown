#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urwid
import urwid.raw_display
import getopt,sys,os,subprocess
from xfdown_api import XF


class SwitchingPadding(urwid.Padding):
    def padding_values(self, size, focus):
        maxcol = size[0]
        width, ignore = self.original_widget.pack(size, focus=focus)
        if maxcol > width:
            self.align = "left"
        else:
            self.align = "right"
        return urwid.Padding.padding_values(self, size, focus)


class XFdownUi:
    palette = [
        ('body',         'black',      'light gray', 'standout'),
        ('header',       'black',      'light gray', 'standout'),
        ('footer',       'black',      'light gray', 'standout'),
        ('button normal','light gray', 'dark blue', 'standout'),
        ('button select','white',      'dark green'),
        ('button disabled','dark gray','dark blue'),
        ('edit',         'light gray', 'dark blue'),
        ('bigtext',      'white',      'black'),
        ('chars',        'light gray', 'black'),
        ('exit',         'white',      'dark cyan'),
        ]
        
    def create_radio_button(self, g=None, name='', font=None, fn=None):
        w = urwid.CheckBox(name, False ,False, on_state_change=fn)
        w.font = font
        return w

    def create_disabled_radio_button(self, name):
        w = urwid.Text("    " + name + " (UTF-8 mode required)")
        w = urwid.AttrWrap(w, 'button disabled')
        return w
    
    def create_edit(self, label, text, fn):
        w = urwid.Edit(label, text)
        urwid.connect_signal(w, 'change', fn)
        fn(w, text)
        w = urwid.AttrWrap(w, 'edit')
        return w

    def set_font_event(self, w, state):
        if state:
            self.bigtext.set_font(w.font)
            self.chars_avail.set_text(w.font.characters())

    def edit_change_event(self, widget, text):
        self.bigtext.set_text(text)

    def setup_view(self):
        # ListBox
        l = []
        self.items = []
        j = xf.getlist()
        # j =[('','asdf'),('','vvvv'),('','asdf'),('','bbbbbb')]*20
        for size ,percent,name in j:
            w = self.create_radio_button()
            self.items.append(w)
            w = urwid.Columns( [('fixed', 4, w), 
                ('fixed',7,urwid.Text(size, align='right')),
                ('fixed',6,urwid.Text(percent+'%', align='right')),
                urwid.Text(name)],1)

            w = urwid.AttrWrap(w, 'button normal', 'button select')
            # w = urwid.AttrWrap(w, 'selectable','focus')
            l.append(w)



        w = urwid.ListBox(urwid.SimpleListWalker(l))
        # w = urwid.AttrWrap( w, "selectable" )
        
        # Frame
        self.listbox = urwid.AttrWrap(w, 'body')
        # self.output_widget = urwid.Text("")
        # w=urwid.Pile([self.listbox,self.output_widget])
        hdr = urwid.Text("XFdown新UI测试版")
        hdr = urwid.AttrWrap(hdr, 'header')
        self.output_widget=footer = urwid.AttrWrap(urwid.Text('上下移动,空格选择,回车下载选中项目,Ctrl+C退出'),'footer')
        w = urwid.Frame(header=hdr, body=self.listbox ,footer=footer)

        return w
    def received_output(self,data):
      self.output_widget.set_text(data)
      


    def getSelected(self):
        selected=[]
        for index,item in enumerate(self.items):
          if item.get_state():
            selected.append(index)
        return selected


    def input_filter(self,key,raw):
      if key in (['enter'],['o']):
        self.key=key
        raise urwid.ExitMainLoop()
        # d=ListDialogDisplay('a',10,30,['a','b','c']).view
        # d = urwid.Overlay(d, self.view, 'center', 25, 'middle', 10)
        # self.loop.widget = d
      else:
        return key
    def main(self):
        self.view= self.setup_view()
        self.loop = urwid.MainLoop(self.view, self.palette, 
            input_filter = self.input_filter)
        # self.write_fd = self.loop.watch_pipe(self.received_output)
        self.loop.run()
        self.work()

    def work(self):
      if self.key==['enter']:
        xf.download(self.getSelected())
      elif self.key==['o']:
        xf.online_v(self.getSelected())
    
    
class DialogDisplay:
    palette = [
        ('body','black','light gray', 'standout'),
        ('border','black','dark blue'),
        ('shadow','white','black'),
        ('selectable','black', 'dark cyan'),
        ('focus','white','dark blue','bold'),
        ('focustext','light gray','dark blue'),
        ]
        
    def __init__(self, text, height, width, body=None):
        width = int(width)
        if width <= 0:
            width = ('relative', 80)
        height = int(height)
        if height <= 0:
            height = ('relative', 80)
    
        self.body = body
        if body is None:
            # fill space with nothing
            body = urwid.Filler(urwid.Divider(),'top')

        self.frame = urwid.Frame( body, focus_part='footer')
        if text is not None:
            self.frame.header = urwid.Pile( [urwid.Text(text),
                urwid.Divider()] )
        w = self.frame
        
        # pad area around listbox
        w = urwid.Padding(w, ('fixed left',2), ('fixed right',2))
        w = urwid.Filler(w, ('fixed top',1), ('fixed bottom',1))
        w = urwid.AttrWrap(w, 'body')
        
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
        
        self.view = w


    def add_buttons(self, buttons):
        l = []
        for name, exitcode in buttons:
            b = urwid.Button( name, self.button_press )
            b.exitcode = exitcode
            b = urwid.AttrWrap( b, 'selectable','focus' )
            l.append( b )
        self.buttons = urwid.GridFlow(l, 10, 3, 1, 'center')
        self.frame.footer = urwid.Pile( [ urwid.Divider(),
            self.buttons ], focus_item = 1)

    def button_press(self, button):
        raise DialogExit(button.exitcode)

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette)
        
        try:
            self.loop.run()
        except DialogExit, e:
            return self.on_exit( e.args[0] )
        
    def on_exit(self, exitcode):
        return exitcode, ""
class ListDialogDisplay(DialogDisplay):
    def __init__(self, text, height, width, items):
        self.items=[]
        l=[]
        for item in items:
            w = urwid.Text(item)
            w = urwid.AttrWrap(w, 'selectable','focus')
            self.items.append(w)
            l.append(w)

        lb = urwid.ListBox(l)
        lb = urwid.AttrWrap( lb, "selectable" )
        DialogDisplay.__init__(self, text, height, width, lb )
        
    

    def on_exit(self, exitcode):
        """Print the tag of the item selected."""
        if exitcode != 0:
            return exitcode, ""
        s = ""
        for i in self.items:
            if i.get_state():
                s = i.get_label()
                break
        return exitcode, s



def main():
    XFdownUi().main()
    
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

      main()
  except KeyboardInterrupt:
    print (" exit now.")
    sys.exit(2)
  except getopt.GetoptError as err:
    print(err)
    usage()
    sys.exit(2)
