* 简介

用python实现的基于webqq协议
http://lixian.qq.com/
的一个下载离线任务的程序
调用aria2下载
可实现多线程，断点续传等特性

* 截图

![gnome_terminal_screenshot](https://raw.github.com/kikyous/xfdown/beta/screenshot/xfdown.png)

* 安装:

```
git clone https://github.com/kikyous/xfdown.git
cd xfdown
python xfdown.py
```
如果系统没有urwid模块,到 http://excess.org/urwid/ 下载解压
`sudo python setup.py install`安装

或直接用系统包管理器安装
`sudo apt-get install python-urwid`

* 运行:

`python xfdown.py`

or

`python xfdown.py -h`
