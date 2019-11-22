#coding:utf-8


import wx,os
import wx.xrc
import wx.stc
import sys
from event import *
from data import *
from sorttreectrl import *
from compare import *
from pathutils import get_parent_path
from textctrl import CodeTextCtrl
from const import FileFormat
from codeutil import check_as_file_error,CodeError
from menubar import MenuBar

class ToolBar(wx.Panel):
    GO_UP = "go_up"
    GO_DOWN = "go_down"
    COMMENT = "comment"
    DEEP_COMPARE="deep_compare"
    BLANK_LINE="blank_line"
    RE_DO = "redo"
    UN_DO = "undo"
    SAVE = "save"
    COMPARE = "compare"
    CLOSE = "close"
    FORMAT = "format"
    CHECK_ERROR = "check_error"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    FILE_FILTER = "file_filter"
    MERGE_FILTER = "merge_filter"
    SHOW_CONFLICT = "show_conflict"

    def __init__(self,parent):
        wx.Panel.__init__(self, parent,id=wx.ID_ANY,size=wx.Size(1000,40))
        self._init_view()

    def _init_view(self):
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.comment_btn = wx.ToggleButton(self, id=wx.ID_ANY, label="注释", size=wx.Size(40, 30), pos=wx.Point(25, 10),
                                           name=ToolBar.COMMENT)
        self.deepcompare_btn = wx.ToggleButton(self, id=wx.ID_ANY, label="深度对比", size=wx.Size(80, 30),
                                               pos=wx.Point(25, 10), name=ToolBar.DEEP_COMPARE)
        self.blank_line_btn = wx.ToggleButton(self, id=wx.ID_ANY, label="空白行", size=wx.Size(60, 30),
                                              pos=wx.Point(25, 10), name=ToolBar.BLANK_LINE)
        self.format_btn = wx.ComboBox(self, id=wx.ID_ANY,
                                      choices=[FileFormat.NormalText, FileFormat.XML, FileFormat.AS],
                                      size=wx.Size(120, 30), pos=wx.Point(25, 10), name=ToolBar.FORMAT)
        self.format_btn.SetEditable(False)
        self.check_error_btn = wx.Button(self, id=wx.ID_ANY, label="检查错误", size=wx.Size(80, 30), pos=wx.Point(25, 10),
                                         name=ToolBar.CHECK_ERROR)
        self.up_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_GO_UP), pos=wx.Point(10, 10),
                                      size=wx.Size(30, 30), name=ToolBar.GO_UP)
        self.down_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN), pos=wx.Point(10, 10),
                                        size=wx.Size(30, 30), name=ToolBar.GO_DOWN)
        self.expand_btn = wx.Button(self, id=wx.ID_ANY, label="展开", size=wx.Size(40, 30), pos=wx.Point(25, 10),
                                    name=ToolBar.EXPAND)
        self.collapse_btn = wx.Button(self, id=wx.ID_ANY, label="折叠", size=wx.Size(40, 30), pos=wx.Point(25, 10),
                                      name=ToolBar.COLLAPSE)
        self.redo_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_REDO), pos=wx.Point(10, 10),
                                        size=wx.Size(30, 30), name=ToolBar.RE_DO)
        self.redo_btn.SetToolTip("重做")
        self.undo_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_UNDO), pos=wx.Point(10, 10),
                                        size=wx.Size(30, 30), name=ToolBar.UN_DO)
        self.undo_btn.SetToolTip("撤销")
        self.save_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE), pos=wx.Point(10, 10),
                                        size=wx.Size(30, 30), name=ToolBar.SAVE)
        self.save_btn.SetToolTip("保存")
        self.compare_btn = wx.Button(self, label="对比", pos=wx.Point(10, 10), size=wx.Size(40, 30), name=ToolBar.COMPARE)

        self.filter = wx.ComboBox(self, id=wx.ID_ANY,
                                  choices=[".txt", ".xml", ".as"],
                                  size=wx.Size(120, 30), pos=wx.Point(25, 10), name=ToolBar.FILE_FILTER)

        self.merge_filter = wx.ComboBox(self, id=wx.ID_ANY,
                                  choices=[CompareFilter.ALL, CompareFilter.MERGEABLE, CompareFilter.CONFLICT, CompareFilter.SAME],
                                  size=wx.Size(120, 30), pos=wx.Point(25, 10), name=ToolBar.MERGE_FILTER)
        self.merge_filter.SetValue(CompareFilter.ALL)
        self.merge_filter.SetEditable(False)
        self.show_conflict_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_WARNING), pos=wx.Point(10, 10),
                                         size=wx.Size(30, 30), name=ToolBar.SHOW_CONFLICT)
        self.show_conflict_btn.SetToolTip("有冲突")
        self.close_btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_CLOSE), pos=wx.Point(10, 10),
                                         size=wx.Size(30, 30), name=ToolBar.CLOSE)
        self.close_btn.SetToolTip("关闭")
        line = wx.StaticLine(self, style=wx.LI_VERTICAL, size=wx.Size(3, 30), pos=wx.Point(15, 10))
        # print line.GetEffectiveMinSize()
        sizer = self.sizer
        sizer.Add(line, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.comment_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.deepcompare_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.blank_line_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.format_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.check_error_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.merge_filter, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.up_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.down_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.expand_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.collapse_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.redo_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.undo_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.compare_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.filter, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        sizer.Add(self.show_conflict_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.save_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(5)
        sizer.Add(self.close_btn, 0, wx.FIXED_MINSIZE, 5)
        sizer.AddSpacer(10)
        # sizer.FitInside(self.comment_button)
        self.SetSizer(sizer)
        sizer.Layout()

    def show_conflict(self,b):
        self.show_conflict_btn.Enable(b)
        self.save_btn.Enable(not b)

    def show_save(self,b):
        self.save_btn.Enable(b)

    def destory(self):
        self.DestroyChildren()
        self.Destory()
        self._remove_event()
        self._page_data = None
        pass

    def enable(self):
        items = self.sizer.GetChildren()
        for sizeItem in items:
            window = sizeItem.GetWindow()
            if window:
                window.Enable()
    def disable(self):
        items = self.sizer.GetChildren()
        for sizeItem in items:
            window = sizeItem.GetWindow()
            if window and window.GetName() != ToolBar.CLOSE:
                window.Disable()

    def set_show(self,btnArr):
        # self.sizer.ShowItems(True)
        items = self.sizer.GetChildren()
        for sizeItem in items:
            window = sizeItem.GetWindow()
            if window:
                self.sizer.Show(window,  window.GetName() in btnArr)

    def set_pagedata(self,pageData):
        self._page_data = pageData
        self.comment_btn.SetValue(pageData.cmp_option.ignore_comment)
        self.blank_line_btn.SetValue(pageData.cmp_option.ignore_blank)
        self.deepcompare_btn.SetValue(pageData.cmp_option.deep_compare)
        self.format_btn.SetValue(pageData.cmp_option.file_format)
        self.filter.SetValue(pageData.cmp_option.filter.filterString)


class Page(wx.Panel):
    COMPARE_PAGE = 1
    MERGE_PAGE = 2
    def __init__(self,parent,page_data=None):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self._page_data = page_data
        self.focus_obj = None

    def getdata(self):
        return self._page_data
    def setdata(self, data):
        self._page_data = data
        self._update_ui()

    def _update_ui(self):
        pass

    def destory(self):
        self.Destroy()

    def __del__(self):
        print "deled"

    def get_type(self):
        raise Exception("this function must be overload")
class TwoSidePage(Page):
    '''
    两方对比界面
    '''
    def __init__(self, parent, page_data=None):
        Page.__init__(self, parent, page_data)
        self.__init_ui__()
        self.__init_event__()
        self._page_data = page_data
        self._update_ui()

    def __init_ui__(self):
        self.leftPath = ""
        self.rightPath = ""

        self.tree_ctrl = TreeController()

        self.rootSize = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = ToolBar(self)
        bookSizer = wx.BoxSizer(wx.VERTICAL)
        bookSizer.AddSpacer(10)
        bookSizer.Add(self.toolbar, -1, wx.FIXED_MINSIZE, 5)
        bookSizer.FitInside(self.toolbar)
        bookTopSizer = wx.BoxSizer(wx.HORIZONTAL)

        # 初始化最左边的面板
        self.leftPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        leftPanelSizer = self.leftPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.leftPathText = wx.TextCtrl(self.leftPanel, wx.ID_ANY, self.leftPath, wx.DefaultPosition,
                                        wx.DefaultSize, wx.TE_PROCESS_ENTER)
        leftPanelSizer.Add(self.leftPathText, 0, wx.ALL | wx.EXPAND, 5)
        # 生成文件列表
        self.leftTree = SortTreeCtr(self.leftPanel, self.leftPath)
        self.tree_ctrl.register_tree(self.leftTree)
        # 生成对比的文本框
        self.leftText = CodeTextCtrl(self.leftPanel, wx.DefaultSize)
        leftPanelSizer.Add(self.leftText.text, 1, wx.ALL | wx.EXPAND, 5)
        leftPanelSizer.Add(self.leftTree, 1, wx.ALL | wx.EXPAND, 5)
        leftPanelSizer.Hide(self.leftTree)
        leftPanelSizer.Layout()
        self.leftPanel.SetSizer(leftPanelSizer)
        self.leftPanel.Layout()
        leftPanelSizer.Fit(self.leftPanel)
        bookTopSizer.Add(self.leftPanel, 1, wx.EXPAND | wx.ALL, 5)

        # 初始化最右边的面板
        self.rightPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        rightPanelSizer = self.rightPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.rightPathText = wx.TextCtrl(self.rightPanel, wx.ID_ANY, self.rightPath, wx.DefaultPosition,
                                         wx.DefaultSize, wx.TE_PROCESS_ENTER)
        rightPanelSizer.Add(self.rightPathText, 0, wx.ALL | wx.EXPAND, 5)

        self.rightText = CodeTextCtrl(self.rightPanel, wx.DefaultSize)
        rightPanelSizer.Add(self.rightText.text, 1, wx.ALL | wx.EXPAND, 5)
        self.rightTree = SortTreeCtr(self.rightPanel, self.rightPath)
        self.tree_ctrl.register_tree(self.rightTree)
        rightPanelSizer.Add(self.rightTree, 1, wx.ALL | wx.EXPAND, 5)
        rightPanelSizer.Hide(self.rightTree)
        rightPanelSizer.Layout()

        self.rightPanel.SetSizer(rightPanelSizer)
        self.rightPanel.Layout()
        rightPanelSizer.Fit(self.rightPanel)
        bookTopSizer.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)

        bookSizer.Add(bookTopSizer, 2, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bookSizer)
        self.Layout()

    def destory(self):
        self.__remove_event__()
        self.leftPathText.Destroy()
        self.rightPathText.Destroy()
        self.leftText.destory()
        self.rightText.destory()
        self.toolbar.destory()
        self.leftPanel.Destroy()
        self.leftPanelSizer.Destroy()
        self.rightPanel.Destroy()
        self.rightPanelSizer.Destroy()
        self.leftTree.Destroy()
        self.rightTree.Destroy()
        del self._page_data
        del self.tree_ctrl
        Page.destory(self)


    def __init_event__(self):
        self.Bind(wx.EVT_TEXT_ENTER, self._on_left_path, self.leftPathText)
        self.Bind(wx.EVT_TEXT_ENTER, self._on_right_path, self.rightPathText)

        self.leftText.text.Bind(stc.EVT_STC_URIDROPPED, self._on_left_file_drop)
        self.rightText.text.Bind(stc.EVT_STC_URIDROPPED, self._on_right_file_drop)
        self.leftText.text.Bind(wx.EVT_SET_FOCUS, self._on_left_text_focus)
        self.rightText.text.Bind(wx.EVT_SET_FOCUS, self._on_right_text_focus)

    def __remove_event__(self):
        self.Unbind(wx.EVT_TEXT_ENTER, self.leftPathText)
        self.Unbind(wx.EVT_TEXT_ENTER, self.rightPathText)
        self.leftText.text.Unbind(wx.EVT_SET_FOCUS)
        self.leftText.text.Unbind(stc.EVT_STC_URIDROPPED)
        self.rightText.text.Unbind(wx.EVT_SET_FOCUS)
        self.rightText.text.Unbind(stc.EVT_STC_URIDROPPED)


    def _on_left_file_drop(self, evt):
        url = evt.GetText()
        if self._page_data:
            if self._page_data.leftPath != url:
                self._page_data.leftPath = url
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(url)
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(url, None, None, option)

    def _on_right_file_drop(self, evt):
        url = evt.GetText()
        if self._page_data:
            if self._page_data.rightPath != url:
                self._page_data.rightPath = url
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(url)
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(None, None, url, option)

    def _on_left_text_focus(self,evt):
        self.focus_obj = self.leftText.text
        evt.Skip()

    def _on_right_text_focus(self, evt):
        self.focus_obj = self.rightText.text
        evt.Skip()


    def _update_ui(self):
        if self._page_data != None:
            self.toolbar.set_pagedata(self._page_data)

            self.leftPath = self._page_data.leftPath
            self.centerPath = self._page_data.centerPath
            self.rightPath = self._page_data.rightPath

            self.leftPathText.SetLabelText(self.leftPath)
            self.leftTree.set_path(self.leftPath)

            if is_url_dir(self.leftPath):
                self.leftPanelSizer.Hide(self.leftText.text)
                self.leftPanelSizer.Show(self.leftTree)
            else:
                self.leftPanelSizer.Hide(self.leftTree)
                self.leftPanelSizer.Show(self.leftText.text)

            self.leftPanelSizer.Layout()
            self.leftPanel.Layout()

            # 初始化最右边的面板
            self.rightPathText.SetLabelText(self.rightPath)
            self.rightTree.set_path(self.rightPath)
            if is_url_dir(self.rightPath):
                self.rightPanelSizer.Hide(self.rightText.text)
                self.rightPanelSizer.Show(self.rightTree)
            else:
                self.rightPanelSizer.Hide(self.rightTree)
                self.rightPanelSizer.Show(self.rightText.text)

            self.rightPanelSizer.Layout()
            self.rightPanel.Layout()

            self.Layout()

            if not is_url_dir(self.leftPath):
                self.compare_ctrl = CompareTextCtrl(self.leftText, self.rightText, self._page_data)
                self.toolbar.format_btn.SetValue(self._page_data.cmp_option.file_format)
                self.toolbar.comment_btn.SetValue(self._page_data.cmp_option.ignore_comment)
                self.toolbar.blank_line_btn.SetValue(self._page_data.cmp_option.ignore_blank)
                self.toolbar.deepcompare_btn.SetValue(self._page_data.cmp_option.deep_compare)
                self.toolbar.set_show([ToolBar.COMMENT, ToolBar.GO_DOWN, ToolBar.GO_UP, ToolBar.BLANK_LINE, ToolBar.RE_DO, ToolBar.UN_DO, ToolBar.SAVE, ToolBar.COMPARE,
                                       ToolBar.CLOSE, ToolBar.FORMAT])
            else:
                self.compare_ctrl = CompareDirCtrl(self.leftTree, self.rightTree, self._page_data)
                self.leftRadionbtn.Enable()
                self.rightRadionbtn.Enable()
                self.toolbar.set_show([ToolBar.COMMENT, ToolBar.GO_DOWN, ToolBar.GO_UP, ToolBar.BLANK_LINE, ToolBar.COMPARE,
                                       ToolBar.CLOSE, ToolBar.FORMAT, ToolBar.COLLAPSE, ToolBar.EXPAND, ToolBar.FILE_FILTER])
            self.toolbar.enable()
            self.toolbar.show_save(False)
            self.toolbar.Layout()
        else:
            self.toolbar.disable()

    def get_type(self):
        return Page.COMPARE_PAGE

    def _on_left_path(self,evt):
        if self._page_data:
            if self._page_data.leftPath != self.leftPathText.GetValue():
                self._page_data.leftPath = self.leftPathText.GetValue()
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(self.leftPathText.GetValue())
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(self.leftPathText.GetValue(), None, None, option)
    def _on_right_path(self,evt):
        if self._page_data:
            if self._page_data.rightPath != self.rightPathText.GetValue():
                self._page_data.rightPath = self.rightPathText.GetValue()
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(self.rightPathText.GetValue())
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(None, None, self.rightPathText.GetValue(), option)

    def _refreshPageData(self):
        if self._page_data.leftPath and self._page_data.rightPath:
            self._update_ui()


    def expand_all(self):
        self.leftTree.ExpandAll()
        self.rightTree.ExpandAll()

    def collapse_all(self):
        self.leftTree.CollapseAll()
        self.rightTree.CollapseAll()

class ThreeSidePage(Page):
    '''
    三方对比界面
    '''
    def __init__(self, parent, page_data=None):
        Page.__init__(self,parent,page_data)
        self.__init_ui__()
        self.__init_event__()
        self._page_data = page_data
        self._update_ui()

    def __init_ui__(self):
        self.leftPath = ""
        self.centerPath = ""
        self.rightPath = ""

        self.tree_ctrl = TreeController()

        self.rootSize = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = ToolBar(self)
        bookSizer = wx.BoxSizer(wx.VERTICAL)
        bookSizer.AddSpacer(10)
        bookSizer.Add(self.toolbar, -1, wx.FIXED_MINSIZE, 5)
        bookSizer.FitInside(self.toolbar)
        bookTopSizer = wx.BoxSizer(wx.HORIZONTAL)

        # 初始化最左边的面板
        self.leftPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        leftPanelSizer = self.leftPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.leftPathText = wx.TextCtrl(self.leftPanel, wx.ID_ANY, self.leftPath, wx.DefaultPosition,
                                        wx.DefaultSize, wx.TE_PROCESS_ENTER)
        leftPanelSizer.Add(self.leftPathText, 0, wx.ALL | wx.EXPAND, 5)
        # 生成文件列表
        self.leftTree = SortTreeCtr(self.leftPanel, self.leftPath)
        self.tree_ctrl.register_tree(self.leftTree)
        # 生成对比的文本框
        self.leftText = CodeTextCtrl(self.leftPanel, wx.DefaultSize)
        leftPanelSizer.Add(self.leftText.text, 1, wx.ALL | wx.EXPAND, 5)
        leftPanelSizer.Add(self.leftTree, 1, wx.ALL | wx.EXPAND, 5)
        leftPanelSizer.Hide(self.leftTree)
        leftPanelSizer.Layout()
        self.leftPanel.SetSizer(leftPanelSizer)
        self.leftPanel.Layout()
        leftPanelSizer.Fit(self.leftPanel)
        bookTopSizer.Add(self.leftPanel, 1, wx.EXPAND | wx.ALL, 5)

        # 初始化中间的面板
        self.centerPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        centerPanelSizer = self.centerPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.centerPathText = wx.TextCtrl(self.centerPanel, wx.ID_ANY, self.centerPath, wx.DefaultPosition,
                                          wx.DefaultSize, wx.TE_PROCESS_ENTER)
        centerPanelSizer.Add(self.centerPathText, 0, wx.ALL | wx.EXPAND, 5)

        self.centerText = CodeTextCtrl(self.centerPanel, wx.DefaultSize)
        centerPanelSizer.Add(self.centerText.text, 1, wx.ALL | wx.EXPAND, 5)
        self.centerTree = SortTreeCtr(self.centerPanel, self.centerPath)
        self.tree_ctrl.register_tree(self.centerTree)
        centerPanelSizer.Add(self.centerTree, 1, wx.ALL | wx.EXPAND, 5)
        centerPanelSizer.Hide(self.centerTree)
        centerPanelSizer.Layout()

        self.centerPanel.SetSizer(centerPanelSizer)
        self.centerPanel.Layout()
        centerPanelSizer.Fit(self.centerPanel)
        bookTopSizer.Add(self.centerPanel, 1, wx.EXPAND | wx.ALL, 5)

        # 初始化最右边的面板
        self.rightPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        rightPanelSizer = self.rightPanelSizer = wx.BoxSizer(wx.VERTICAL)

        self.rightPathText = wx.TextCtrl(self.rightPanel, wx.ID_ANY, self.rightPath, wx.DefaultPosition,
                                         wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self._on_right_path, self.rightPathText)
        rightPanelSizer.Add(self.rightPathText, 0, wx.ALL | wx.EXPAND, 5)

        self.rightText = CodeTextCtrl(self.rightPanel, wx.DefaultSize)
        rightPanelSizer.Add(self.rightText.text, 1, wx.ALL | wx.EXPAND, 5)
        self.rightTree = SortTreeCtr(self.rightPanel, self.rightPath)
        self.tree_ctrl.register_tree(self.rightTree)
        rightPanelSizer.Add(self.rightTree, 1, wx.ALL | wx.EXPAND, 5)
        rightPanelSizer.Hide(self.rightTree)
        rightPanelSizer.Layout()

        self.rightPanel.SetSizer(rightPanelSizer)
        self.rightPanel.Layout()
        rightPanelSizer.Fit(self.rightPanel)
        bookTopSizer.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)


        bookSizer.Add(bookTopSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.downPanel = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.downText = CodeTextCtrl(self.downPanel, wx.DefaultSize)
        mergeToSizer = wx.BoxSizer(wx.HORIZONTAL)
        mergeLabel = wx.StaticText(self.downPanel,label="Merge to:",size=wx.Size(70,22),pos=wx.Point(0,5))
        mergeToSizer.Add(mergeLabel, 0, wx.FIXED_MINSIZE,5)
        self.leftRadionbtn = wx.RadioButton(self.downPanel, label = "Left",size=wx.Size(60,22))
        mergeToSizer.Add(self.leftRadionbtn, 0, wx.FIXED_MINSIZE,5)
        self.rightRadionbtn = wx.RadioButton(self.downPanel, label = "Right",size=wx.Size(60,22))
        mergeToSizer.Add(self.rightRadionbtn, 0, wx.FIXED_MINSIZE,5)
        # self.otherRadionbtn = wx.RadioButton(self.downPanel, label = "Right",size=wx.Size(100,30))
        downPanelSizer = wx.BoxSizer(wx.VERTICAL)
        downPanelSizer.Add(mergeToSizer, 0, wx.FIXED_MINSIZE)
        downPanelSizer.Add(self.downText.text, 1, wx.ALL | wx.EXPAND, 5)
        self.downPanel.SetSizer(downPanelSizer)
        self.downPanel.Layout()
        downPanelSizer.Fit(self.downPanel)
        bookSizer.Add(self.downPanel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bookSizer)
        self.Layout()

    def _update_ui(self):
        if self._page_data != None:
            self.toolbar.set_pagedata(self._page_data)

            self.leftPath = self._page_data.leftPath
            self.centerPath = self._page_data.centerPath
            self.rightPath = self._page_data.rightPath

            self.leftPathText.SetLabelText(self.leftPath)
            self.leftTree.refresh_filters(self._page_data.cmp_option.filter)
            self.leftTree.set_path(self.leftPath)

            if is_url_dir(self.leftPath):
                self.leftPanelSizer.Hide(self.leftText.text)
                self.leftPanelSizer.Show(self.leftTree)
            else:
                self.leftPanelSizer.Hide(self.leftTree)
                self.leftPanelSizer.Show(self.leftText.text)

            self.leftPanelSizer.Layout()
            self.leftPanel.Layout()

            # 初始化中间的面板
            self.centerPathText.SetLabelText(self.centerPath)
            self.centerTree.refresh_filters(self._page_data.cmp_option.filter)
            self.centerTree.set_path(self.centerPath)
            if is_url_dir(self.centerPath):
                self.centerPanelSizer.Hide(self.centerText.text)
                self.centerPanelSizer.Show(self.centerTree)
            else:
                self.centerPanelSizer.Hide(self.centerTree)
                self.centerPanelSizer.Show(self.centerText.text)

            self.centerPanelSizer.Layout()
            self.centerPanel.Layout()

            # 初始化最右边的面板
            self.rightPathText.SetLabelText(self.rightPath)
            self.rightTree.refresh_filters(self._page_data.cmp_option.filter)
            self.rightTree.set_path(self.rightPath)
            if is_url_dir(self.rightPath):
                self.rightPanelSizer.Hide(self.rightText.text)
                self.rightPanelSizer.Show(self.rightTree)
            else:
                self.rightPanelSizer.Hide(self.rightTree)
                self.rightPanelSizer.Show(self.rightText.text)

            self.rightPanelSizer.Layout()
            self.rightPanel.Layout()

            self.leftRadionbtn.SetValue(self._page_data.cmp_option.merge_option == CompareOption.MERGE_TO_LEFT)
            self.rightRadionbtn.SetValue(self._page_data.cmp_option.merge_option == CompareOption.MERGE_TO_RIGHT)

            self.downPanel.Layout()
            self.Layout()

            self.toolbar.enable()
            if not is_url_dir(self.leftPath):
                self.toolbar.format_btn.SetValue(self._page_data.cmp_option.file_format)
                self.toolbar.comment_btn.SetValue(self._page_data.cmp_option.ignore_comment)
                self.toolbar.blank_line_btn.SetValue(self._page_data.cmp_option.ignore_blank)
                self.toolbar.deepcompare_btn.SetValue(self._page_data.cmp_option.deep_compare)
                self.leftRadionbtn.Disable()
                self.rightRadionbtn.Disable()
                self.toolbar.set_show(
                    [ToolBar.COMMENT, ToolBar.GO_DOWN, ToolBar.GO_UP, ToolBar.BLANK_LINE,
                     ToolBar.RE_DO, ToolBar.UN_DO, ToolBar.SAVE, ToolBar.COMPARE,
                     ToolBar.CLOSE, ToolBar.FORMAT, ToolBar.CHECK_ERROR, ToolBar.SHOW_CONFLICT])
                self.compare_ctrl = MergeTextCtrl(self.leftText, self.centerText, self.rightText, self.downText,
                                                  self._page_data)
                self.toolbar.show_conflict(self.compare_ctrl.has_conflict())


            else:
                self.leftRadionbtn.Enable()
                self.rightRadionbtn.Enable()
                self.toolbar.set_show(
                    [ToolBar.COMMENT, ToolBar.GO_DOWN, ToolBar.GO_UP, ToolBar.BLANK_LINE,
                     ToolBar.SAVE, ToolBar.COMPARE,
                     ToolBar.CLOSE, ToolBar.FORMAT, ToolBar.FILE_FILTER, ToolBar.COLLAPSE, ToolBar.EXPAND, ToolBar.MERGE_FILTER])
                self.compare_ctrl = MergeDirCtrl(self.leftTree, self.centerTree, self.rightTree, self._page_data)

        else:
            self.toolbar.disable()

    def get_type(self):
        return Page.MERGE_PAGE

    def destory(self):
        self.__remove_event__()
        self.leftPathText.Destory()
        self.rightPathText.Destory()
        self.centerPathText.Destory()
        self.leftText.destory()
        self.centerText.destory()
        self.rightText.destory()
        self.downText.destory()
        self.toolbar.destory()
        self.leftTree.Destroy()
        self.centerTree.Destroy()
        self.rightTree.Destroy()
        self.leftPanel.Destroy()
        self.leftPanelSizer.Destroy()
        self.centerPanel.Destroy()
        self.centerPanelSizer.Destroy()
        self.rightPanel.Destroy()
        self.rightPanelSizer.Destroy()
        self.downPanel.Destroy()

        del self._page_data
        del self.tree_ctrl
        Page.destory(self)

    def __init_event__(self):
        self.downPanel.Bind(wx.EVT_RADIOBUTTON, self._on_output_path_change)
        self.Bind(wx.EVT_TEXT_ENTER, self._on_left_path, self.leftPathText)
        self.Bind(wx.EVT_TEXT_ENTER, self._on_center_path, self.centerPathText)
        self.Bind(wx.EVT_TEXT_ENTER, self._on_right_path, self.rightPathText)

    def __remove_event__(self):
        self.downPanel.Unbind(wx.EVT_RADIOBUTTON)
        self.Bind(wx.EVT_TEXT_ENTER, self.leftPathText)
        self.Bind(wx.EVT_TEXT_ENTER, self.centerPathText)
        self.Bind(wx.EVT_TEXT_ENTER, self.rightPathText)

    def _on_output_path_change(self, evt):
        obj = evt.GetEventObject()
        if obj is self.leftRadionbtn:
            self.compare_ctrl.set_output_path(self._page_data.leftPath)
            self._page_data.cmp_option.merge_option = CompareOption.MERGE_TO_LEFT
        else:
            self.compare_ctrl.set_output_path(self._page_data.rightPath)
            self._page_data.cmp_option.merge_option = CompareOption.MERGE_TO_RIGHT

    def _on_left_path(self,evt):
        if self._page_data:
            if self._page_data.leftPath != self.leftPathText.GetValue():
                self._page_data.leftPath = self.leftPathText.GetValue()
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(self.leftPathText.GetValue())
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(self.leftPathText.GetValue(), None, None, option)
    def _on_center_path(self):
        if self._page_data:
            if self._page_data.centerPath != self.centerPathText.GetValue():
                self._page_data.centerPath = self.centerPathText.GetValue()
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(self.centerPathText.GetValue())
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(None, self.centerPathText.GetValue(), None, option)
    def _on_right_path(self):
        if self._page_data:
            if self._page_data.rightPath != self.rightPathText.GetValue():
                self._page_data.rightPath = self.rightPathText.GetValue()
                self._refreshPageData()
        else:
            fileFormat = CompareOption.GetFileFormatByUrl(self.rightPathText.GetValue())
            option = CompareOption.GetDefaultValue()
            option.file_format = fileFormat
            self._page_data = PageData(None, None, self.rightPathText.GetValue(), option)

    def _refreshPageData(self):
        if self._page_data.leftPath and self._page_data.centerPath and self._page_data.rightPath:
            self._update_ui()

    def expand_all(self):
        self.leftTree.ExpandAll()
        self.centerTree.ExpandAll()
        self.rightTree.ExpandAll()

    def collapse_all(self):
        self.leftTree.CollapseAll()
        self.centerTree.CollapseAll()
        self.rightTree.CollapseAll()



class PageController(object):
    def __init__(self, page):
        self.page = page
        self._init_handler()
        self._init_event()

    def _init_event(self):
        self.page.toolbar.Bind(wx.EVT_TOGGLEBUTTON, self._toolbar_handler)
        self.page.toolbar.Bind(wx.EVT_BUTTON, self._toolbar_handler)
        self.page.toolbar.Bind(wx.EVT_COMBOBOX, self._toolbar_handler)

    def _remove_event(self):
        self.page.toolbar.Unbind(wx.EVT_TOGGLEBUTTON)
        self.page.toolbar.Unbind(wx.EVT_BUTTON)
        self.page.toolbar.Unbind(wx.EVT_COMBOBOX)


    def _init_handler(self):
        self._tool_function_dic = {}
        self._tool_function_dic[ToolBar.RE_DO] = self._toolbar_redo
        self._tool_function_dic[ToolBar.UN_DO] = self._toolbar_undo
        self._tool_function_dic[ToolBar.SAVE] = self._toolbar_save
        self._tool_function_dic[ToolBar.COMPARE] = self._toolbar_merge
        self._tool_function_dic[ToolBar.GO_UP] = self._toolbar_go_up
        self._tool_function_dic[ToolBar.GO_DOWN] = self._toolbar_go_down
        self._tool_function_dic[ToolBar.CLOSE] = self._toolbar_close
        self._tool_function_dic[ToolBar.DEEP_COMPARE] = self._deep_compre
        self._tool_function_dic[ToolBar.COMMENT] = self._comment_compare
        self._tool_function_dic[ToolBar.BLANK_LINE] = self._blank_line_switch
        self._tool_function_dic[ToolBar.FORMAT] = self._format_handler
        self._tool_function_dic[ToolBar.CHECK_ERROR] = self._check_error
        self._tool_function_dic[ToolBar.EXPAND] = self.expand_all
        self._tool_function_dic[ToolBar.COLLAPSE] = self.collapse_all
        self._tool_function_dic[ToolBar.FILE_FILTER] = self._file_filter_handler
        self._tool_function_dic[ToolBar.MERGE_FILTER] = self._merge_filter_handler
        self._tool_function_dic[ToolBar.SHOW_CONFLICT] = self._show_conflict_handler

    def destory(self):
        self._remove_event()
        self._tool_function_dic.clear()

    def _merge_filter_handler(self,evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        self.page.compare_ctrl.refresh_filter(value)

    def _show_conflict_handler(self, evt):
        self.page.toolbar.show_conflict(False)

    def _toolbar_handler(self,evt):
        btn = evt.GetEventObject()
        func = self._tool_function_dic[btn.GetName()]
        func(evt)

    def _format_handler(self, evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        self.page.getdata().cmp_option.file_format = value
        self.page.compare_ctrl.refresh_compare(self.page.getdata().cmp_option)

    def _file_filter_handler(self, evt):
        btn = evt.data.GetEventObject()
        value = btn.GetValue()
        self.page.getdata().cmp_option.filter = FilterData(value)
        self.page.compare_ctrl.refresh_compare(self.page.getdata().cmp_option)


    def _toggle_btn_handler(self, evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        func = self._tool_function_dic[btn.GetName()]
        func(evt, value)

    def _blank_line_switch(self, evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        self.page.getdata().cmp_option.ignore_blank = value
        self.page.compare_ctrl.refresh_compare(self.page.getdata().cmp_option)

    def _deep_compre(self, evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        self.page.getdata().cmp_option.deep_compare = value
        self.page.compare_ctrl.refresh_compare(self.page.getdata().cmp_option)

    def _comment_compare(self, evt):
        btn = evt.GetEventObject()
        value = btn.GetValue()
        self.page.getdata().cmp_option.ignore_comment = value
        self.page.compare_ctrl.refresh_compare(self.page.getdata().cmp_option)

    def _toolbar_redo(self, evt):
        text = self.page.focus_obj
        if text:
            text.Redo()

    def _toolbar_undo(self, evt):
        text = self.page.focus_obj
        if text:
            text.Undo()

    def _toolbar_merge(self, evt):
        print "merge"

    def _toolbar_go_up(self, evt):
        self.page.compare_ctrl.last_selection()

    def _toolbar_go_down(self, evt):
        self.page.compare_ctrl.next_selection()

    def _toolbar_save(self, evt):
        self.page.compare_ctrl.save()
        index = PageManager.get_instance().notebook.FindPage(self.page)
        PageManager.get_instance().notebook.SetPageText(index, self.page.getdata().get_label())

    def _check_error(self, evt):
        state = check_as_file_error(self.page.downText)
        msg = CodeError.get_state_msg(state)
        dlg = wx.MessageDialog(self.page, msg, "Confirm", wx.OK)
        dlg.ShowModal()

    def expand_all(self,evt):
        self.page.expand_all()

    def collapse_all(self,evt):
        self.page.collapse_all()

    def _toolbar_close(self, evt=None):
        PageManager.get_instance().remove_page(self.page)

class TwoSidePageController(PageController):
    def _init_event(self):
        PageController._init_event(self)
        self.page.leftText.text.Bind(stc.EVT_STC_SAVEPOINTLEFT, self._on_save_point_left)
        self.page.leftText.text.Bind(stc.EVT_STC_SAVEPOINTREACHED, self._on_save_point_reached)
        self.page.rightText.text.Bind(stc.EVT_STC_SAVEPOINTLEFT, self._on_save_point_left)
        self.page.rightText.text.Bind(stc.EVT_STC_SAVEPOINTREACHED, self._on_save_point_reached)
        self.page.leftText.text.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.page.rightText.text.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _remove_event(self):
        PageController._remove_event(self)
        self.page.leftText.text.Unbind(stc.EVT_STC_SAVEPOINTLEFT)
        self.page.leftText.text.Unbind(stc.EVT_STC_SAVEPOINTREACHED)
        self.page.rightText.text.Unbind(stc.EVT_STC_SAVEPOINTLEFT)
        self.page.rightText.text.Unbind(stc.EVT_STC_SAVEPOINTREACHED)
        self.page.leftText.text.Unbind(wx.EVT_KEY_DOWN)
        self.page.rightText.text.Unbind(wx.EVT_KEY_DOWN)

    def _on_save_point_left(self,evt):
        index = PageManager.get_instance().notebook.FindPage(self.page)
        PageManager.get_instance().notebook.SetPageText(index,self.page.getdata().get_label()+"*")
        self.page.toolbar.show_save(True)
        evt.Skip()

    def _on_save_point_reached(self,evt):
        index = PageManager.get_instance().notebook.FindPage(self.page)
        PageManager.get_instance().notebook.SetPageText(index,self.page.getdata().get_label())
        self.page.toolbar.show_save(False)
        if evt:
            evt.Skip()

    def _on_key_down(self,evt):
        if evt.ControlDown():
            keyCode = evt.GetKeyCode()
            if keyCode == ord("S"):
                print "save"
                self.page.compare_ctrl.save()
                self._on_save_point_reached(None)
            elif keyCode == ord("F"):
                print "find"
                self.
        evt.Skip()

class PageManager(object):
    _instance = None
    @staticmethod
    def get_instance():
        if not PageManager._instance:
            PageManager._instance = PageManager()
            return PageManager._instance
        else:
            return PageManager._instance

    def __init__(self):
        if PageManager._instance != None:
            raise Exception("this is instance")

    def setup(self, notebook):
        self._page_controller_dic = {}
        self.notebook = notebook

        EventManager.get_instance().Bind(EVT_FRAME_EVENT, self._frame_handler)
        EventManager.get_instance().Bind(EVT_MENU_BAR, self._menu_handler)
        self._init_handler()
        self._init_notebook()

    def _init_notebook(self):
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, size=wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16, 16)))
        self.notebook.AssignImageList(imglist)

    def destory(self):
        EventManager.get_instance().Unbind(EVT_FRAME_EVENT)
        EventManager.get_instance().Unbind(EVT_MENU_BAR)
        del self.notebook
        for id in self._page_controller_dic:
            del self._page_controller_dic[id]
        del self._page_controller_dic
        self._menu_handler_dic.clear()

    def _init_handler(self):
        self._menu_handler_dic = {}
        self._menu_handler_dic[MenuBar.NEW_SESSION_COMPARE] = self._open_new_page
        self._menu_handler_dic[MenuBar.NEW_SESSION_MERGE] = self._open_new_page
        self._menu_handler_dic[MenuBar.EDIT_COLLAPSEALL] = self._opera_tree
        self._menu_handler_dic[MenuBar.EDIT_EXPANDALL] = self._opera_tree
        self._menu_handler_dic[MenuBar.MERGE_INFO] = self._merge_result_handler

    def _frame_handler(self, evt):
        print "receive:", evt.data
        curPageData = self.notebook.GetCurrentPage().getdata()
        if evt.type == FrameEventType.OPEN_FILE:
            itemData = evt.data
            leftFileUrl = get_parent_path(curPageData.leftPath) + "/" + itemData.relative_path
            centerFileUrl = get_parent_path(curPageData.centerPath) + "/" + itemData.relative_path
            rightFileUrl = get_parent_path(curPageData.rightPath) + "/" + itemData.relative_path
            pageData = PageData(leftFileUrl, centerFileUrl, rightFileUrl, curPageData.cmp_option)
            self.create_page(pageData)
        elif evt.type == FrameEventType.CLOSE_PAGE:
            self.remove_page(evt.data)
        elif evt.type == FrameEventType.TREE_READY:
            # self.get_cur_page()
            pass

    def get_cur_page(self):
        return self.notebook.GetCurrentPage()

    def _menu_handler(self, evt):
        id = evt.data
        func = self._menu_handler_dic[id]
        func(evt)

    def _opera_tree(self, evt):
        id = evt.data
        curPage = self.notebook.GetCurrentPage()
        if id == MenuBar.EDIT_EXPANDALL:
            curPage.expand_all()
        elif id == MenuBar.EDIT_COLLAPSEALL:
            curPage.collapse_all()

    def _open_new_page(self, evt):
        id = evt.data
        if id == MenuBar.NEW_SESSION_COMPARE:
            self.create_page(type=Page.COMPARE_PAGE)
        else:
            self.create_page(type=Page.MERGE_PAGE)

    def create_page(self, data=None, type=Page.MERGE_PAGE):
        if type == Page.MERGE_PAGE:
            page = ThreeSidePage(self.notebook, data)
            pageCtrl = PageController(page)
            label = "New Merge"
        else:
            page = TwoSidePage(self.notebook, data)
            pageCtrl = TwoSidePageController(page)
            label = "New Compare"
        label = data.get_label() if data else label
        if self._page_controller_dic.has_key(page.GetId()):
            logger.log_line("creat page found ctrl is not null, pageId:"+str(page.GetId()))
        self._page_controller_dic[page.GetId()] = pageCtrl
        self.notebook.AddPage(page, label, True)
        print "add page"
        return page

    def open_find_frame(self):
        if self.find_frame:
            self.find_frame.Destory()

    def remove_page(self, page):
        index = self.notebook.FindPage(page)
        self.notebook.RemovePage(index)
        pageCtrl = self._page_controller_dic[page.GetId()]
        pageCtrl.destory()
        del self._page_controller_dic[page.GetId()]
        page.destory()
        print "remove page"

    def _merge_result_handler(self, evt):
        curPage = self.get_cur_page()
        result_msg = curPage.compare_ctrl.get_merge_result()
        dlg = wx.MessageDialog(self.get_cur_page(), result_msg, "Confirm", wx.OK)
        dlg.ShowModal()
