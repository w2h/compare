#coding:utf-8
import wx
from event import *

class MenuBar(wx.MenuBar):
    SESSION = 1
    NEW_SESSION = 11
    MERGE_INFO = 12
    NEW_SESSION_MERGE = 111
    NEW_SESSION_COMPARE = 112
    EDIT = 2
    EDIT_EXPANDALL = 21
    EDIT_COLLAPSEALL = 22
    def __init__(self):
        wx.MenuBar.__init__(self, style=0)
        self.session_menu = wx.Menu()
        self.Append(self.session_menu, u"任务")
        self.new_session_menu = wx.Menu()
        self.session_menu.AppendSubMenu(self.new_session_menu, u"新任务")
        self.session_menu.Append(MenuBar.MERGE_INFO, u"合并结果")
        self.new_session_menu.Append(MenuBar.NEW_SESSION_COMPARE, u"对比")
        self.new_session_menu.Append(MenuBar.NEW_SESSION_MERGE, u"合并")
        self.edit_menu = wx.Menu()
        self.Append(self.edit_menu, u"编辑")
        self.edit_menu.Append(MenuBar.EDIT_EXPANDALL, u"展开所有")
        self.edit_menu.Append(MenuBar.EDIT_COLLAPSEALL, u"折叠所有")
        self.Bind(wx.EVT_MENU, self._menu_handler)

    def _menu_handler(self,evt):
        evt = MenuBarEvent(data=evt.GetId())
        EventManager.get_instance().ProcessEvent(evt)



