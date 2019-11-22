#coding:utf-8
import wx

class MyFrame(wx.Frame):
    def __init__(self,parent):
        wx.Frame.__init__(self, parent)


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.Show()
    app.MainLoop()