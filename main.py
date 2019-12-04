# -*- coding: utf-8 -*-


import wx,os
import wx.xrc
import sys
from page import PageManager
from data import PageData, CompareOption
from log import logger
from threadctrl import ThreadInstance
from menubar import MenuBar

leftPath=ur"D:\workspace\French\fr_client_proj\trunk\src\naruto.activity\src\com\tencent\morefun\naruto\plugin\activity".replace("\\","/")
# centerPath=ur"D:\workspace\German\de_client_proj\branches\DE_NarutoAlpha5.50\src\naruto.activity\src\com\tencent\morefun\naruto\plugin\activity".replace("\\","/")
centerPath = None
rightPath=ur"D:\workspace\German\de_client_proj\trunk\src\naruto.activity\src\com\tencent\morefun\naruto\plugin\activity".replace("\\","/")

# leftPath=ur"D:\workspace\Poland\pl_client_proj\branches\PL_NarutoAlpha3.39\src".replace("\\","/")
# centerPath=ur"D:\workspace\German\de_client_proj\branches\DE_NarutoAlpha3.17\src".replace("\\","/")
# rightPath=ur"D:\workspace\German\de_client_proj\branches\DE_NarutoAlpha5.50\src".replace("\\","/")

# leftPath = ur"http://tc-svn.tencent.com/narutoI18n/fr_client_proj/trunk/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity"
# centerPath = ur"http://tc-svn.tencent.com/narutoI18n/de_client_proj/branches/DE_NarutoAlpha5.50/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity"
# rightPath = ur"http://tc-svn.tencent.com/narutoI18n/de_client_proj/trunk/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity"


class MyFrame(wx.Frame):
    def __init__(self, parent,title,id=wx.ID_ANY):
        wx.Frame.__init__(self, parent, id, title, pos=wx.DefaultPosition,
                          size=wx.Size(1400, 800), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.rootBook = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition)

        PageManager.get_instance().setup(self.rootBook)
        # fileFormat = CompareOption.GetFileFormatByUrl(leftPath)
        # option = CompareOption.GetDefaultValue()
        # option.file_format = fileFormat
        # data = PageData(leftPath, centerPath, rightPath, option)
        # self.pageCtrl.create_page(data)
        self.Bind(wx.EVT_SIZE, self._on_size,self)
        self.Layout()

        self.menubar = MenuBar()

        self.SetMenuBar(self.menubar)

        self.Centre(wx.BOTH)

        self.thread_instance = ThreadInstance(self)
        self.thread_instance.start()

    def __del__(self):
        logger.close()
        pass


    def _on_size(self, evt):
        pos = self.rootBook.GetPosition()
        size = evt.GetSize()
        self.rootBook.SetSize(pos.x,pos.y, size.GetWidth(), size.GetHeight()-80)

import profile

def pro():
    path_l = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window\UILobbyTask.prefab".replace(
        "\\", "/")
    path_r = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window\UILobbyTask2.prefab".replace(
        "\\", "/")
    fileFormat = CompareOption.GetFileFormatByUrl(path_l)
    option = CompareOption.GetDefaultValue()
    option.file_format = fileFormat
    data = PageData(path_l, None, path_r, option)
    PageManager.get_instance().create_page(data, type)
if __name__ == '__main__':
    # str = "\n".join(sys.argv)
    app = wx.App()
    frame = MyFrame(None, title="Compare")
    operaType = ""
    path_l = ""
    path_c = ""
    path_r = ""
    path_d = ""
    type = 0
    if len(sys.argv) == 3:
        path_l = sys.argv[1].replace("\\", "/")
        path_r = sys.argv[2].replace("\\", "/")
        type = 1
    elif len(sys.argv) == 5:
        path_l = sys.argv[1].replace("\\", "/")
        path_c = sys.argv[2].replace("\\", "/")
        path_r = sys.argv[3].replace("\\", "/")
        path_d = sys.argv[4].replace("\\", "/")
        type = 2

    if type == 1:
        fileFormat = CompareOption.GetFileFormatByUrl(path_r)
        option = CompareOption.GetDefaultValue()
        option.file_format = fileFormat
        data = PageData(path_l, None, path_r, option)
        PageManager.get_instance().create_page(data, type)
        print "pathL:"+path_l
        print "pathR:"+path_r
        print "compare:-----------------------"
    elif type == 2:
        fileFormat = CompareOption.GetFileFormatByUrl(path_l)
        option = CompareOption.GetDefaultValue()
        option.file_format = fileFormat
        data = PageData(path_l, path_c, path_r, option)
        data.save_path = path_d
        PageManager.get_instance().create_page(data,type)
    frame.CreateStatusBar()
    frame.Show(True)
    # profile.run("pro()")
    # pro()
    app.MainLoop()


