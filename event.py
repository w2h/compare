#coding=utf-8

import wx.lib.newevent
import wx

FrameEvent, EVT_FRAME_EVENT = wx.lib.newevent.NewCommandEvent()
ToolBarEvent, EVT_TOOL_BAR = wx.lib.newevent.NewCommandEvent()
MenuBarEvent, EVT_MENU_BAR = wx.lib.newevent.NewEvent()

class FrameEventType(object):
    OPEN_FILE = 1
    CLOSE_PAGE = 2
    TREE_READY = 3

class ToolBarEventType(object):
    SWITCH_TEXT = 1

class EventManager(wx.EvtHandler):
    _instance = None
    @staticmethod
    def get_instance():
        if not EventManager._instance:
            EventManager._instance = EventManager()
            return EventManager._instance
        else:
            return EventManager._instance
    def __init__(self):
        wx.EvtHandler.__init__(self)