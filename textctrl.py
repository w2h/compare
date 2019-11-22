#coding:utf-8

import copy
import wx
import wx.stc as stc
from data import LineData,LineModify
from diff_match_patch import *


class RenderData(object):
    pass

class MarkRenderData(RenderData):
    def __init__(self, lineIndex, markNum):
        self.line_index = lineIndex
        self.mark_num = markNum

class StyleRenderData(RenderData):
    def __init__(self, lineIndex, renderP, styleNum):
        self.line_index = lineIndex
        self.render_p = renderP
        self.style_num = styleNum

class UserModify(object):
    ADD_LINE = 1
    MODIFY_LINE = 0
    DELETE_LINE = -1
    def __init__(self,lineIndex, modifyType, content=None, addLineCount = 1):
        self.index = lineIndex
        self.type = modifyType
        self.content = content# the value is None when type is delete
        self.add_line_count = addLineCount


class CodeTextCtrl(object):
    UNSTABLE_LINE_MARKER = 0
    NEAR_STABLE_LINE_MARKER = 1
    DIFF_LINE_MARKER = 2
    ERROR_BUILD_LINE_MARKER = 3
    NORMAL_STYLE = 9
    DIFF_STYLE = 10
    MATCH_NUM_MARKER = 11
    RESOLVE_CONFLICT_MARKER = 12
    UNRESOLVE_CONFLICT_MARKER = 13
    MARK_FOLD = 20
    MARK_OPEN = 21
    ANNOTATION_INSERT_STYLE = 513

    def __init__(self,parent=None,size=None, render=True, renderIme=True):
        self.render = render
        self.render_ime = renderIme
        self.render_cache = []
        self.has_modify = False
        if render:
            self.text = stc.StyledTextCtrl(parent, size=size)
            self._init_style()
            self._init_margin()
            self._init_event()
            # self.switch_text_format(FileFormat.AS)
        self.text_lines = []
        self.text_line_dic = {}
        self.modify_offset = 0
        self.listen_modifys = {}

    def destory(self):
        del self.text_lines
        del self.text_line_dic
        del self.listen_modifys
        if self.text:
            self._remove_event()
            self.text.Destroy()

    def _init_style(self):
        if wx.Platform == '__WXMSW__':
            self.faces = {'times': 'Times New Roman',
                         'mono': 'Courier New',
                         'helv': 'Arial',
                         'other': 'Comic Sans MS',
                         'size': 10,
                         'size2': 8,
                         }
        else:
            self.faces = {'times': 'Times',
                         'mono': 'Courier',
                         'helv': 'Helvetica',
                         'other': 'new century schoolbook',
                         'size': 12,
                         'size2': 10,
                         }

        self.text.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(mono)s,size:%(size)d" % self.faces)
        self.text.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#cccccc,face:%(helv)s,size:%(size2)d,fore:#000000" % self.faces)
        self.text.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % self.faces)
        self.text.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.text.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

        self.text.StyleSetSpec(CodeTextCtrl.NORMAL_STYLE, "fore:#000000,size:%(size)d,face:%(mono)s" % self.faces)
        self.text.StyleSetSpec(CodeTextCtrl.DIFF_STYLE, "fore:#ff0000,size:%(size)d,face:%(mono)s" % self.faces)

        self.text.SetCaretLineVisible(True)
        self.text.SetCaretLineBackground("#eeeeee")
        self.text.SetCaretWidth(3)
        # self.text.SetCaretForeground("red")

        # 初始化Annotation
        self.text.AnnotationSetVisible(stc.STC_ANNOTATION_STANDARD)
        style = "fore:#8b0000,bold,back:#ffe3e3"
        self.text.StyleSetSpec(CodeTextCtrl.ANNOTATION_INSERT_STYLE, style)


    def _init_margin(self):
        self.text.SetMargins(0, 0)
        self.text.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.text.SetMarginWidth(0,20)
        self.text.SetMarginWidth(1,20)
        self.text.SetMarginCursor(0, stc.STC_CURSORNORMAL)
        self.text.SetMarginCursor(1, stc.STC_CURSORNORMAL)
        self.text.SetMarginType(1, stc.STC_MARGIN_SYMBOL)

        self.text.SetMarginWidth(2, 0)
        self.text.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.text.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.text.SetMarginWidth(2, 20)
        self.text.SetMarginCursor(2, stc.STC_CURSORNORMAL)
        self.text.SetMarginSensitive(2, True)
        self.text.SetMarginSensitive(1, True)

        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS, "black", "white")
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, "black", "white")
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY)
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY)
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY)
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY)
        self.text.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY)

        color = wx.Colour(255, 50, 50)
        self.text.MarkerDefine(CodeTextCtrl.UNSTABLE_LINE_MARKER, stc.STC_MARK_SHORTARROW, "black", color)
        color = wx.Colour(247, 210, 100)
        self.text.MarkerDefine(CodeTextCtrl.DIFF_LINE_MARKER, stc.STC_MARK_SHORTARROW, "black", color)
        color = wx.Colour(200, 100, 100)
        self.text.MarkerDefine(CodeTextCtrl.NEAR_STABLE_LINE_MARKER, stc.STC_MARK_SHORTARROW, "black", color)
        # self.text.MarkerDefine(2, stc.STC_MARK_LCORNER, "black", "red")
        self.text.MarkerDefine(CodeTextCtrl.ERROR_BUILD_LINE_MARKER, stc.STC_MARK_CHARACTER+ord("e"), "red", "white")
        # self.text.MarkerDefine(4, stc.STC_MARK_VLINE, "black", "red")

        self.text.MarkerDefine(CodeTextCtrl.MATCH_NUM_MARKER, stc.STC_MARK_BACKGROUND,"black", "green")

        # self.text.MarkerDefine(CodeTextCtrl.MARK_FOLD, stc.STC_MARK_BOXPLUS, "white", "black")
        # self.text.MarkerDefine(CodeTextCtrl.MARK_OPEN, stc.STC_MARK_BOXMINUS, "white", "black")

        color = wx.Colour(213, 255, 255)
        self.text.MarkerDefine(CodeTextCtrl.RESOLVE_CONFLICT_MARKER, stc.STC_MARK_BACKGROUND, "black", color)
        color = wx.Colour(255, 227, 227)
        self.text.MarkerDefine(CodeTextCtrl.UNRESOLVE_CONFLICT_MARKER, stc.STC_MARK_BACKGROUND, "black", color)

    def _init_event(self):
        self.text.SetModEventMask(stc.STC_MOD_INSERTTEXT | stc.STC_MOD_DELETETEXT | stc.STC_MOD_CHANGEFOLD)
        pass

    def _remove_event(self):
        pass


    # def switch_text_format(self,mFormat):
        # self.m_format = mFormat
        # if self.m_format == FileFormat.AS:
        #     self.text.SetKeyWords(0,"function class package var const import extends static implements private public override if for each switch else break")

    def mark_near_stable_line(self,lineIndex):
        if not self.render:
            return
        if self.render_ime:
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.NEAR_STABLE_LINE_MARKER)
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.RESOLVE_CONFLICT_MARKER)
        else:
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.NEAR_STABLE_LINE_MARKER))
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.RESOLVE_CONFLICT_MARKER))


    def mark_conflict_line(self,lineIndex):
        if not self.render:
            return
        if self.render_ime:
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.UNRESOLVE_CONFLICT_MARKER)
        else:
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER))
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.UNRESOLVE_CONFLICT_MARKER))

    def mark_diff_line(self, lineIndex):
        if not self.render:
            return
        if self.render_ime:
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.DIFF_LINE_MARKER)
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.UNRESOLVE_CONFLICT_MARKER)
            self.text.UpdateWindowUI()
        else:
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.DIFF_LINE_MARKER))
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.UNRESOLVE_CONFLICT_MARKER))

    def clear_diff_line_mark(self, lineIndex):
        if not self.render:
            return
        self.text.MarkerDelete(lineIndex, -1)

    def mark_auto_resolve_line(self,lineIndex):
        if not self.render:
            return
        if self.render_ime:
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.NEAR_STABLE_LINE_MARKER)
            self.text.MarkerAdd(lineIndex, CodeTextCtrl.RESOLVE_CONFLICT_MARKER)
        else:
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.NEAR_STABLE_LINE_MARKER))
            self.render_cache.append(MarkRenderData(lineIndex, CodeTextCtrl.RESOLVE_CONFLICT_MARKER))
    # 标记不稳定的行
    # def mark_unstable_trunk(self,startIndex, endIndex):
    #     if not self.render:
    #         return
    #     length = endIndex - startIndex
    #     if length == 0:
    #         self.text.MarkerAdd(startIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)
    #     elif length == 1:
    #         self.text.MarkerAdd(startIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)
    #         self.text.MarkerAdd(endIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)
    #     elif length > 1:
    #         self.text.MarkerAdd(startIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)
    #         for i in range(1, length):
    #             self.text.MarkerAdd(startIndex + i, CodeTextCtrl.UNSTABLE_LINE_MARKER)
    #         self.text.MarkerAdd(endIndex, CodeTextCtrl.UNSTABLE_LINE_MARKER)


    def styled_text_by_index(self, indexArr, lineNum):
        '''
        标记不同的文字
        :param indexArr: tuple数组
        :param lineNum: 行索引
        :return:
        '''
        if not self.render:
            return
        start_index = self.text.PositionFromLine(lineNum)
        for i in range(0, len(indexArr)):
            render_p = indexArr[i]
            if self.render_ime:
                self.text.StartStyling(render_p[0] + start_index, CodeTextCtrl.DIFF_STYLE)
                self.text.SetStyling(render_p[1], CodeTextCtrl.DIFF_STYLE)
            else:
                self.render_cache.append(StyleRenderData(lineNum, render_p, CodeTextCtrl.DIFF_STYLE))

    def clear_text_style(self, lineNum):
        if not self.render:
            return
        start_index = self.text.PositionFromLine(lineNum)
        le = len(self.text.GetLineText(lineNum))
        self.text.StartStyling(start_index, CodeTextCtrl.NORMAL_STYLE)
        self.text.SetStyling(le, CodeTextCtrl.NORMAL_STYLE)

    def SetText(self,text):
        if not self.render:
            return
        self.text.SetText(text)
        self.update_line_num()

    def set_line_match_background(self,lineNum):
        if not self.render:
            return
        if self.render_ime:
            self.text.MarkerAdd(lineNum, CodeTextCtrl.MATCH_NUM_MARKER)
        else:
            self.render_cache.append(MarkRenderData(lineNum, CodeTextCtrl.MATCH_NUM_MARKER))

    def ClearAll(self):
        if self.render:
            self.text.ClearAll()
        self.text_lines = []
        self.text_line_dic.clear()
        self.modify_offset = 0

    def update_line_num(self):
        if not self.render:
            return
        lines = self.text.GetLineCount()
        width = self.text.TextWidth(stc.STC_STYLE_LINENUMBER, str(lines) + ' ')
        self.text.SetMarginWidth(0, width)

    def get_data_by_index(self,index):
        return self.text_line_dic[index]

    def add_line_data(self, lineData = LineData(0), suffix=None):
        if self.render:
            if self.render_ime:
                content = lineData.get_show_content()
                if suffix and not content.endswith(suffix):
                    content = content + suffix
                    lineData.show_suffix = suffix
                content = content + "\n"
                self.text.AddText(content)
                lineData.show_line_num = len(self.text_lines)
            else:
                if suffix:
                    lineData.show_suffix = suffix
                lineData.show_line_num = len(self.text_lines)
        self.text_lines.append(lineData)
        self.text_line_dic[lineData.index] = lineData

    def start_render(self):
        if not self.render_ime:
            lineNum = 0
            addEmptyLineDic = {}
            resultContent = []
            for lineData in self.text_lines:
                content = lineData.get_show_content()
                suffix = lineData.show_suffix
                if suffix and not content.endswith(suffix):
                    content = content + suffix
                content = content + "\n"
                resultContent.append(content)
                lineData.show_line_num = lineNum
                if lineData.add_empty_line_num > 0:
                    addEmptyLineDic[lineNum] = lineData.add_empty_line_num
                lineNum += 1
            self.text.SetText("".join(resultContent))

            for key in addEmptyLineDic:
                addEmptyNum = addEmptyLineDic[key]
                if addEmptyNum > 1:
                    msg = " " + "\n" * (addEmptyNum - 1)
                else:
                    msg = " "
                self.text.AnnotationSetText(key, msg)
                self.text.AnnotationSetStyle(key, CodeTextCtrl.ANNOTATION_INSERT_STYLE)

            for renderData in self.render_cache:
                if isinstance(renderData, StyleRenderData):
                    start_index = self.text.PositionFromLine(renderData.line_index)
                    self.text.StartStyling(renderData.render_p[0] + start_index, CodeTextCtrl.DIFF_STYLE)
                    self.text.SetStyling(renderData.render_p[1], CodeTextCtrl.DIFF_STYLE)
                elif isinstance(renderData, MarkRenderData):
                    self.text.MarkerAdd(renderData.line_index, renderData.mark_num)
        self.render_ime = True
        self.update_line_num()

    def add_blank_line(self, lineCount=1):
        lineIndex = len(self.text_lines) - 1
        self.insert_blank_line(lineIndex, lineCount)

    def insert_blank_line(self, lineIndex, addLineCount=1):
        if self.render:
            if self.render_ime:
                m_count = self.text.AnnotationGetLines(lineIndex)
                lineCount = addLineCount + m_count
                if lineCount > 1:
                    msg = " " + "\n" * (lineCount - 1)
                else:
                    msg = " "
                self.text.AnnotationSetText(lineIndex, msg)
                self.text.AnnotationSetStyle(lineIndex, CodeTextCtrl.ANNOTATION_INSERT_STYLE)
        lineData = self.text_lines[lineIndex]# lineIndex也是从0开始的，而lineData也是从0开始计算
        if not lineData:
            raise Exception("insert blank line occur error",0)
        lineData.add_empty_line_num += addLineCount

    def editor_insert_blank_line(self, lineIndex, addLineCount=1):
        '''
        不影响lineData,编辑使用
        :param lineIndex:
        :param addLineCount:
        :return:
        '''
        m_count = self.text.AnnotationGetLines(lineIndex)
        lineCount = addLineCount + m_count
        if lineCount > 1:
            msg = " " + "\n" * (lineCount - 1)
        else:
            msg = " "
        self.text.AnnotationSetText(lineIndex, msg)
        self.text.AnnotationSetStyle(lineIndex, CodeTextCtrl.ANNOTATION_INSERT_STYLE)

    def editor_check_blank_line(self, lineIndex, lineCount):
        m_count = self.text.AnnotationGetLines(lineIndex)
        if m_count == lineCount:
            return
        if lineCount <= 0:
            self.text.AnnotationClearLine(lineIndex)
            return
        if lineCount > 1:
            msg = " " + "\n" * (lineCount - 1)
        else:
            msg = " "
        self.text.AnnotationSetText(lineIndex, msg)
        self.text.AnnotationSetStyle(lineIndex, CodeTextCtrl.ANNOTATION_INSERT_STYLE)


    def get_all_line_datas(self):
        return self.text_lines
    def get_last_line_data(self):
        return self.text_lines[len(self.text_lines) - 1]

    def clone_text_ctrl(self,textCtrl):
        '''
        复制一个一样的文本数据
        :param textCtrl:
        :return:
        '''
        self.ClearAll()
        lineDatas = textCtrl.get_all_line_datas()
        for i in range(0, len(lineDatas)):
            lineData = lineDatas[i]
            newLineData = lineData.clone()
            self.add_line_data(newLineData,lineData.show_suffix)
            if lineData.add_empty_line_num > 0:
                self.add_blank_line(lineData.add_empty_line_num)

    def GetLineText(self, n):
        if n >= 0:
            return self.text.GetLineText(n)
        else:
            return None

    def modify_text(self,modify):
        if not self.render:
            return
        '''
        修改显示的文本，不会对实际的LineData造成影响
        :param modify:
        :return:
        '''
        index = modify.lineIndex
        lineData = self.get_data_by_index(index)
        showLineNum = lineData.show_line_num
        showLineNum = self.modify_offset + showLineNum
        if modify.type == LineModify.ADD_TYPE:
            self.modify_offset += 1
            m_count = self.text.AnnotationGetLines(showLineNum)
            if m_count > 0:
                lineCount = m_count - 1
                if lineCount > 1:
                    msg = " " + "\n" * (lineCount - 1)
                else:
                    msg = " "
                self.text.AnnotationClearLine(showLineNum)
                insertPos = self.text.PositionFromLine(showLineNum + 1)
                self.text.InsertText(insertPos, modify.lineDatas.get_show_content()+"\n")
                if lineCount > 0:
                    self.text.AnnotationSetText(showLineNum + 1, msg)
                    self.text.AnnotationSetStyle(showLineNum + 1, CodeTextCtrl.ANNOTATION_INSERT_STYLE)
            else:
                insertPos = self.text.PositionFromLine(showLineNum + 1)
                self.text.InsertText(insertPos, modify.lineDatas.get_show_content() + "\n")
            self.mark_auto_resolve_line(showLineNum+1)
        elif modify.type == LineModify.DELETE_TYPE:
            startPos = self.text.PositionFromLine(showLineNum)
            self.text.DeleteRange(startPos, len(self.text.GetLineText(showLineNum)))
            self.mark_auto_resolve_line(showLineNum)
        elif modify.type == LineModify.MODIFY_TYPE:
            self.text.SetTargetStart(self.text.PositionFromLine(showLineNum))
            self.text.SetTargetEnd(self.text.PositionFromLine(showLineNum + 1) - 1)
            self.text.ReplaceTarget(modify.lineDatas.get_show_content())
            self.mark_auto_resolve_line(showLineNum)
        elif modify.type == LineModify.CONFLICT_TYPE:
            self.mark_conflict_line(showLineNum)
        elif modify.type == LineModify.EMPTY_CONFLICT_TYPE:# 空行冲突（为了更好显示效果，和普通文本冲突，加上特别效果）
            self.modify_offset += 1
            m_count = self.text.AnnotationGetLines(showLineNum)
            if m_count > 0:
                lineCount = m_count - 1
                if lineCount > 1:
                    msg = " " + "\n" * (lineCount - 1)
                else:
                    msg = " "
                self.text.AnnotationClearLine(showLineNum)
                insertPos = self.text.PositionFromLine(showLineNum + 1)
                self.text.InsertText(insertPos, modify.lineDatas.get_show_content() + "\n")
                if lineCount > 0:
                    self.text.AnnotationSetText(showLineNum + 1, msg)
                    self.text.AnnotationSetStyle(showLineNum + 1, CodeTextCtrl.ANNOTATION_INSERT_STYLE)
            else:
                insertPos = self.text.PositionFromLine(showLineNum + 1)
                self.text.InsertText(insertPos, modify.lineDatas.get_show_content() + "\n")
            self.mark_conflict_line(showLineNum + 1)
        elif modify.type == LineModify.NONE_TYPE:
            self.mark_auto_resolve_line(showLineNum)


class MergeTextScrollCtrl(object):
    """
    对比显示滚动3方同步器
    """
    def __init__(self, text_l, text_c, text_r, text_d):
        self.text_l = text_l
        self.text_c = text_c
        self.text_r = text_r
        self.text_d = text_d
        self._add_event()

    def destory(self):
        self._remove_event()
        self.text_l = None
        self.text_c = None
        self.text_r = None
        self.text_d = None

    def _add_event(self):
        self.text_l.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)
        self.text_c.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)
        self.text_r.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)
        self.text_d.Bind(stc.EVT_STC_UPDATEUI, self._on_down_text_update)

    def _remove_event(self):
        self.text_l.Unbind(stc.EVT_STC_UPDATEUI)
        self.text_c.Unbind(stc.EVT_STC_UPDATEUI)
        self.text_r.Unbind(stc.EVT_STC_UPDATEUI)
        self.text_d.Unbind(stc.EVT_STC_UPDATEUI)

    def _on_down_text_update(self,event):
        updateField = event.GetUpdated()
        if updateField == stc.STC_UPDATE_V_SCROLL:
            line_num = self.text_d.GetFirstVisibleLine()
            if self.text_l.GetFirstVisibleLine() != line_num:
                self.text_l.SetFirstVisibleLine(line_num)
            if self.text_c.GetFirstVisibleLine() != line_num:
                self.text_c.SetFirstVisibleLine(line_num)
            if self.text_r.GetFirstVisibleLine() != line_num:
                self.text_r.SetFirstVisibleLine(line_num)

    def _on_update_ui(self,event):
        updateField = event.GetUpdated()
        evt_obj = event.GetEventObject()
        if updateField == stc.STC_UPDATE_V_SCROLL:
            line_num = evt_obj.GetFirstVisibleLine()
            if self.text_d.GetFirstVisibleLine() != line_num:
                self.text_d.SetFirstVisibleLine(line_num)
            if evt_obj is self.text_l:
                if self.text_c.GetFirstVisibleLine() != line_num:
                    self.text_c.SetFirstVisibleLine(line_num)
                if self.text_r.GetFirstVisibleLine() != line_num:
                    self.text_r.SetFirstVisibleLine(line_num)
            elif evt_obj is self.text_c:
                if self.text_l.GetFirstVisibleLine() != line_num:
                    self.text_l.SetFirstVisibleLine(line_num)
                if self.text_r.GetFirstVisibleLine() != line_num:
                    self.text_r.SetFirstVisibleLine(line_num)
            else:
                if self.text_l.GetFirstVisibleLine() != line_num:
                    self.text_l.SetFirstVisibleLine(line_num)
                if self.text_c.GetFirstVisibleLine() != line_num:
                    self.text_c.SetFirstVisibleLine(line_num)
        elif updateField == stc.STC_UPDATE_H_SCROLL:
            x_offset = evt_obj.GetXOffset()
            if evt_obj is self.text_l:
                if self.text_c.GetXOffset() != x_offset:
                    self.text_c.SetXOffset(x_offset)
                if self.text_r.GetXOffset() != x_offset:
                    self.text_r.SetXOffset(x_offset)
            elif evt_obj is self.text_c:
                if self.text_l.GetXOffset() != x_offset:
                    self.text_l.SetXOffset(x_offset)
                if self.text_r.GetXOffset() != x_offset:
                    self.text_r.SetXOffset(x_offset)
            else:
                if self.text_l.GetXOffset() != x_offset:
                    self.text_l.SetXOffset(x_offset)
                if self.text_c.GetXOffset() != x_offset:
                    self.text_c.SetXOffset(x_offset)

class CompareTextScrollCtrl(object):
    """
    对比显示滚动2方同步器
    """
    def __init__(self, text_l, text_r):
        self.text_l = text_l
        self.text_r = text_r
        self._add_event()

    def destory(self):
        self._remove_event()
        self.text_l = None
        self.text_r = None

    def _add_event(self):
        self.text_l.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)
        self.text_r.Bind(stc.EVT_STC_UPDATEUI, self._on_update_ui)

    def _remove_event(self):
        self.text_l.Unbind(stc.EVT_STC_UPDATEUI)
        self.text_r.Unbind(stc.EVT_STC_UPDATEUI)

    def _on_update_ui(self,event):
        updateField = event.GetUpdated()
        evt_obj = event.GetEventObject()
        if updateField == stc.STC_UPDATE_V_SCROLL:
            line_num = evt_obj.GetFirstVisibleLine()
            if evt_obj is self.text_l:
                if self.text_r.GetFirstVisibleLine() != line_num:
                    self.text_r.SetFirstVisibleLine(line_num)
            else:
                if self.text_l.GetFirstVisibleLine() != line_num:
                    self.text_l.SetFirstVisibleLine(line_num)
        elif updateField == stc.STC_UPDATE_H_SCROLL:
            x_offset = evt_obj.GetXOffset()
            if evt_obj is self.text_l:
                if self.text_r.GetXOffset() != x_offset:
                    self.text_r.SetXOffset(x_offset)
            else:
                if self.text_l.GetXOffset() != x_offset:
                    self.text_l.SetXOffset(x_offset)

import math
class CompareTextEditCtrl(object):
    '''
    对比时，编辑同步控制器
    '''
    def __init__(self,textL, textR):
        self.text_l = textL
        self.text_r = textR
        pass

    def _prase_compare_index(self):
        lines = self.text_l.text_lines
        left_line_indexs = []
        le = len(lines)
        for i in range(0, le):
            lineData = lines[i]
            left_line_indexs.append(i)
            if lineData.add_empty_line_num > 0:
                left_line_indexs.extend([-1 for x in range(lineData.add_empty_line_num)])

        lines = self.text_r.text_lines
        right_line_indexs = []
        le = len(lines)
        for i in range(0, le):
            lineData = lines[i]
            right_line_indexs.append(i)
            if lineData.add_empty_line_num > 0:
                right_line_indexs.extend([-1 for x in range(lineData.add_empty_line_num)])

        self.left_line_indexs = left_line_indexs
        self.right_line_indexs = right_line_indexs

    def _fold_compare_result(self, stable_chunks):
        gap = 5
        if len(stable_chunks) <= 0:
            return
        last_l_line = stable_chunks[0][0]
        last_r_line = stable_chunks[0][1]
        is_stable = False
        left_stable_start_line = None
        right_stable_start_line = None
        stable_line_num = 0
        left_stable_line_heads = []
        right_stable_line_heads = []
        i = 1
        for i in range(1, len(stable_chunks)):
            leftLine, rightLine = stable_chunks[i]
            if last_l_line.add_empty_line_num == 0 and leftLine.show_line_num - last_l_line.show_line_num == 1:
                if not is_stable:
                    left_stable_start_line = last_l_line
                    right_stable_start_line = last_r_line
                is_stable = True
                stable_line_num += 1
            else:
                if stable_line_num > 50 and left_stable_start_line and i - gap >= 0:
                    left_stable_end_line, right_stable_end_line = stable_chunks[i - gap]
                    self.text_l.text.SetFoldLevel(left_stable_start_line.show_line_num + gap, 1 | stc.STC_FOLDLEVELHEADERFLAG)
                    left_stable_line_heads.append(left_stable_start_line.show_line_num + gap)
                    self.text_l.text.SetFoldLevel(left_stable_end_line.show_line_num, 1 | stc.STC_FOLDLEVELHEADERFLAG)
                    self.text_r.text.SetFoldLevel(right_stable_start_line.show_line_num + gap, 1 | stc.STC_FOLDLEVELHEADERFLAG)
                    right_stable_line_heads.append(right_stable_start_line.show_line_num + gap)
                    self.text_r.text.SetFoldLevel(right_stable_end_line.show_line_num, 1 | stc.STC_FOLDLEVELHEADERFLAG)
                is_stable = False
                stable_line_num = 0
                left_stable_start_line = None
                right_stable_start_line = None
            last_l_line = leftLine
            last_r_line = rightLine
        if stable_line_num > 50 and left_stable_start_line:
            left_stable_end_line, right_stable_end_line = stable_chunks[len(stable_chunks) - 1]
            self.text_l.text.SetFoldLevel(left_stable_start_line.show_line_num + gap, 1 | stc.STC_FOLDLEVELHEADERFLAG)
            left_stable_line_heads.append(left_stable_start_line.show_line_num + gap)
            self.text_l.text.SetFoldLevel(left_stable_end_line.show_line_num, 1 | stc.STC_FOLDLEVELHEADERFLAG)
            self.text_r.text.SetFoldLevel(right_stable_start_line.show_line_num + gap, 1 | stc.STC_FOLDLEVELHEADERFLAG)
            right_stable_line_heads.append(right_stable_start_line.show_line_num + gap)
            self.text_r.text.SetFoldLevel(right_stable_end_line.show_line_num, 1 | stc.STC_FOLDLEVELHEADERFLAG)
            # self.fold_same_text_ctrl.set_fold_flag(
            #     (left_stable_start_line.show_line_num, left_stable_end_line.show_line_num),
            #     (right_stable_start_line.show_line_num, right_stable_end_line.show_line_num))
        for line in left_stable_line_heads:
            self.text_l.text.ToggleFold(line)
        for line in right_stable_line_heads:
            self.text_r.text.ToggleFold(line)

    def destory(self):
        self.listen_modify_stop()
        del self.left_line_indexs
        del self.right_line_indexs
        del self.text_l
        del self.text_r

    def listen_modify_start(self,stableTrunks):
        self._prase_compare_index()
        self._fold_compare_result(stableTrunks)
        self.text_l.text.Bind(stc.EVT_STC_MODIFIED, self._on_modify)
        self.text_r.text.Bind(stc.EVT_STC_MODIFIED, self._on_modify)
        self.text_l.text.Bind(stc.EVT_STC_MARGINCLICK, self._on_margin_click)
        self.text_r.text.Bind(stc.EVT_STC_MARGINCLICK, self._on_margin_click)

    def listen_modify_stop(self):
        self.text_l.text.Unbind(stc.EVT_STC_MODIFIED)
        self.text_r.text.Unbind(stc.EVT_STC_MODIFIED)
        self.text_l.text.Unbind(stc.EVT_STC_MARGINCLICK)
        self.text_r.text.Unbind(stc.EVT_STC_MARGINCLICK)


    def _on_margin_click(self, evt):
        evt.Skip()
        pos = evt.GetPosition()
        curText = evt.GetEventObject()
        lineIndex = curText.LineFromPosition(pos)
        print "margin click line:" + str(lineIndex)
        margin = evt.GetMargin()
        if curText is self.text_l.text:
            op_line_indexs, cp_line_indexs = self.left_line_indexs, self.right_line_indexs
            op_text, cp_text = self.text_l, self.text_r
        else:
            op_line_indexs, cp_line_indexs = self.right_line_indexs, self.left_line_indexs
            op_text, cp_text = self.text_r, self.text_l
        if margin == 2:
            opIndex = op_line_indexs.index(lineIndex)
            op_text.text.ToggleFold(lineIndex)
            other_line = cp_line_indexs[opIndex]
            cp_text.text.ToggleFold(other_line)
        elif margin == 1:
            markerNum = op_text.text.MarkerGet(lineIndex)
            value = int(math.pow(2, CodeTextCtrl.DIFF_LINE_MARKER)) & markerNum
            if value > 0:
                opIndex = op_line_indexs.index(lineIndex)
                other_line = cp_line_indexs[opIndex]
                if other_line == -1:
                    # 删除行
                    op_text.clear_diff_line_mark(lineIndex)
                    startPos = op_text.text.PositionFromLine(lineIndex)
                    op_text.text.DeleteRange(startPos - 1, len(op_text.text.GetLineText(lineIndex)) + 1)

                    # cpStartIndex = self.get_op_index_fore(cp_line_indexs, opIndex)
                    # num = self.get_index_empty_num(cp_line_indexs, cpStartIndex)
                    # cp_text.editor_check_blank_line(cpStartIndex, num)

                else:
                    otherText = cp_text.text.GetLineText(other_line)
                    op_text.text.SetTargetStart(op_text.text.PositionFromLine(lineIndex))
                    op_text.text.SetTargetEnd(op_text.text.PositionFromLine(lineIndex + 1) - 1)
                    op_text.text.ReplaceTarget(otherText)
                    # op_text.clear_diff_line_mark(lineIndex)
                    # cp_text.clear_diff_line_mark(other_line)


    def refresh_diff_result(self):
        leftText = self.text_l.text.GetText()
        leftArr = leftText.split("\n")
        rightText = self.text_r.text.GetText()
        rightArr = rightText.split("\n")
        st = time.time()
        diffs = diff_obj.diff_main(leftArr, rightArr)
        lcs_content_arr = diff_obj.get_lcs(diffs)

    @staticmethod
    def get_index_empty_num(arr,index):
        '''
        get -1 num from index in arr
        :param arr:
        :param index:
        :return:
        '''
        le = len(arr)
        if index >= le - 1:
            return 0
        emptyNum = 0
        for i in range(index + 1, le):
            if arr[i] == -1:
                emptyNum += 1
            else:
                break
        return emptyNum

    @staticmethod
    def modify_index_arr(arr, offset, startIndex):
        '''
        modify arr element add offset
        :param arr:
        :param offset:
        :param startIndex:
        :return:
        '''
        le = len(arr)
        if le <= startIndex + 1:
            return False
        for i in range(startIndex, le):
            arr[i] = arr[i] + offset
        return True

    @staticmethod
    def get_op_index_fore(arr,index):
        while index >= 0:
            if arr[index] != -1:
                return index
            else:
                index -= 1

    @staticmethod
    def get_op_index_behind(arr, index):
        le = len(arr)
        while index < le:
            if arr[index] != -1:
                return index
            else:
                index += 1

    def diff_line_by_char(self, leftIndex, rightIndex):
        l_line = r_line = ""
        l_line = self.text_l.GetLineText(leftIndex)
        r_line = self.text_r.GetLineText(rightIndex)
        if l_line != None and r_line != None:
                # raise Exception("line data has not been add to stage")
            if l_line == r_line:
                self.text_l.clear_diff_line_mark(leftIndex)
                self.text_r.clear_diff_line_mark(rightIndex)
                self.text_l.clear_text_style(leftIndex)
                self.text_r.clear_text_style(rightIndex)
            else:
                self.text_l.mark_diff_line(leftIndex)
                self.text_r.mark_diff_line(rightIndex)
                diffs = diff_obj.diff_main(l_line, r_line)
                lcs = diff_obj.get_lcs(diffs, False)
                if len(lcs) > 0:
                    lcs_index = get_index_by_commstring(l_line, lcs)
                    diff_index = get_diff_lcs_index(l_line, lcs_index)
                    self.text_l.styled_text_by_index(diff_index, leftIndex)
                    lcs_index = get_index_by_commstring(r_line, lcs)
                    diff_index = get_diff_lcs_index(r_line, lcs_index)
                    self.text_r.styled_text_by_index(diff_index, rightIndex)
                else:
                    self.text_l.styled_text_by_index([(0, len(l_line))], leftIndex)
                    self.text_r.styled_text_by_index([(0, len(r_line))], rightIndex)

        elif l_line != None:
            self.text_l.mark_diff_line(leftIndex)
        else:
            self.text_r.mark_diff_line(rightIndex)

    def diff_lines(self, leftLinesIndex, rightLinesIndex):
        le = len(leftLinesIndex)
        for i in range(0, le):
            leftIndex = leftLinesIndex[i]
            rightIndex = rightLinesIndex[i]
            self.diff_line_by_char(leftIndex, rightIndex)

    def _on_modify(self, evt):
        t = evt.GetModificationType()
        if (stc.STC_MOD_INSERTTEXT & t) or (stc.STC_MOD_DELETETEXT & t):
            pos = evt.GetPosition()
            curText = evt.GetEventObject()
            lineIndex = curText.LineFromPosition(pos)
            print "line:"+str(lineIndex)
            addLines = evt.GetLinesAdded()
            addIndexArr = []
            if curText is self.text_l.text:
                op_line_indexs, cp_line_indexs = self.left_line_indexs, self.right_line_indexs
                op_text, cp_text = self.text_l, self.text_r
            else:
                op_line_indexs, cp_line_indexs = self.right_line_indexs, self.left_line_indexs
                op_text, cp_text = self.text_r, self.text_l
            opIndex = op_line_indexs.index(lineIndex)
            if addLines > 0:
                # modify
                emptyNum = self.get_index_empty_num(op_line_indexs, opIndex)
                le = len(op_line_indexs)
                if emptyNum >= addLines:
                    num = 0
                    # 修改行索引
                    for i in range(opIndex + 1, le):
                        num += 1
                        if addLines >= num:
                            op_line_indexs[i] = lineIndex + num
                            addIndexArr.append(lineIndex + num)
                        else:
                            if op_line_indexs[i] != -1:
                                op_line_indexs[i] += addLines
                    num = self.get_index_empty_num(op_line_indexs, opIndex)
                    op_text.editor_check_blank_line(lineIndex, num)
                    num = self.get_index_empty_num(op_line_indexs, opIndex+addLines)
                    op_text.editor_check_blank_line(op_line_indexs[opIndex+addLines], num)
                else:
                    # 需要增加行
                    addIndexCount = addLines - emptyNum
                    for i in range(0, addIndexCount):
                        op_line_indexs.insert(opIndex + 1, -1)
                        cp_line_indexs.insert(opIndex + 1, -1)
                    # 更新空行显示
                    cpStartIndex = self.get_op_index_fore(cp_line_indexs, opIndex+emptyNum)
                    cp_text.editor_insert_blank_line(cp_line_indexs[cpStartIndex], addIndexCount)
                    op_text.text.AnnotationClearLine(lineIndex)
                    # 修改行索引
                    num = 0
                    for i in range(opIndex + 1, le):
                        num += 1
                        if addLines >= num:
                            op_line_indexs[i] = lineIndex + num
                            addIndexArr.append(lineIndex + num)
                        else:
                            if op_line_indexs[i] != -1:
                                op_line_indexs[i] += addLines

                # 对比新增的文本块
                # 待后续完成
                sIndex = max(0,opIndex - 2)
                eIndex = min(len(self.left_line_indexs) - 1, opIndex + addLines + 2)
                leftLines = self.left_line_indexs[sIndex: eIndex]
                rightLines = self.right_line_indexs[sIndex: eIndex]
                self.diff_lines(leftLines, rightLines)
            elif addLines < 0:
                addEmpytNum = 0
                delIndexCount = 0
                delLines = abs(addLines)
                self.diff_line_by_char(self.left_line_indexs[opIndex], self.right_line_indexs[opIndex])
                if op_line_indexs[opIndex + 1] == -1:
                    # 删除行不是下一行，需要修正
                    opIndex = self.get_op_index_behind(op_line_indexs, opIndex + 1)
                    opIndex -= 1
                for i in range(0, delLines):
                    if cp_line_indexs[opIndex + 1 + addEmpytNum] == -1:
                        delIndexCount += 1
                        op_line_indexs.pop(opIndex + 1 + addEmpytNum)
                        cp_line_indexs.pop(opIndex + 1 + addEmpytNum)
                    else:
                        op_line_indexs[opIndex + 1 + addEmpytNum] = -1
                        addEmpytNum += 1
                # 修正后面的索引
                le = len(op_line_indexs)
                for i in range(opIndex + addEmpytNum + 1, le):
                    if op_line_indexs[i] != -1:
                        op_line_indexs[i] += addLines
                # 修正空行
                opStartIndex = self.get_op_index_fore(op_line_indexs, opIndex)
                num = self.get_index_empty_num(op_line_indexs, opStartIndex)
                op_text.editor_check_blank_line(op_line_indexs[opStartIndex], num)
                cpStartIndex = self.get_op_index_fore(cp_line_indexs, opIndex)
                for i in range(cpStartIndex,addEmpytNum + opIndex + 1):
                    if cp_line_indexs[i] != -1:
                        num = self.get_index_empty_num(cp_line_indexs, i)
                        cp_text.editor_check_blank_line(cp_line_indexs[i], num)
                leftLines = self.left_line_indexs[opIndex: opIndex + delLines + 1]
                rightLines = self.right_line_indexs[opIndex: opIndex + delLines + 1]
                self.diff_lines(leftLines, rightLines)
            else:
                #行修改,对比同行
                self.diff_line_by_char(self.left_line_indexs[opIndex], self.right_line_indexs[opIndex])
        elif (stc.STC_MOD_CHANGEFOLD & t):
            print "fold change"

        evt.Skip()

import time
class SaveTextCtrl(object):
    def __init__(self, text, file):
        self.code_text = text
        self.original_text = None
        self.file = file
        self.start()

    def destory(self):
        del self.original_text
        del self.code_text
        del self.file

    def start(self):
        """
        初始化文本后，就需要执行，否则这段时间修改的记录，就不会保存到文本
        :return:
        """
        self.original_text = self.code_text.text.GetText()
        self.code_text.text.SetSavePoint()

    def get_modifyed(self):
        # return self.code_text.text.GetText() is not self.original_text
        return self.code_text.text.GetModify()

    def save(self,url):
        if not url:
            return
        self.modifys = []
        if self.original_text is None:
            return
        self._create_diff_modify()
        self._save_to_url(url)
        self.code_text.text.SetSavePoint()

    def _save_to_url(self, url):
        file = self.file
        lines = copy.deepcopy(file.lines)
        line_offset = 0  # 这里是索引漂移，由于插入和删除数据导致索引漂移
        for modify in self.modifys:
            if modify.type == UserModify.ADD_LINE:
                lines.insert(modify.index + 1 + line_offset, modify.content)
                print "insert", modify.index + 1 + line_offset, modify.content
                line_offset += 1  #
            elif modify.type == UserModify.DELETE_LINE:
                del lines[modify.index + line_offset]
                print "delete line:", modify.index + line_offset
                line_offset -= 1
            else:
                lines[modify.index + line_offset] = modify.content
                print "modify line:", modify.index + line_offset
        f = open(url, 'w')  # 设置文件对象
        s = "".join(lines)
        f.write(s)  # 将字符串写入文件中
        f.flush()
        f.close()
        print "save"

    def _create_diff_modify(self):
        oriText = self.original_text
        oriArr = oriText.split("\n")
        curText = self.code_text.text.GetText()
        curArr = curText.split("\n")
        st = time.time()
        diffs = diff_obj.diff_main(oriArr, curArr)
        lcs_content_arr = diff_obj.get_lcs(diffs)
        print "diff time:"+str(time.time() - st)
        if len(lcs_content_arr) > 0:
            # 计算出公共行数索引
            l_lcs_index = []
            r_lcs_index = []
            l_index = -1  # 开始搜索索引
            r_index = -1
            for i in range(0, len(lcs_content_arr)):
                has_unstable_chunk = False
                line = lcs_content_arr[i]
                left_diffs = []
                right_diffs = []
                l_index = oriArr.index(line, l_index + 1)
                l_lcs_index.append(l_index)
                if i == 0:
                    if l_index > 0:
                        has_unstable_chunk = True
                        left_diffs = get_all_index_by_start_and_end(0, l_index)
                else:
                    lines = l_lcs_index[i] - l_lcs_index[i - 1]
                    if lines > 1:
                        has_unstable_chunk = True
                        left_diffs = get_all_index_by_start_and_end(l_lcs_index[i - 1] + 1, l_lcs_index[i])
                r_index = curArr.index(line, r_index + 1)
                r_lcs_index.append(r_index)
                if i == 0:
                    if r_index > 0:
                        has_unstable_chunk = True
                        right_diffs = get_all_index_by_start_and_end(0, r_index)
                else:
                    lines = r_lcs_index[i] - r_lcs_index[i - 1]
                    if lines > 1:
                        has_unstable_chunk = True
                        right_diffs = get_all_index_by_start_and_end(r_lcs_index[i - 1] + 1, r_lcs_index[i])
                if has_unstable_chunk:
                    leftLineDataArr = get_line_by_index(self.code_text.text_lines, left_diffs)
                    rightLineArr = get_line_by_index(curArr, right_diffs)
                    self._create_modify(leftLineDataArr, rightLineArr, self.code_text.text_lines[l_lcs_index[i - 1]])
            # 检查公共字符串后面有没有非稳定块
            last_l_index = l_lcs_index[len(l_lcs_index) - 1]
            last_r_index = r_lcs_index[len(r_lcs_index) - 1]
            left_diffs = get_all_index_by_start_and_end(last_l_index + 1, len(self.code_text.text_lines))
            leftLineDataArr = get_line_by_index(self.code_text.text_lines, left_diffs)
            right_diffs = get_all_index_by_start_and_end(last_r_index + 1, len(curArr))
            rightLineArr = get_line_by_index(curArr, right_diffs)
            if len(left_diffs) > 0 or len(right_diffs) > 0:
                self._create_modify(leftLineDataArr, rightLineArr, self.code_text.text_lines[last_l_index])
        else:
            raise Exception("can not find any same string, something is wrong")

    def _create_modify(self, lineDatas, destContents, stableLine):
        l_len = len(lineDatas)
        r_len = len(destContents)
        max_len = max(l_len, r_len)
        result = []

        def getContent(arr, startIndex):
            l = len(arr)
            content = ""
            num = 0
            for i in range(startIndex, l):
                content += arr[i] + "\n"
                num += 1
            return content, num

        for i in range(0, max_len):
            if i >= l_len:
                content, num = getContent(destContents, i)
                if l_len == 0:
                    modifyIndex = stableLine.index
                else:
                    modifyIndex = lineDatas[l_len - 1].index
                modify = UserModify(modifyIndex, UserModify.ADD_LINE, content, num)
                self._add_to_modify_list(modify)
                break
            elif i >= r_len:
                modify = UserModify(lineDatas[i].index, UserModify.DELETE_LINE)
            else:
                # modify
                modify = UserModify(lineDatas[i].index, UserModify.MODIFY_LINE, destContents[i] + "\n")
            self._add_to_modify_list(modify)

    def _add_to_modify_list(self, modify):
        modifys = self.modifys
        le = len(modifys)
        if le == 0 or self.modifys[le - 1].index <= modify.index:
            modifys.append(modify)
            return
        if self.modifys[0].index > modify.index:
            modifys.insert(0, modify)
            return
        for i in range(1, le):
            lastM = modifys[i - 1]
            curM = modifys[i]
            if curM.index > modify.index and modify.index >= lastM.index:
                modifys.insert(i, modify)
                break
        if modify not in modifys:
            raise Exception("error in add modify to list")

