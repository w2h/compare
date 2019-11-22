# -*- coding: utf-8 -*-


import wx,os
import wx.xrc
import wx.stc as stc
from data import *
from textctrl import *
from compare import *
import copy
import keyword

testStr = "kdalfskldfjlaksdjf aklsdjfkalsdf\n" \
          "kjalfsdflajksjdlfalsdf\n" \
          "alsdjkflajsldjflajlskdf\n" \
          "alksdfjlakjlsdjflajsdf\n" \
          "laksdfjlakjsldjflasdf\n" \
          "laksdjflaksldfjkajskdf\n" \
          "laksjdfljalskdfjlaksjdflk\n" \
          "laksdjflakjlskdfjlkajsdf"

class MyTextCtrl(stc.StyledTextCtrl):
    MARGIN_SCRIPT_FOLD_INDEX = 1
    def __init__(self,parent,size):
        stc.StyledTextCtrl.__init__(self,parent,size=size)
        self.SetMargins(0, 0)  # set left and right outer margins to 0 width
        # self.SetKeyWords(0, "private as")
        # self.SetKeyWords(0," ".join(keyword.kwlist))
        # self.SetLexer(stc.STC_LEX_NULL)
        # self.SetText(file.get_render_text())
        # self.Colourise(0, -1)
        # self.StyleSetForeground()
        # self.SetLexer(stc.STC_LEX_CPP)
        self.SetStyleBits(5)
        # self.SetProperty("fold", "1")
        # self.AddText("first line")
        # self.SetProperty("fold","1")
        # self.SetProperty("fold.compact","0")
        # self.SetProperty("fold.comment","1")
        # self.SetProperty("fold.preprocessor","1")


        lines = self.GetLineCount()  # get # of lines, ensure text is loaded first!

        # width = self.TextWidth(stc.STC_STYLE_LINENUMBER, str(lines) + ' ')
        self.SetMarginWidth(self.MARGIN_SCRIPT_FOLD_INDEX, 0)
        self.SetMarginType(self.MARGIN_SCRIPT_FOLD_INDEX, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(self.MARGIN_SCRIPT_FOLD_INDEX, stc.STC_MASK_FOLDERS)
        self.SetMarginWidth(self.MARGIN_SCRIPT_FOLD_INDEX, 20)
        # self.SetMarginWidth(1, 16)  # margin 1 for symbols, 16 px wide
        # self.SetMarginWidth(2, 20)  # margin 1 for symbols, 16 px wide

        # Setup a margin to hold fold markers
        # self.SetMarginMask(1, stc.STC_MASK_FOLDERS)  # margin 2 for symbols
        # self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)  # margin 2 for symbols
        # self.SetMarginMask(1, stc.STC_MASK_FOLDERS)  # margin 2 for symbols
        # self.SetMarginType(0, stc.STC_MARGIN_NUMBER)  # margin 2 for symbols
        # self.SetMarginMask(2, stc.STC_MASK_FOLDERS)  # margin 2 for symbols
        self.MarkerDefine(stc.STC_MARKNUM_FOLDER,stc.STC_MARK_PLUS)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,stc.STC_MARK_MINUS)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL,stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID,stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,stc.STC_MARK_EMPTY)
        self.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,stc.STC_MARK_EMPTY)
        # self.MarkerDefine(0,stc.STC_MARK_BOXMINUS,"white","black")
        # self.MarkerDefine(1,stc.STC_MARK_VLINE,"black","black")
        # self.MarkerDefine(2,stc.STC_MARK_LCORNER,"black","black")
        # self.MarkerDefine(3,stc.STC_MARK_EMPTY,"red","red")
        # self.MarkerDefine(10, stc.STC_MARK_CHARACTER+ord("!"),"red","white")



        self.SetFoldFlags(64)
        # self.SetMarginMask(0, stc.STC_STYLE_LINENUMBER)  # set up mask for folding symbols
        self.SetMarginSensitive(self.MARGIN_SCRIPT_FOLD_INDEX, True)  # this one needs to be mouse-aware
        # self.SetMarginWidth(2, 16)  # set margin 2 16 px wide
        # self.MarkerAdd(4,0)
        # self.MarkerAdd(4,10)
        # self.SetFoldMarginColour(True, "red")
        # self.SetFoldMarginHiColour(True, "red")
        # self.MarkerAdd(3,20)
        # self.MarkerAdd(5,stc.STC_MARKNUM_FOLDEROPEN)
        # self.MarkerAdd(5,1)
        # self.MarkerAdd(3,3)
        # self.MarkerAdd(4,stc.STC_MARKNUM_FOLDEROPENMID)
        # self.MarkerAdd(5,stc.STC_MARKNUM_FOLDERSUB)
        # self.MarkerAdd(5,stc.STC_MARKNUM_FOLDERTAIL)
        # define folding markers
        # self.MarkerDefine(1, stc.STC_MARK_BACKGROUND, "black", color)
        # self.MarkerDefine(1, stc.STC_MARK_BACKGROUND, "black", color)

        if wx.Platform == '__WXMSW__':
            faces = {'times': 'Times New Roman',
                     'mono': 'Courier New',
                     'helv': 'Arial',
                     'other': 'Comic Sans MS',
                     'size': 10,
                     'size2': 8,
                     }
        else:
            faces = {'times': 'Times',
                     'mono': 'Courier',
                     'helv': 'Helvetica',
                     'other': 'new century schoolbook',
                     'size': 12,
                     'size2': 10,
                     }

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#cccccc,face:%(helv)s,size:%(size2)d,fore:#000000" % faces)
        pos = self.PositionFromLine(0)
        # self.DeleteRange(0,len(self.GetLineText(0)))
        # self.SetTargetStart(0)
        # self.SetTargetEnd(len(self.GetLineText(0)))
        # self.ReplaceTarget("replaceText")
        # self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        # self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        # self.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

        # self.StyleSetSpec(10, "fore:#ff0000,size:%(size)d,face:%(mono)s" % faces)
        # line_num = 6
        # start = self.PositionFromLine(line_num)
        # self.StartStyling(start,10)
        # end = self.GetLineEndPosition(line_num)
        # self.SetStyling(end - start + 2,10)
        # self.InsertText(self.PositionFromLine(4),self.GetLineRaw(10))
        # self.AnnotationSetVisible(stc.STC_ANNOTATION_STANDARD)
        # style = "fore:#000000,bold"
        # self.StyleSetSpec(513,style)
        # self.AnnotationSetText(4," 123\n\n")
        # self.AnnotationSetStyle(4,513)
        #
        # self.HideLines(4, 7)
        # print self.AnnotationGetText(4)
        # print self.AnnotationGetLines(5)
        # self.SetTabIndents(1)
        # self.SetViewWhiteSpace(stc.STC_WS_VISIBLEALWAYS)

        # print self.GetEndStyled()
        # foreC = wx.Colour(33,0,0)
        # self.SetStyle(5,10,wx.TextAttr(foreC))

        # self.StyleSetSpec(1, "fore:#7F007F,italic,face:%(times)s,size:%(size)d" % faces)

        # self.StyleSetSpec(1)
class MyFrame(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, "FrameWithButton", size = (1000, 900))
        self.panel = wx.Panel(self) # 初始化容器
        btn = wx.Button(self.panel,wx.ID_ANY,label="Load Pictue",pos=wx.Point(900,30),style=wx.BU_BOTTOM)#初始化一个按钮
        # line = wx.StaticLine(self.panel,pos=wx.Point(100,50))
        self.Bind(wx.EVT_BUTTON, self.OnButtonClick,btn)#绑定按钮点击后处理器
        text = MyTextCtrl(self.panel,size=wx.Size(800,800))
        # self.codeText = text
        self.style_text = text
        as_file = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window/UILobbyTask3.prefab".replace("\\","/")
        file = PrefabFile(as_file)
        self.file = file
        # self.SetKeyWords(0," ".join(keyword.kwlist))
        # self.SetLexer(stc.STC_LEX_NULL)
        # text.render_ime = False
        # num = 0
        # st = time.time()
        # for key in file.element_dic:
        #     element = file.element_dic[key]
        #     lineDatas = element.line_datas
        #     for line in lineDatas:
        #         num += 1
        #         text.add_line_data(line)
        #         if num == 3:
        #             text.add_blank_line(2)
        #
        # text.start_render()
        # print "add time:",(time.time() - st)
        # self.style_text.SetText(file.get_render_text())
        # self.save_ctrl = SaveTextCtrl(text, file)
        # text.styled_text_by_index([(3,4)],2)
        # text.styled_text_by_index([(3,4)],2)
        self.style_text.SetText(testStr)
        self.style_text.SetFoldLevel(0, 1|stc.STC_FOLDLEVELHEADERFLAG)


        self.style_text.SetFoldLevel(5, 1|stc.STC_FOLDLEVELHEADERFLAG)
        for i in range(0, 8):
            print i, self.style_text.GetFoldParent(i)

        # self.StyleSetForeground()
        # self.style_text.Show(True)
        # self.style_text.Bind(stc.EVT_STC_UPDATEUI, self.onColour)
        # self.radio_btn1 = wx.RadioButton(self.panel, label = "checked", style = wx.RB_GROUP, pos=wx.Point(0,0))
        # self.radio_btn2 = wx.RadioButton(self.panel, label = "checked2",pos=wx.Point(100,0))
        # self.radio_btn2.Disable()
        # self.style_text.EnsureCaretVisible()
        # self.style_text.SetCaretForeground("red")
        # self.style_text.SetCaretWidth(5)
        # self.style_text.SetCaretLineVisible(True)
        # self.style_text.SetCaretLineBackAlpha(10)

        # self.style_text.HideLines(8,11)
        # self.style_text.SetFoldMarginColour()
        # print self.style_text.GetFoldLevel(8)
        self.style_text.Bind(stc.EVT_STC_MARGINCLICK,self.onMarginClick,self.style_text)
        # self.style_text.SetMarginSensitive(2,True)
        # self.style_text.SetMarginSensitive(1,True)
        # self.style_text.SetMarginCursor(1,stc.STC_CURSORNORMAL)
        # # self.style_text.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        # self.style_text.SetEOLMode(stc.STC_EOL_LF)
        # self.style_text.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT)
        # self.style_text.Bind(stc.EVT_STC_MODIFIED, self._on_modify)
        # self.style_text.MarkerAdd(3, 2)
        # self.style_text.MarkerAdd(3, 2)
        # self.style_text.MarkerAdd(3, 13)
        # self.style_text.MarkerAdd(3, 13)
        # by =  self.style_text.MarkerGet(3)
        # print by

        # print self.style_text.DocLineFromVisible(7)
        # self.style_text.SetStyling(11,10)
        # self.style_text.MarkerAdd(0,1)
        # self.style_text.MarkerSetBackground(stc.STC_MARKNUM_FOLDEROPEN,"red")
        # self.style_text.SetEditable(False)
        # print self.style_text.GetTextRange(0,100)

        # self.Bind(wx.EVT_KEY_UP, self.onColour)  # instead of:
        self.index = 1
    def _on_modify(self,evt):
        t = evt.GetModificationType()
        pos = evt.GetPosition()
        curText = evt.GetEventObject()
        lineIndex = curText.LineFromPosition(pos)
        print "line:" + str(lineIndex)
        addLines = evt.GetLinesAdded()
        if addLines == 0:
            # modify
            pass
        if (stc.STC_MOD_INSERTTEXT & t):
            print "insert text:" + evt.GetText()
            print "addLine:" + str(evt.GetLinesAdded())
        elif (stc.STC_MOD_DELETETEXT & t):
            print "delete text:" + evt.GetText()
            print "addLine:" + str(evt.GetLinesAdded())
            if evt.GetText() == "\n":
                print "delete line"
        print "-------------------"
    def _on_key_down(self,evt):
        print "keyCode:",evt.GetKeyCode()
        print "unicode:",evt.GetUnicodeKey()
        evt.Skip()
    def onMarginClick(self,evt):
        line_num = self.style_text.LineFromPosition(evt.GetPosition())
        margin = evt.GetMargin()
        print line_num,margin
        self.style_text.ToggleFold(line_num)
        # if line_num == 3:
        #     if self.style_text.GetLineVisible(4):
        #         self.style_text.HideLines(4,7)
        #         # self.style_text.MarkerDelete(3,21)
        #         self.style_text.MarkerAdd(3, 2)
        #         self.style_text.MarkerAdd(3, 13)
        #     else:
        #         self.style_text.ShowLines(4,7)
        #         self.style_text.MarkerDelete(3,-1)
                # self.style_text.MarkerAdd(3, 21)
        # num = self.style_text.MarkerGet(line_num)
        # print bin(num)
        # print hex(num)
        # if num != 0:
        #     self.style_text.MarkerDelete(line_num, stc.STC_MARKNUM_FOLDEROPEN)
        # else:
        #     self.style_text.MarkerAdd(line_num, stc.STC_MARKNUM_FOLDEROPEN)
        # print "line_num:"+str(line_num)
        #
        # self.style_text.AnnotationClearLine(4)
        # self.style_text.ToggleFold(line_num)
    # and the following handler function:
    def onColour(self, event):
        print str(self.style_text.GetXOffset())+"/"+str(self.style_text.GetScrollWidth())
        # self.style_text.Unbind(stc.EVT_STC_UPDATEUI)

        # print self.style_text.GetFirstVisibleLine()





    def OnButtonClick(self, event):
        as_file = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window/UILobbyTask3_new.prefab".replace(
                "\\", "/")
        self.save_ctrl.save(as_file)
        return
        add_btn = wx.Button(self.panel,label="x++",pos=wx.Point(100,30))
        reduce_btn = wx.Button(self.panel, label="x--",pos = wx.Point(200, 30))
        self.Bind(wx.EVT_BUTTON, self._on_add,add_btn)
        self.Bind(wx.EVT_BUTTON, self._on_reduce,reduce_btn)

        bitmap = wx.Image("1.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()#加载图片数据
        self.pic = wx.StaticBitmap(self.panel, wx.ID_ANY, bitmap, pos=wx.Point(0, 100))#初始化图片
        self.pic.SetPosition(wx.Point(50,100))#设置坐标
        self.textf = wx.TextCtrl(self.panel, wx.ID_ANY, wx.EmptyString, wx.Point(0,200), wx.DefaultSize,
                            style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)#初始化文本框
        self.textf.SetSize(wx.Size(200, 80))#设置文本框大小
        self._update_info()



    def _on_add(self,evt):
        p = self.pic.GetPosition()
        p.x = p.x + 5
        self.pic.SetPosition(p)
        self._update_info()
    def _on_reduce(self,evt):
        p = self.pic.GetPosition()
        p.x = p.x - 5
        self.pic.SetPosition(p)
        self._update_info()
    def _update_info(self):
        size = self.pic.GetSize()
        pos = self.pic.GetPosition()
        self.textf.SetLabel(
            "width:" + str(size.GetWidth()) + " height:" + str(size.GetHeight()) +
            " x:" + str(pos.x) + " y:" + str(pos.y)
        )


    def __del__(self):
        print "deled"



if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None,wx.ID_ANY)
    frame.Show(True)
    app.MainLoop()
