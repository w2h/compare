#coding=utf-8

import wx
import os
from data import *
from textctrl import *
from log import logger
from codeutil import *
from const import *
from event import *
from diff_match_patch import *

def get_merge_by_type(fileFormat):
    if fileFormat == FileFormat.AS:
        return ThreeSideAsCompare
    else:
        return ThreeSideTextCompare

def get_compare_by_type(fileFormat):
    if fileFormat == FileFormat.PREFAB:
        return TwoSidePrefabCmp
    else:
        return TwoSideTextCmp

class CompareCtrl:
    def __init__(self):
        self.cur_selection = 0
        self.cmp = None

    def next_selection(self):
        index = self.cur_selection + 1
        if not self.cmp or len(self.cmp.unstable_chunks) == 0:
            return
        if index > len(self.cmp.unstable_chunks) - 1:
            index = 0
        if index < 0:
            index = len(self.cmp.unstable_chunks) - 1
        self.cur_selection = index
        self.go_to_unstable_chunk(self.cur_selection)
    def last_selection(self):
        self.cur_selection -= 1
        self.go_to_unstable_chunk(self.cur_selection)

    def go_to_unstable_chunk(self, index):
        pass

    def get_modifyed(self):
        pass

    def save(self):
        pass


class CompareTextCtrl(CompareCtrl):
    def __init__(self, textL, textR, pageData):
        CompareCtrl.__init__(self)
        self.text_l = textL
        self.text_r = textR
        self.cmp = None
        self.scrollctrl = CompareTextScrollCtrl(textL.text, textR.text)
        self.editor_ctrl = CompareTextEditCtrl(textL, textR)
        self.page_data = pageData
        self._init_data()

    def _init_data(self):
        l_file_url = self.page_data.leftPath
        r_file_url = self.page_data.rightPath
        cmp_cls = get_compare_by_type(self.page_data.cmp_option.file_format)
        st = time.time()
        self.text_l.render_ime = False
        self.text_r.render_ime = False
        self.cmp = cmp_cls(self.text_l, self.text_r, l_file_url, r_file_url)
        self.text_l.start_render()
        self.text_r.start_render()
        print "tot:"+str(time.time() - st)
        self.editor_ctrl.listen_modify_start(self.cmp.stable_chunks)
        self.left_save_ctrl = SaveTextCtrl(self.text_l, self.cmp.file_l)
        self.right_save_ctrl = SaveTextCtrl(self.text_r, self.cmp.file_r)
        self.text_l.text.EmptyUndoBuffer()
        self.text_r.text.EmptyUndoBuffer()

    def refresh_compare(self, cmpOption):
        # self.pageData.cmp_option = cmpOption
        # if self.cmp.get_cmp_type() != cmpOption.file_format:
        #     self.cmp.destory()
        #     l_file = self.page_data.leftPath
        #     r_file = self.page_data.rightPath
        #     cmp_cls = get_compare_by_type(cmpOption.file_format)
        #     self.cmp = cmp_cls(self.text_l, self.text_r, l_file, r_file)
        # else:
        #     self.cmp.refresh_option(cmpOption)
        pass

    def go_to_unstable_chunk(self, index):
        chunk = self.cmp.unstable_chunks[index]
        if chunk.leftLineData:
            self.text_l.text.SetFirstVisibleLine(chunk.leftLineData.show_line_num)
        else:
            self.text_l.text.SetFirstVisibleLine(chunk.leftStableLine.show_line_num)
        if chunk.rightLineData:
            self.text_r.text.SetFirstVisibleLine(chunk.rightLineData.show_line_num)
        else:
            self.text_r.text.SetFirstVisibleLine(chunk.rightStableLine.show_line_num)

    def get_modifyed(self):
        return self.right_save_ctrl.get_modifyed() or self.left_save_ctrl.get_modifyed()

    def save(self):
        if self.left_save_ctrl.get_modifyed():
            self.left_save_ctrl.save(self.page_data.leftPath)
        if self.right_save_ctrl.get_modifyed():
            self.right_save_ctrl.save(self.page_data.rightPath)

    def destory(self):
        if self.cmp:
            self.cmp.destory()
            del self.cmp
        self.scrollctrl.destory()
        del self.scrollctrl
        self.fold_same_text_ctrl.destory()
        del self.fold_same_text_ctrl
        if self.left_save_ctrl:
            self.left_save_ctrl.destory()
            del self.left_save_ctrl
        if self.right_save_ctrl:
            self.right_save_ctrl.destory()
            del self.right_save_ctrl
        if self.editor_ctrl:
            self.editor_ctrl.destory()
            del self.editor_ctrl
        del self.page_data
        del self.text_l
        del self.text_r


class CompareDirCtrl(CompareCtrl):
    '''
    两方对比文件夹
    '''
    pass

class TwoSideTextCmp(object):
    def __init__(self, textL, textR, fileL, fileR):
        self.text_l = textL
        self.text_r = textR
        self.input_file_l = fileL
        self.input_file_r = fileR
        self.unstable_chunks = []
        self.stable_chunks = []
        self._init_file()
        self.compare()

    def destory(self):
        self.input_file_l.destory()
        self.input_file_r.destory()
        del self.input_file_l
        del self.input_file_l
        del self.stable_chunks
        del self.unstable_chunks
        if self.text_l:
            self.text_l.destory()
            del self.text_l
        if self.text_r:
            self.text_r.destory()
            del self.text_r

    def compare(self):
        leftLineDatas = self.file_l.get_line_datas();
        rightLineDatas = self.file_r.get_line_datas();
        self._compare_chunk(leftLineDatas,rightLineDatas);

    def clear(self):
        self.text_l.ClearAll()
        self.text_r.ClearAll()
        self.unstable_chunks = []

    def _init_file(self):
        self.file_l = File(self.input_file_l)
        self.file_r = File(self.input_file_r)

    def diff_line_by_char(self, leftLineData, rightLineData):
        l_line = r_line = ""
        if leftLineData != None:
            l_line = leftLineData.get_show_content()
        if rightLineData != None:
            r_line = rightLineData.get_show_content()
        if leftLineData != None and rightLineData != None:
            if leftLineData.show_line_num == -1 or rightLineData.show_line_num == -1:
                pass
                # raise Exception("line data has not been add to stage")
            diffs = diff_obj.diff_main(l_line, r_line)
            lcs = diff_obj.get_lcs(diffs,False)
            if len(lcs) > 0:
                lcs_index = get_index_by_commstring(l_line, lcs)
                diff_index = get_diff_lcs_index(l_line, lcs_index)
                self.styled_text_by_index(diff_index, leftLineData.show_line_num, self.text_l)
                lcs_index = get_index_by_commstring(r_line, lcs)
                diff_index = get_diff_lcs_index(r_line, lcs_index)
                self.styled_text_by_index(diff_index, rightLineData.show_line_num, self.text_r)
            else:
                self.styled_text_by_index([(0, len(l_line))], leftLineData.show_line_num, self.text_l)
                self.styled_text_by_index([(0, len(r_line))], rightLineData.show_line_num, self.text_r)

    def styled_text_by_index(self, indexArr, lineNum, codeText):
        codeText.styled_text_by_index(indexArr, lineNum)

    # def styled_line_text(self, lineNum, codeText):
    #     start_index = codeText.PositionFromLine(lineNum)
    #     end_index = codeText.GetLineEndPosition(lineNum)
    #     codeText.StartStyling(start_index, CodeTextCtrl.DIFF_STYLE)
    #     codeText.SetStyling(end_index - start_index, CodeTextCtrl.DIFF_STYLE)

    def _compare_chunk(self, leftLineDataArr, rightLineDataArr):
        l_property_content_arr = get_content_from_line_data_arr(leftLineDataArr)
        r_property_content_arr = get_content_from_line_data_arr(rightLineDataArr)

        def addLineDatasToTextCtrl(leftLines, rightLines):
            for i in range(0, len(leftLines)):
                self.text_l.add_line_data(leftLines[i])
                self.text_r.add_line_data(rightLines[i])
                self.stable_chunks.append((leftLines[i], rightLines[i]))

        if cmp(l_property_content_arr, r_property_content_arr) == 0 :
            addLineDatasToTextCtrl(leftLineDataArr, rightLineDataArr)
            # 一样的代码直接添加到显示
            return
        diffs = diff_obj.diff_main(l_property_content_arr, r_property_content_arr)
        lcs_content_arr = diff_obj.get_lcs(diffs)
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
                l_index = l_property_content_arr.index(line, l_index + 1)
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
                r_index = r_property_content_arr.index(line, r_index + 1)
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
                    self._compare_unstable_chunk(leftLineDataArr, rightLineDataArr, left_diffs,
                                                  right_diffs)
                self.text_l.add_line_data(leftLineDataArr[l_lcs_index[i]])
                self.text_r.add_line_data(rightLineDataArr[r_lcs_index[i]])
                self.stable_chunks.append((leftLineDataArr[l_lcs_index[i]], rightLineDataArr[r_lcs_index[i]]))
            # 检查公共字符串后面有没有非稳定块
            last_l_index = l_lcs_index[len(l_lcs_index) - 1]
            last_r_index = r_lcs_index[len(r_lcs_index) - 1]
            left_diffs = get_all_index_by_start_and_end(last_l_index + 1, len(leftLineDataArr))
            right_diffs = get_all_index_by_start_and_end(last_r_index + 1, len(rightLineDataArr))
            if len(left_diffs) > 0 or len(right_diffs) > 0:
                self._compare_unstable_chunk(leftLineDataArr, rightLineDataArr, left_diffs,
                                             right_diffs)
        else:
            left_diffs = get_all_index_by_start_and_end(0, len(leftLineDataArr))
            right_diffs = get_all_index_by_start_and_end(0, len(rightLineDataArr))
            self._compare_unstable_chunk(leftLineDataArr, rightLineDataArr, left_diffs,
                                         right_diffs)
    def add_lines_unstable_mark(self, leftLineDatas, rightLineDatas):
        '''
        对行增加行标记，主要用于不稳定块前面
        :param leftLineDatas:
        :param centerLineDatas:
        :param rightLineDatas:
        :return:
        '''
        def addMarginLines(lineDatas,textCtrl):
            if lineDatas:
                for i in range(0, len(lineDatas)):
                    line = lineDatas[i]
                    if line.show_line_num != -1:
                        textCtrl.mark_diff_line(line.show_line_num)
        addMarginLines(leftLineDatas, self.text_l)
        addMarginLines(rightLineDatas, self.text_r)
    def _compare_unstable_chunk(self, l_lines, r_lines, left_diffs, right_diffs):
        # 不稳定块
        max_len = max(len(left_diffs), len(right_diffs))
        left_has_line = False
        right_has_line = False
        for i in range(0, max_len):
            left_line_data = None
            right_line_data = None
            if i >= len(left_diffs):
                self.text_l.add_blank_line()
                left_has_line = False
            else:
                left_line_data = l_lines[left_diffs[i]]
                self.text_l.add_line_data(left_line_data)
                left_has_line = True
            if i >= len(right_diffs):
                self.text_r.add_blank_line()
                right_has_line = False
            else:
                right_line_data = r_lines[right_diffs[i]]
                self.text_r.add_line_data(right_line_data)
                right_has_line = True
            self.diff_line_by_char(left_line_data, right_line_data)
            if left_has_line:
                self.text_l.mark_diff_line(left_line_data.show_line_num)
            if right_has_line:
                self.text_r.mark_diff_line(right_line_data.show_line_num)
            chunk = UnStableChunk(left_line_data, None, right_line_data, self.text_l.get_last_line_data(),
                                  self.text_r.get_last_line_data())
            self.unstable_chunks.append(chunk)
class TwoSidePrefabCmp(TwoSideTextCmp):

    def _init_file(self):
        self.file_l = PrefabFile(self.input_file_l)
        self.file_r = PrefabFile(self.input_file_r)
        self.text_l.text.SetEOLMode(stc.STC_EOL_LF)
        self.text_r.text.SetEOLMode(stc.STC_EOL_LF)

    def compare(self):
        self.clear()
        addKey = []
        rightLineDatas = []
        self.text_l.add_line_data(self.file_l.yaml_version_line)
        self.text_r.add_line_data(self.file_r.yaml_version_line)
        self.diff_line_by_char(self.file_l.yaml_version_line, self.file_r.yaml_version_line)
        self.text_l.add_line_data(self.file_l.unity_tag_line)
        self.text_r.add_line_data(self.file_r.unity_tag_line)
        self.diff_line_by_char(self.file_l.unity_tag_line, self.file_r.unity_tag_line)
        leftNewArr = []
        for key in self.file_l.element_dic:
            l_element = self.file_l.element_dic[key]
            addKey.append(key)
            leftLineDatas = l_element.line_datas
            if self.file_r.element_dic.has_key(key):
                rightLineDatas = self.file_r.element_dic[key].line_datas
                self._compare_chunk(leftLineDatas, rightLineDatas)
            else:
                leftNewArr.extend(leftLineDatas)
        self._compare_chunk(leftNewArr, [])
        for key in self.file_r.element_dic:
            if key in addKey:
                continue
            else:
                rightLineDatas = self.file_r.element_dic[key].line_datas
                self._compare_chunk([], rightLineDatas)

class MergeCtrl(CompareCtrl):
    def refresh_compare(self, cmpOption):
        self.cmp_option = cmpOption

    def set_output_path(self,path):
        self.output_path = path

    def get_merge_result(self):
        return "must be override"

    def refresh_filter(self, inFilter):
        pass

class MergeDirCtrl(MergeCtrl):
    '''
    三方文件目录合并计算
    '''
    def __init__(self, treeL, treeC, treeR, pageData):
        CompareCtrl.__init__(self)
        self.tree_l = treeL
        self.tree_c = treeC
        self.tree_r = treeR
        self.page_data = pageData
        self._init_event()
        self.is_complete = False
        self.same_files = []
        self.conflict_files = []
        self.mergeable_files = []
        self.show_filter = CompareFilter.ALL
        # self.refresh_compare(pageData.cmp_option)

    def _init_event(self):
        self.tree_l.Bind(EVT_FRAME_EVENT, self._tree_ready_handler)
        self.tree_c.Bind(EVT_FRAME_EVENT, self._tree_ready_handler)
        self.tree_r.Bind(EVT_FRAME_EVENT, self._tree_ready_handler)

    def _remove_event(self):
        self.tree_l.Unbind(EVT_FRAME_EVENT)
        self.tree_c.Unbind(EVT_FRAME_EVENT)
        self.tree_r.Unbind(EVT_FRAME_EVENT)

    def _tree_ready_handler(self,evt):
        self.compare()
        pass

    def refresh_compare(self, cmpOption):
        self.tree_l.refresh_filters(cmpOption.filter)
        self.tree_c.refresh_filters(cmpOption.filter)
        self.tree_r.refresh_filters(cmpOption.filter)
        self.compare()

    def compare(self):
        if self.tree_l.get_ready() and self.tree_c.get_ready() and self.tree_r.get_ready():
            l_item_dic = self.tree_l.get_item_dic()
            c_item_dic = self.tree_c.get_item_dic()
            r_item_dic = self.tree_r.get_item_dic()
            self.same_files = []
            self.conflict_files = []
            self.mergeable_files = []
            for key in l_item_dic:
                if c_item_dic.has_key(key) and r_item_dic.has_key(key):
                    l_itemData = self.tree_l.get_item_data_by_relative_path(key)
                    c_itemData = self.tree_c.get_item_data_by_relative_path(key)
                    r_itemData = self.tree_r.get_item_data_by_relative_path(key)
                    if l_itemData.isDir:
                        continue
                    cmp_cls = get_merge_by_type(self.page_data.cmp_option.file_format)
                    l_file = get_parent_path(self.tree_l.get_path()) + "/" + key
                    c_file = get_parent_path(self.tree_c.get_path()) + "/" + key
                    r_file = get_parent_path(self.tree_r.get_path()) + "/" + key
                    l_text = CodeTextCtrl(render=False)
                    c_text = CodeTextCtrl(render=False)
                    r_text = CodeTextCtrl(render=False)
                    d_text = CodeTextCtrl(render=False)
                    print "compare:"
                    print l_file
                    print c_file
                    print r_file
                    print "-------------------"
                    cmp = cmp_cls(l_text, c_text, r_text, l_file, c_file, r_file, d_text,
                                  self.page_data.cmp_option)
                    if cmp.is_same():
                        self.tree_l.set_item_normal(self.tree_l.ge_item_by_relative_path(key)[0])
                        self.tree_c.set_item_normal(self.tree_c.ge_item_by_relative_path(key)[0])
                        self.tree_r.set_item_normal(self.tree_r.ge_item_by_relative_path(key)[0])
                        l_itemData.compare_result = CompareFilter.SAME
                        c_itemData.compare_result = CompareFilter.SAME
                        r_itemData.compare_result = CompareFilter.SAME
                        self.same_files.append(key)
                    else:
                        if cmp.get_has_conflict():
                            self.tree_l.set_item_conflict(self.tree_l.ge_item_by_relative_path(key)[0])
                            self.tree_c.set_item_conflict(self.tree_c.ge_item_by_relative_path(key)[0])
                            self.tree_r.set_item_conflict(self.tree_r.ge_item_by_relative_path(key)[0])
                            l_itemData.compare_result = CompareFilter.CONFLICT
                            c_itemData.compare_result = CompareFilter.CONFLICT
                            r_itemData.compare_result = CompareFilter.CONFLICT
                            self.conflict_files.append(key)
                        else:
                            self.tree_l.set_item_merged(self.tree_l.ge_item_by_relative_path(key)[0])
                            self.tree_c.set_item_merged(self.tree_c.ge_item_by_relative_path(key)[0])
                            self.tree_r.set_item_merged(self.tree_r.ge_item_by_relative_path(key)[0])
                            l_itemData.compare_result = CompareFilter.MERGEABLE
                            c_itemData.compare_result = CompareFilter.MERGEABLE
                            r_itemData.compare_result = CompareFilter.MERGEABLE
                            self.mergeable_files.append(key)
            self.is_complete = True


    def destory(self):
        self._remove_event()
        self.tree_l = None
        self.tree_c = None
        self.tree_r = None
        self.pageData = None

    def get_merge_result(self):
        if self.is_complete:
            result_str = ""
            result_str += str(len(self.same_files))+" same file(s)\n"
            result_str += str(len(self.mergeable_files)) + " mergeable file(s)\n"
            result_str += str(len(self.conflict_files)) + " conflict file(s)\n"
            return result_str
        else:
            return "not completed"
    def refresh_filter(self, inFilter):
        if inFilter != self.show_filter:
            self.show_filter = inFilter
            self.tree_l.refresh_merge_filter(inFilter)
            self.tree_c.refresh_merge_filter(inFilter)
            self.tree_r.refresh_merge_filter(inFilter)



class MergeTextCtrl(MergeCtrl):
    '''
    三方文本合并计算
    '''
    def __init__(self, textL, textC, textR, textD, pageData):
        CompareCtrl.__init__(self)
        self.text_l = textL
        self.text_c = textC
        self.text_r = textR
        self.text_d = textD
        self.cmp = None
        self.scrollctrl = MergeTextScrollCtrl(textL.text,textC.text,textR.text, textD.text)
        self.page_data = pageData
        self.init_data(pageData)


    def init_data(self,pageData):
        l_file = pageData.leftPath
        c_file = pageData.centerPath
        r_file = pageData.rightPath
        self.output_path = pageData.get_output_path()
        cmp_cls = get_merge_by_type(pageData.cmp_option.file_format)
        self.cmp = cmp_cls(self.text_l, self.text_c, self.text_r, l_file, c_file, r_file, self.text_d, pageData.cmp_option)

    def get_merge_result(self):
        result_str = ""
        if self.cmp:
            chunks = self.cmp.unstable_chunks
            if len(chunks) > 0:
                conflict_num = 0
                for i in range(0, len(chunks)):
                    chunk = chunks[i]
                    if chunk.is_confilcted:
                        conflict_num += 1
                merge_num = len(chunks) - conflict_num
                result_str += str(merge_num) + " mergeable line(s)\n"
                result_str += str(conflict_num) + " conflict line(s)\n"
            else:
                result_str = "no different line"
        return result_str

    def refresh_compare(self, cmpOption):
        if self.cmp.get_cmp_type() != cmpOption.file_format:
            self.cmp.destory()
            l_file = self.page_data.leftPath
            c_file = self.page_data.centerPath
            r_file = self.page_data.rightPath
            cmp_cls = get_merge_by_type(cmpOption.file_format)
            self.cmp = cmp_cls(self.text_l, self.text_c, self.text_r, l_file, c_file, r_file, self.text_d, cmpOption)
        else:
            self.cmp.refresh_option(cmpOption)

    def save_to_output(self):
        file_text = self.cmp.get_output()
        pass

    def has_conflict(self):
        chunks = self.cmp.unstable_chunks
        if len(chunks) > 0:
            for chunk in chunks:
                if chunk.is_confilcted:
                    return True
        return False

    def go_to_unstable_chunk(self, index):
        chunk = self.cmp.unstable_chunks[index]
        if chunk.leftLineData:
            self.text_l.text.SetFirstVisibleLine(chunk.leftLineData.show_line_num)
        else:
            self.text_l.text.SetFirstVisibleLine(chunk.leftStableLine.show_line_num)
        if chunk.centerLineData:
            self.text_c.text.SetFirstVisibleLine(chunk.centerLineData.show_line_num)
        if chunk.rightLineData:
            self.text_r.text.SetFirstVisibleLine(chunk.rightLineData.show_line_num)
        else:
            self.text_r.text.SetFirstVisibleLine(chunk.rightStableLine.show_line_num)

    def destory(self):
        self.pageData = None
        self.text_l = None
        self.text_c = None
        self.text_r = None
        self.text_d = None
        self.cmp = None
        self.scrollctrl.destory()
        self.scrollctrl = None

class ThreeSideTextCompare:
    def __init__(self,textL,textC,textR,l_file,c_file,r_file,textOutput,compareOption = CompareOption()):
        self.text_l = textL
        self.text_c = textC
        self.text_r = textR
        self.text_d = textOutput
        self.l_input_file = l_file
        self.c_input_file = c_file
        self.r_input_file = r_file
        self.cmp_option = compareOption
        self.output_modifys = []
        self.unstable_chunks = []
        self.show_conflict_index = 0
        self.init_file()
        self.compare()

    def get_has_conflict(self):
        for i in range(0, len(self.output_modifys)):
            modify = self.output_modifys[i]
            if modify.type == LineModify.CONFLICT_TYPE:
                return True
        return False

    def is_same(self):
        return len(self.unstable_chunks) == 0

    def get_cmp_type(self):
        return FileFormat.NormalText

    def init_file(self):
        self.l_file = File(self.l_input_file,self.cmp_option.ignore_blank)
        self.c_file = File(self.c_input_file,self.cmp_option.ignore_blank)
        self.r_file = File(self.r_input_file,self.cmp_option.ignore_blank)


    def refresh_option(self,value):
        self.cmp_option = value
        self.init_file()
        self.compare()


    def diff_line_by_char(self,leftLineData,centerLineData,rightLineData):
        l_line = c_line = r_line = ""
        if leftLineData != None:
            l_line = leftLineData.get_show_content()
        if centerLineData != None:
            c_line = centerLineData.get_show_content()
        if rightLineData != None:
            r_line = rightLineData.get_show_content()
        if leftLineData != None and centerLineData != None and l_line != c_line:
            if leftLineData.show_line_num == -1 or centerLineData.show_line_num == -1:
                pass
                # raise Exception("line data has not been add to stage")
            diffs = diff_obj.diff_main(l_line, c_line)
            lcs_index = diff_obj.get_lcs_indexs_by_text1(diffs, l_line)
            if len(lcs_index) > 0:
                diff_index = get_diff_lcs_index(l_line, lcs_index)
                self.styled_text_by_index(diff_index, leftLineData.show_line_num, self.text_l)
        if rightLineData != None and centerLineData != None and c_line != r_line:
            if rightLineData.show_line_num == -1 or centerLineData.show_line_num == -1:
                pass
                # raise Exception("line data has not been add to stage")
            diffs = diff_obj.diff_main(r_line, c_line)
            lcs_index = diff_obj.get_lcs_indexs_by_text1(diffs, r_line)
            if len(lcs_index) > 0:
                diff_index = get_diff_lcs_index(r_line, lcs_index)
                self.styled_text_by_index(diff_index, rightLineData.show_line_num, self.text_r)
        if centerLineData == None and leftLineData != None and rightLineData != None and l_line != r_line:
            if rightLineData.show_line_num == -1 or leftLineData.show_line_num == -1:
                pass
                # raise Exception("line data has not been add to stage")
            diffs = diff_obj.diff_main(l_line, r_line)
            lcs_index = diff_obj.get_lcs_indexs_by_text1(diffs, l_line)
            if len(lcs_index) > 0:
                diff_index = get_diff_lcs_index(l_line, lcs_index)
                self.styled_text_by_index(diff_index, leftLineData.show_line_num, self.text_l)

    def styled_text_by_index(self,indexArr,lineNum,codeText):
        codeText.styled_text_by_index(indexArr, lineNum)

    # def styled_line_text(self,lineNum,codeText):
    #     start_index = codeText.PositionFromLine(lineNum)
    #     end_index = codeText.GetLineEndPosition(lineNum)
    #     codeText.StartStyling(start_index, CodeTextCtrl.DIFF_STYLE)
    #     codeText.SetStyling(end_index - start_index, CodeTextCtrl.DIFF_STYLE)

    def compare(self):
        loglist = []
        loglist.append("start TextCompare -------------------------------------------\n")
        loglist.append("leftFile:" + self.l_file.url + "\n")
        loglist.append("centerFile:" + self.c_file.url + "\n")
        loglist.append("rightFile:" + self.r_file.url + "\n")
        logger.log_list(loglist)

        self.text_l.ClearAll()
        self.text_c.ClearAll()
        self.text_r.ClearAll()
        self.text_d.ClearAll()
        self.output_modifys = []
        self.unstable_chunks = []
        self.merger = TextMerge(self.cmp_option.merge_option)
        self._compare_chunk(self.l_file.get_line_datas(),self.c_file.get_line_datas(),self.r_file.get_line_datas())
        self.show_output()

    def destory(self):
        self.text_l = None
        self.text_c = None
        self.text_r = None
        self.text_d = None
        self.l_file.destory()
        self.c_file.destory()
        self.r_file.destory()

    def show_output(self):
        if self.cmp_option.merge_option == CompareOption.MERGE_TO_LEFT:
            copy_text = self.text_l
        else:
            copy_text = self.text_r
        self.text_d.clone_text_ctrl(copy_text)
        for i in range(0, len(self.output_modifys)):
            modify = self.output_modifys[i]
            self.text_d.modify_text(modify)




    def _compare_disorder_block(self, l_import_arr, c_import_arr, r_import_arr):
        def addMarginFlag(lineData, textCtrl):
            if lineData and lineData.show_line_num != -1:
                textCtrl.mark_conflict_line(lineData.show_line_num)
        # 比对import 使用无顺序的对比方法,同时执行全量字符对比策略，不同的就是新增
        l_import_content = get_content_from_line_data_arr(l_import_arr)
        r_import_content = get_content_from_line_data_arr(r_import_arr)
        l_added_index_arr = []
        r_added_index_arr = []
        is_stable = True
        l_line = None
        c_line = None
        r_line = None

        for i in range(0, len(c_import_arr)):  # 先从中间开始遍历
            c_line = c_import_arr[i]
            self.text_c.add_line_data(c_line)
            line_content = c_line.get_no_blank_content()
            is_stable = True
            if line_content not in l_import_content:
                self.text_l.add_blank_line(1)
                l_line = None
                is_stable = False
            else:
                index = l_import_content.index(line_content)
                l_added_index_arr.append(index)
                l_line = l_import_arr[index]
                self.text_l.add_line_data(l_line)
            if line_content not in r_import_content:
                self.text_r.add_blank_line(1)
                r_line = None
                is_stable = False
            else:
                index = r_import_content.index(line_content)
                r_added_index_arr.append(index)
                r_line = r_import_arr[index]
                self.text_r.add_line_data(r_line)
            if not is_stable:
                chunk = UnStableChunk(l_line, c_line, r_line, self.text_l.get_last_line_data(), self.text_r.get_last_line_data())
                addMarginFlag(l_line,self.text_l)
                addMarginFlag(c_line,self.text_c)
                addMarginFlag(r_line,self.text_r)
                self.unstable_chunks.append(chunk)
                modify = self.merger.merge_disorder_line(chunk)
                if modify:
                    self.output_modifys.append(modify)

        for i in range(0, len(l_import_arr)):  # 再次从左边开始遍历
            if i not in l_added_index_arr:
                import_line_data = l_import_arr[i]
                line_content = import_line_data.get_show_content()
                self.text_l.add_line_data(l_import_arr[i])
                self.text_c.add_blank_line(1)
                if line_content not in r_import_content:
                    self.text_r.add_blank_line(1)
                    r_line = None
                else:
                    index = r_import_content.index(line_content)
                    r_added_index_arr.append(index)
                    r_line = r_import_arr[index]
                    self.text_r.add_line_data(r_import_arr[index])
                chunk = UnStableChunk(import_line_data, None, r_line, self.text_l.get_last_line_data(), self.text_r.get_last_line_data())
                self.unstable_chunks.append(chunk)
                modify = self.merger.merge_disorder_line(chunk)
                if modify:
                    self.output_modifys.append(modify)
                addMarginFlag(import_line_data, self.text_l)
                addMarginFlag(r_line, self.text_r)
        if len(r_added_index_arr) < len(r_import_arr):  # 最后在判断右边是否有未遍历到的
            for i in range(0, len(r_import_arr)):
                if i not in r_added_index_arr:
                    import_line_data = r_import_arr[i]
                    self.text_r.add_line_data(r_import_arr[i])
                    self.text_c.add_blank_line(1)
                    self.text_l.add_blank_line(1)
                    chunk = UnStableChunk(None, None, import_line_data, self.text_l.get_last_line_data(), self.text_r.get_last_line_data())
                    self.unstable_chunks.append(chunk)
                    modify = self.merger.merge_disorder_line(chunk)
                    if modify:
                        self.output_modifys.append(modify)
                    addMarginFlag(import_line_data, self.text_r)

    # 比较一块代码，计算出稳定块和非稳定块
    def _compare_chunk(self, leftLineDataArr, centerLineDataArr, rightLineDataArr):
        l_property_content_arr = get_content_from_line_data_arr(leftLineDataArr)
        c_property_content_arr = get_content_from_line_data_arr(centerLineDataArr)
        r_property_content_arr = get_content_from_line_data_arr(rightLineDataArr)

        def addLineDatasToTextCtrl(textCtrl, lineDatas):
            for i in range(0, len(lineDatas)):
                textCtrl.add_line_data(lineDatas[i])

        if cmp(l_property_content_arr, c_property_content_arr) == 0 and cmp(c_property_content_arr,
                                                                            r_property_content_arr) == 0:
            addLineDatasToTextCtrl(self.text_l, leftLineDataArr)
            addLineDatasToTextCtrl(self.text_c, centerLineDataArr)
            addLineDatasToTextCtrl(self.text_r, rightLineDataArr)
            # 一样的代码直接添加到显示
            return

        diffs = diff_obj.diff_main(l_property_content_arr, c_property_content_arr)
        lcs_content_lc = diff_obj.get_lcs(diffs)
        # try:
        diffs = diff_obj.diff_main(lcs_content_lc, r_property_content_arr)
        # except:
        # print "error happened"
        lcs_content_arr = diff_obj.get_lcs(diffs)
        if len(lcs_content_arr) > 0:
            # 计算出公共行数索引
            l_lcs_index = []
            c_lcs_index = []
            r_lcs_index = []
            l_index = -1  # 开始搜索索引
            c_index = -1
            r_index = -1
            for i in range(0, len(lcs_content_arr)):
                has_unstable_chunk = False
                line = lcs_content_arr[i]
                left_diffs = []
                center_diffs = []
                right_diffs = []
                l_index = l_property_content_arr.index(line, l_index + 1)
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
                c_index = c_property_content_arr.index(line, c_index + 1)
                c_lcs_index.append(c_index)
                if i == 0:
                    if c_index > 0:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(0, c_index)
                else:
                    lines = c_lcs_index[i] - c_lcs_index[i - 1]
                    if lines > 1:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(c_lcs_index[i - 1] + 1, c_lcs_index[i])
                r_index = r_property_content_arr.index(line, r_index + 1)
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
                    self._compare_unstable_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs,
                                                 center_diffs, right_diffs)
                self.text_l.add_line_data(leftLineDataArr[l_lcs_index[i]])
                self.text_c.add_line_data(centerLineDataArr[c_lcs_index[i]])
                self.text_r.add_line_data(rightLineDataArr[r_lcs_index[i]])
            # 检查公共字符串后面有没有非稳定块
            last_l_index = l_lcs_index[len(l_lcs_index) - 1]
            last_c_index = c_lcs_index[len(c_lcs_index) - 1]
            last_r_index = r_lcs_index[len(r_lcs_index) - 1]
            left_diffs = get_all_index_by_start_and_end(last_l_index + 1, len(leftLineDataArr))
            center_diffs = get_all_index_by_start_and_end(last_c_index + 1, len(centerLineDataArr))
            right_diffs = get_all_index_by_start_and_end(last_r_index + 1, len(rightLineDataArr))
            if len(left_diffs) > 0 or len(center_diffs) > 0 or len(right_diffs) > 0:
                self._compare_unstable_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs,
                                             center_diffs,
                                             right_diffs)
        else:
            left_diffs = get_all_index_by_start_and_end(0, len(leftLineDataArr))
            center_diffs = get_all_index_by_start_and_end(0, len(centerLineDataArr))
            right_diffs = get_all_index_by_start_and_end(0, len(rightLineDataArr))
            self._compare_unstable_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs, center_diffs,
                                         right_diffs)

    def add_lines_unstable_mark(self, leftLineDatas, centerLineDatas, rightLineDatas):
        '''
        对行增加行标记，主要用于不稳定块前面
        :param leftLineDatas:
        :param centerLineDatas:
        :param rightLineDatas:
        :return:
        '''
        def addMarginLines(lineDatas,textCtrl):
            if lineDatas:
                for i in range(0, len(lineDatas)):
                    line = lineDatas[i]
                    if line.show_line_num != -1:
                        textCtrl.mark_conflict_line(line.show_line_num)
        addMarginLines(leftLineDatas, self.text_l)
        addMarginLines(centerLineDatas, self.text_c)
        addMarginLines(rightLineDatas, self.text_r)


    def _compare_unstable_chunk(self, l_lines, c_lines, r_lines, left_diffs, center_diffs, right_diffs):
        # 不稳定块
        max_len = max(len(left_diffs), len(center_diffs), len(right_diffs))
        left_has_line = False
        center_has_line = False
        right_has_line = False
        for i in range(0, max_len):
            left_line_data = None
            center_line_data = None
            right_line_data = None
            if i >= len(left_diffs):
                self.text_l.add_blank_line()
            else:
                left_line_data = l_lines[left_diffs[i]]
                self.text_l.add_line_data(left_line_data)
                left_has_line = True
            if i >= len(center_diffs):
                self.text_c.add_blank_line()
            else:
                center_line_data = c_lines[center_diffs[i]]
                self.text_c.add_line_data(center_line_data)
                center_has_line = True
            if i >= len(right_diffs):
                self.text_r.add_blank_line()
            else:
                right_line_data = r_lines[right_diffs[i]]
                self.text_r.add_line_data(right_line_data)
                right_has_line = True
            self.diff_line_by_char(left_line_data, center_line_data, right_line_data)
            chunk = UnStableChunk(left_line_data, center_line_data, right_line_data, self.text_l.get_last_line_data(),
                                  self.text_r.get_last_line_data())
            self.unstable_chunks.append(chunk)
            modify = self.merger.merge_line(chunk)
            if modify:
                self.output_modifys.append(modify)
        left_lines = ThreeSideAsCompare.get_line_by_index(l_lines, left_diffs)
        center_lines = ThreeSideAsCompare.get_line_by_index(c_lines, center_diffs)
        right_lines = ThreeSideAsCompare.get_line_by_index(r_lines, right_diffs)
        self.add_lines_unstable_mark(left_lines,center_lines,right_lines)
        center_line_check_list = []
        right_line_check_list = []
        for i in range(0, len(left_diffs)):
            left_line_data = l_lines[left_diffs[i]]
            c_match_line = get_same_line_from_lines(left_line_data, center_lines)
            r_match_line = get_same_line_from_lines(left_line_data, right_lines)
            if c_match_line or r_match_line:
                self.text_l.set_line_match_background(left_line_data.show_line_num)
                if c_match_line:
                    self.text_c.set_line_match_background(c_match_line.show_line_num)
                    center_line_check_list.append(c_match_line)
                elif r_match_line:
                    self.text_r.set_line_match_background(r_match_line.show_line_num)
                    right_line_check_list.append(r_match_line)
        for i in range(0, len(center_diffs)):
            center_line_data = c_lines[center_diffs[i]]
            if center_line_data not in center_line_check_list:
                r_match_line = get_same_line_from_lines(center_line_data, right_lines)
                if r_match_line:
                    self.text_c.set_line_match_background(center_line_data.show_line_num)
                    self.text_r.set_line_match_background(r_match_line.show_line_num)




class ThreeSideAsCompare(ThreeSideTextCompare):
    def __init__(self,textL,textC,textR,l_file,c_file,r_file,textOutput,mergeOption):
        ThreeSideTextCompare.__init__(self, textL, textC, textR, l_file, c_file, r_file, textOutput, mergeOption)
    def get_cmp_type(self):
        return FileFormat.AS
    def init_file(self):
        self.l_file = AsFile(self.l_input_file,self.cmp_option.ignore_blank,self.cmp_option.ignore_comment)
        self.c_file = AsFile(self.c_input_file,self.cmp_option.ignore_blank,self.cmp_option.ignore_comment)
        self.r_file = AsFile(self.r_input_file,self.cmp_option.ignore_blank,self.cmp_option.ignore_comment)


    def compare(self):
        loglist = []
        loglist.append("start AsCompare -------------------------------------------\n")
        loglist.append("leftFile:"+self.l_file.url+"\n")
        loglist.append("centerFile:"+self.c_file.url+"\n")
        loglist.append("rightFile:"+self.r_file.url+"\n")
        logger.log_list(loglist)

        self.text_l.ClearAll()
        self.text_c.ClearAll()
        self.text_r.ClearAll()
        self.text_d.ClearAll()
        self.output_modifys = []
        self.unstable_chunks = []
        l_file = self.l_file
        c_file = self.c_file
        r_file = self.r_file
        # 先比对包名
        self.text_l.add_line_data(l_file.package_line, "{")
        self.text_c.add_line_data(c_file.package_line, "{")
        self.text_r.add_line_data(r_file.package_line, "{")
        if not is_stable_line(l_file.package_line, c_file.package_line,r_file.package_line):
            self.diff_line_by_char(l_file.package_line,c_file.package_line,r_file.package_line)
            un_chunk = UnStableChunk(l_file.package_line,c_file.package_line,r_file.package_line)
            self.unstable_chunks.append(un_chunk)
            modify = ASCodeMerge.merge_independent_line(chunk=un_chunk, mergeOption=self.cmp_option.merge_option)
            if modify:
                self.output_modifys.append(modify)
        if not (l_file.inner_cls.class_line_data and c_file.inner_cls.class_line_data and r_file.inner_cls.class_line_data):
            print "skip file:"+l_file.url
            return
        # 比对包中类
        self._compare_as_class(l_file.inner_cls,c_file.inner_cls,r_file.inner_cls)
        # 添加package块后缀符号
        self.text_l.add_line_data(LineData.GetlineData("}"))
        self.text_c.add_line_data(LineData.GetlineData("}"))
        self.text_r.add_line_data(LineData.GetlineData("}"))
        # 比对包外类
        l_cls_names = l_file.outer_cls_dic.keys()
        c_cls_names = c_file.outer_cls_dic.keys()
        r_cls_names = r_file.outer_cls_dic.keys()
        all_cls_names = get_all_element_by_arr(l_cls_names, c_cls_names, r_cls_names)
        for name in all_cls_names:
            l_cls = None
            c_cls = None
            r_cls = None
            left_line_datas = []
            center_line_datas = []
            right_line_datas = []
            if l_file.outer_cls_dic.has_key(name):
                l_cls = l_file.outer_cls_dic[name]
                left_line_datas = l_cls.get_all_line_datas()
            if c_file.outer_cls_dic.has_key(name):
                c_cls = c_file.outer_cls_dic[name]
                center_line_datas = c_cls.get_all_line_datas()
            if r_file.outer_cls_dic.has_key(name):
                r_cls = r_file.outer_cls_dic[name]
                right_line_datas = r_cls.get_all_line_datas()
            if l_cls != None and c_cls != None and r_cls != None:
                self._compare_as_class(l_cls, c_cls, r_cls)
            else:
                self._compare_chunk(left_line_datas, center_line_datas, right_line_datas)

        l_other_lines = l_file.other_lines
        c_other_lines = c_file.other_lines
        r_other_lines = r_file.other_lines
        if len(l_other_lines) > 0 or len(c_other_lines) > 0 or len(r_other_lines) > 0:
            self._compare_chunk(l_other_lines, c_other_lines, r_other_lines)

        self.show_output()

    def _compare_as_class(self, l_cls, c_cls, r_cls):
        self.merger = ASCodeMerge(l_cls, c_cls, r_cls, self.cmp_option.merge_option)
        self._compare_import_block(l_cls,c_cls,r_cls)
        # 比对 class line
        self.text_l.add_line_data(l_cls.class_line_data, "{")
        self.text_c.add_line_data(c_cls.class_line_data, "{")
        self.text_r.add_line_data(r_cls.class_line_data, "{")
        if not is_stable_line(l_cls.class_line_data,c_cls.class_line_data,r_cls.class_line_data):
            self.diff_line_by_char(l_cls.class_line_data,c_cls.class_line_data,r_cls.class_line_data)
            un_chunk = UnStableChunk(l_cls.class_line_data, c_cls.class_line_data, r_cls.class_line_data)
            self.unstable_chunks.append(un_chunk)
            modify = ASCodeMerge.merge_independent_line(chunk=un_chunk, mergeOption=self.cmp_option.merge_option)
            if modify:
                self.output_modifys.append(modify)

        # 比对 var
        self._compare_property_block(l_cls, c_cls, r_cls)
        # 比对 function
        self._compare_function_block(l_cls, c_cls, r_cls)
        # 添加类块后缀符号
        self.text_l.add_line_data(LineData.GetlineData("}"))
        self.text_c.add_line_data(LineData.GetlineData("}"))
        self.text_r.add_line_data(LineData.GetlineData("}"))

    def _compare_import_block(self,l_cls,c_cls,r_cls):
        l_import_arr = l_cls.import_arr
        c_import_arr = c_cls.import_arr
        r_import_arr = r_cls.import_arr
        self._compare_disorder_block(l_import_arr, c_import_arr, r_import_arr)

    # 比较属性
    def _compare_property_block(self,l_cls, c_cls, r_cls):
        self._compare_chunk(l_cls.property_arr, c_cls.property_arr, r_cls.property_arr)
    # 比较方法
    def _compare_function_block(self,l_cls, c_cls, r_cls):
        l_fun_names = l_cls.function_dic.keys()
        c_fun_names = c_cls.function_dic.keys()
        r_fun_names = r_cls.function_dic.keys()
        all_fun_names = get_all_element_by_arr(l_fun_names, c_fun_names, r_fun_names)
        left_line_datas = []
        center_line_datas = []
        right_line_datas = []
        for name in all_fun_names:
            left_line_datas = []
            center_line_datas = []
            right_line_datas = []
            if l_cls.function_dic.has_key(name):
                left_line_datas = l_cls.function_dic[name]
            if c_cls.function_dic.has_key(name):
                center_line_datas = c_cls.function_dic[name]
            if r_cls.function_dic.has_key(name):
                right_line_datas = r_cls.function_dic[name]
            self._compare_chunk(left_line_datas, center_line_datas, right_line_datas)

    def _compare_unstable_chunk(self, l_lines, c_lines, r_lines, left_diffs, center_diffs, right_diffs):
        # 不稳定块
        left_lines = get_line_by_index(l_lines, left_diffs)
        center_lines = get_line_by_index(c_lines, center_diffs)
        right_lines = get_line_by_index(r_lines, right_diffs)
        # self.add_lines_unstable_mark(left_lines, center_lines, right_lines)# 标记非稳定块
        # 计算匹配索引
        r_last_index = -1
        l_last_index = -1
        l_result_indexs = []
        r_result_indexs = []
        def get_empty_indexs(l):
            arr = []
            for i in range(0, l):
                arr.append(-1)
            return arr
        def get_compare_indexs(lastIndex, curIndex, length):
            if length <= 0:
                raise Exception("length cannot <= 0")
            if curIndex == lastIndex + 1:
                if length > 1:
                    result_arr = get_empty_indexs(length - 1)
                    result_arr.append(curIndex)
                else:
                    return [curIndex]
            else:
                result_arr = get_all_index_by_start_and_end(lastIndex + 1, curIndex)
                temp_l = length - len(result_arr)
                if temp_l > 1:
                    result_arr.extend(get_empty_indexs(temp_l - 1))
                result_arr.append(curIndex)
            return result_arr
        for i in range(0, len(left_lines)):
            left_line_data = left_lines[i]
            r_match_index = get_match_index_from_lines(left_line_data, right_lines, r_last_index + 1)
            if r_match_index != -1:
                l_len = i - l_last_index
                r_len = r_match_index - r_last_index
                add_len = max(l_len, r_len)
                l_result_indexs.extend(get_compare_indexs(l_last_index, i, add_len))
                r_result_indexs.extend(get_compare_indexs(r_last_index, r_match_index, add_len))
                l_last_index = i
                r_last_index = r_match_index
        # 循环后对于没有匹配上的行进行处理
        if l_last_index < len(left_lines) - 1:
            l_len = len(left_lines) - 1 - l_last_index
        else:
            l_len = 0
        if r_last_index < len(right_lines) - 1:
            r_len = len(right_lines) - 1 - r_last_index
        else:
            r_len = 0
        add_len = max(l_len, r_len)
        if add_len > 0:
            if l_len > 0:
                l_result_indexs.extend(get_compare_indexs(l_last_index, len(left_lines) - 1, add_len))
            else:
                l_result_indexs.extend(get_empty_indexs(add_len))
            if r_len > 0:
                r_result_indexs.extend(get_compare_indexs(r_last_index, len(right_lines) - 1, add_len))
            else:
                r_result_indexs.extend(get_empty_indexs(add_len))
        # 对于center进行匹配处理
        c_result_indexs = get_empty_indexs(len(l_result_indexs))
        l_last_index = -1
        c_last_index = -1
        r_last_index = -1
        c_last_insert_index = -1
        def insert_empty_index(arr, index, num):
            for i in range(0, num):
                arr.insert(index, -1)
        for i in range(0, len(center_lines)):
            center_line_data = center_lines[i]
            l_match_index = get_match_index_from_lines(center_line_data, left_lines, l_last_index + 1)
            if l_match_index != -1:
                c_insert_index = l_result_indexs.index(l_match_index)
                t = (i - c_last_index) - (c_insert_index - c_last_insert_index)
                if t > 0:
                    # 中间索引不够，需要插入
                    insert_empty_index(l_result_indexs, c_last_insert_index + 1, t)
                    insert_empty_index(c_result_indexs, c_last_insert_index + 1, t)
                    insert_empty_index(r_result_indexs, c_last_insert_index + 1, t)
                    c_insert_index += t
                c_result_indexs[c_insert_index] = i
                if i - c_last_index > 1:
                    temp_index = 0
                    for m in range(c_last_index + 1, i):
                        temp_index += 1
                        c_result_indexs[c_last_insert_index + temp_index] = m
                c_last_index = i
                c_last_insert_index = c_insert_index
                l_last_index = l_match_index
            else:
                r_match_index = get_match_index_from_lines(center_line_data, right_lines, r_last_index + 1)
                if r_match_index != -1:
                    c_insert_index = r_result_indexs.index(r_match_index)
                    t = (i - c_last_index) - (c_insert_index - c_last_insert_index)
                    if t > 0:
                        # 中间索引不够，需要插入
                        insert_empty_index(l_result_indexs, c_last_insert_index + 1, t)
                        insert_empty_index(c_result_indexs, c_last_insert_index + 1, t)
                        insert_empty_index(r_result_indexs, c_last_insert_index + 1, t)
                        c_insert_index += t
                    c_result_indexs[c_insert_index] = i
                    if i - c_last_index > 1:
                        temp_index = 0
                        for m in range(c_last_index + 1, i):
                            temp_index += 1
                            c_result_indexs[c_last_insert_index + temp_index] = m
                    c_last_index = i
                    c_last_insert_index = c_insert_index
                    r_last_index = r_match_index
                else:
                    c_insert_index = c_last_insert_index + 1
                    if c_insert_index >= len(c_result_indexs):
                        insert_empty_index(l_result_indexs, c_last_insert_index + 1, 1)
                        insert_empty_index(c_result_indexs, c_last_insert_index + 1, 1)
                        insert_empty_index(r_result_indexs, c_last_insert_index + 1, 1)
                    c_result_indexs[c_insert_index] = i
                    c_last_index = i
                    c_last_insert_index = c_insert_index

        if not (len(l_result_indexs) == len(r_result_indexs) == len(c_result_indexs)):
            raise Exception("code match is wrong, please check function named '_compare_unstable_chunk' in compare.py")
        def addToTextCtrl(textCtrl, lines, index):
            if index != -1:
                lineData = lines[index]
                textCtrl.add_line_data(lineData)
                return lineData
            else:
                textCtrl.add_blank_line(1)
                return None
        # 添加到显示对象文本
        for i in range(0, len(l_result_indexs)):
            l_index = l_result_indexs[i]
            c_index = c_result_indexs[i]
            r_index = r_result_indexs[i]
            left_line_data = addToTextCtrl(self.text_l, left_lines, l_index)
            center_line_data = addToTextCtrl(self.text_c, center_lines, c_index)
            right_line_data = addToTextCtrl(self.text_r, right_lines, r_index)
            self.diff_line_by_char(left_line_data, center_line_data, right_line_data)
            # 合并代码计算
            chunk = UnStableChunk(left_line_data, center_line_data, right_line_data, self.text_l.get_last_line_data(), self.text_r.get_last_line_data())
            self.unstable_chunks.append(chunk)
            modify = self.merger.merge_line(chunk, self.cmp_option.merge_option)
            if modify:
                self.output_modifys.append(modify)
            if chunk.get_conflicted():
                if left_line_data:
                    self.text_l.mark_conflict_line(left_line_data.show_line_num)
                if center_line_data:
                    self.text_c.mark_conflict_line(center_line_data.show_line_num)
                if right_line_data:
                    self.text_r.mark_conflict_line(right_line_data.show_line_num)
            else:
                if left_line_data:
                    self.text_l.mark_auto_resolve_line(left_line_data.show_line_num)
                if center_line_data:
                    self.text_c.mark_auto_resolve_line(center_line_data.show_line_num)
                if right_line_data:
                    self.text_r.mark_auto_resolve_line(right_line_data.show_line_num)



    # 比较一块代码，计算出稳定块和非稳定块
    def _compare_chunk(self, leftLineDataArr, centerLineDataArr, rightLineDataArr):
        l_property_content_arr = get_content_from_line_data_arr(leftLineDataArr)
        c_property_content_arr = get_content_from_line_data_arr(centerLineDataArr)
        r_property_content_arr = get_content_from_line_data_arr(rightLineDataArr)

        def addLineDatasToTextCtrl(textCtrl, lineDatas):
            for i in range(0, len(lineDatas)):
                textCtrl.add_line_data(lineDatas[i])

        if is_line_arr_equality(leftLineDataArr, centerLineDataArr) and is_line_arr_equality(centerLineDataArr,
                                                                                             rightLineDataArr):
            addLineDatasToTextCtrl(self.text_l, leftLineDataArr)
            addLineDatasToTextCtrl(self.text_c, centerLineDataArr)
            addLineDatasToTextCtrl(self.text_r, rightLineDataArr)
            return

        diffs = diff_obj.diff_main(l_property_content_arr, c_property_content_arr)
        lcs_content_lc = diff_obj.get_lcs(diffs)
        # try:
        diffs = diff_obj.diff_main(lcs_content_lc, r_property_content_arr)
        # except:
        # print "error happened"
        lcs_content_arr = diff_obj.get_lcs(diffs)
        if len(lcs_content_arr) > 0:
            # 计算出公共行数索引
            l_lcs_index = []
            c_lcs_index = []
            r_lcs_index = []
            l_index = -1  # 开始搜索索引
            c_index = -1
            r_index = -1
            for i in range(0, len(lcs_content_arr)):
                has_unstable_chunk = False
                line = lcs_content_arr[i]
                left_diffs = []
                center_diffs = []
                right_diffs = []
                l_index = l_property_content_arr.index(line, l_index + 1)
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
                c_index = c_property_content_arr.index(line, c_index + 1)
                c_lcs_index.append(c_index)
                if i == 0:
                    if c_index > 0:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(0, c_index)
                else:
                    lines = c_lcs_index[i] - c_lcs_index[i - 1]
                    if lines > 1:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(c_lcs_index[i - 1] + 1, c_lcs_index[i])
                r_index = r_property_content_arr.index(line, r_index + 1)
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
                    self._deep_compare_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs,
                                                 center_diffs, right_diffs)
                self.text_l.add_line_data(leftLineDataArr[l_lcs_index[i]])
                self.text_c.add_line_data(centerLineDataArr[c_lcs_index[i]])
                self.text_r.add_line_data(rightLineDataArr[r_lcs_index[i]])
            # 检查公共字符串后面有没有非稳定块
            last_l_index = l_lcs_index[len(l_lcs_index) - 1]
            last_c_index = c_lcs_index[len(c_lcs_index) - 1]
            last_r_index = r_lcs_index[len(r_lcs_index) - 1]
            left_diffs = get_all_index_by_start_and_end(last_l_index + 1, len(leftLineDataArr))
            center_diffs = get_all_index_by_start_and_end(last_c_index + 1, len(centerLineDataArr))
            right_diffs = get_all_index_by_start_and_end(last_r_index + 1, len(rightLineDataArr))
            if len(left_diffs) > 0 or len(center_diffs) > 0 or len(right_diffs) > 0:
                self._deep_compare_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs,
                                             center_diffs,
                                             right_diffs)
        else:
            left_diffs = get_all_index_by_start_and_end(0, len(leftLineDataArr))
            center_diffs = get_all_index_by_start_and_end(0, len(centerLineDataArr))
            right_diffs = get_all_index_by_start_and_end(0, len(rightLineDataArr))
            self._deep_compare_chunk(leftLineDataArr, centerLineDataArr, rightLineDataArr, left_diffs, center_diffs,
                                         right_diffs)

    def _deep_compare_chunk(self, l_lines, c_lines, r_lines, left_indexs, center_indexs, right_indexs):
        if not self.cmp_option.deep_compare:
            self._compare_unstable_chunk(l_lines, c_lines, r_lines, left_indexs, center_indexs, right_indexs)
            return
        # 不稳定块,先从中提取出代码相似度高的稳定块
        left_lines = get_line_by_index(l_lines, left_indexs)
        center_lines = get_line_by_index(c_lines, center_indexs)
        right_lines = get_line_by_index(r_lines, right_indexs)
        l_added_lines = []
        r_added_lines = []
        c_added_lines = []
        l_start_index = 0
        r_start_index = 0
        result = []
        for i in range(0, len(center_lines)):  # 从中间开始遍历,找出匹配的代码行
            c_line = center_lines[i]
            has_match = False
            l_line_index = get_match_index_from_lines(c_line, left_lines, l_start_index)
            r_line_index = get_match_index_from_lines(c_line, right_lines, r_start_index)
            has_match = l_line_index != -1
            has_match = r_line_index != -1 and has_match
            if has_match:  # 必须至少有一个匹配，否则视为孤立行
                result.append((l_line_index, i, r_line_index))
                l_added_lines.append(l_line_index)
                l_start_index = l_line_index + 1
                r_added_lines.append(r_line_index)
                r_start_index = r_line_index + 1
                c_added_lines.append(i)
            if l_start_index >= len(left_lines) or r_start_index >= len(right_lines):
                break
        # 用匹配的代码行来进行稳定块代码和非稳定块代码计算
        if len(result) > 0:
            for i in range(0, len(result)):
                l_index, c_index, r_index = result[i]
                has_unstable_chunk = False
                left_diffs = []
                center_diffs = []
                right_diffs = []
                if i == 0:
                    if l_index > 0:
                        has_unstable_chunk = True
                        left_diffs = get_all_index_by_start_and_end(0, l_index)
                    if c_index > 0:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(0, c_index)
                    if r_index > 0:
                        has_unstable_chunk = True
                        right_diffs = get_all_index_by_start_and_end(0, r_index)
                else:
                    l_space_lines = result[i][0] - result[i - 1][0]
                    if l_space_lines > 1:
                        has_unstable_chunk = True
                        left_diffs = get_all_index_by_start_and_end(result[i - 1][0] + 1, result[i][0])
                    c_space_lines = result[i][1] - result[i - 1][1]
                    if c_space_lines > 1:
                        has_unstable_chunk = True
                        center_diffs = get_all_index_by_start_and_end(result[i - 1][1] + 1, result[i][1])
                    r_space_lines = result[i][2] - result[i - 1][2]
                    if r_space_lines > 1:
                        has_unstable_chunk = True
                        right_diffs = get_all_index_by_start_and_end(result[i - 1][2] + 1, result[i][2])
                if has_unstable_chunk:
                    self._compare_unstable_chunk(left_lines, center_lines, right_lines, left_diffs, center_diffs,
                                                      right_diffs)
                left_line_data = left_lines[l_index]
                center_line_data = center_lines[c_index]
                right_line_data = right_lines[r_index]
                self.text_l.add_line_data(left_line_data)
                self.text_c.add_line_data(center_line_data)
                self.text_r.add_line_data(right_line_data)
                self.diff_line_by_char(left_line_data, center_line_data, right_line_data)
                chunk = UnStableChunk(left_line_data, center_line_data, right_line_data)
                self.unstable_chunks.append(chunk)
                modify = self.merger.merge_independent_line(self.merger, chunk, self.merger.merge_option)
                if modify:
                    self.output_modifys.append(modify)
                if chunk.get_conflicted():
                    self.text_l.mark_conflict_line(left_line_data.show_line_num)
                    self.text_c.mark_conflict_line(center_line_data.show_line_num)
                    self.text_r.mark_conflict_line(right_line_data.show_line_num)
                else:
                    self.text_l.mark_auto_resolve_line(left_line_data.show_line_num)
                    self.text_c.mark_auto_resolve_line(center_line_data.show_line_num)
                    self.text_r.mark_auto_resolve_line(right_line_data.show_line_num)
            # 检查公共字符串后面有没有非稳定块
            last_l_index, last_c_index, last_r_index = result[len(result) - 1]
            left_diffs = get_all_index_by_start_and_end(last_l_index + 1, len(left_lines))
            center_diffs = get_all_index_by_start_and_end(last_c_index + 1, len(center_lines))
            right_diffs = get_all_index_by_start_and_end(last_r_index + 1, len(right_lines))
            if len(left_diffs) > 0 or len(center_diffs) > 0 or len(right_diffs) > 0:
                self._compare_unstable_chunk(left_lines, center_lines, right_lines, left_diffs, center_diffs,
                                                  right_diffs)
        else:
            self._compare_unstable_chunk(l_lines, c_lines, r_lines, left_indexs, center_indexs,
                                              right_indexs)


def is_line_arr_equality(arr1,arr2):
    if len(arr1) != len(arr2):
        return False
    for i in range(0, len(arr1)):
        line1 = arr1[i]
        line2 = arr2[i]
        if line1.get_no_blank_content() != line2.get_no_blank_content():
            return False
    return True

# 返回lineData中的内容
def get_content_from_line_data_arr(lineDataArr):
    arr = []
    for index in range(0, len(lineDataArr)):
        data = lineDataArr[index]
        arr.append(data.get_no_blank_content())
    return arr

def is_stable_line(l_line, c_line, r_line):
    return l_line.get_no_blank_content() == c_line.get_no_blank_content() == r_line.get_no_blank_content()

def get_match_line_from_lines(destLine,lines,startIndex=0):
    # 获取匹配度大于等于50的匹配的行
    dest_content = destLine.get_no_blank_content()
    for i in range(startIndex, len(lines)):
        line = lines[i]
        cur_score = get_code_match(line.get_no_blank_content(), dest_content)
        if cur_score >= CODE_MATCH_SCORE:
            return line
    return None

def get_same_line_from_lines(destLine,lines,startIndex=0):
    # 获取内容完全一样的
    dest_content = destLine.get_no_blank_content()
    for i in range(startIndex, len(lines)):
        line = lines[i]
        if dest_content == line.get_no_blank_content:
            return line
    return None


def get_match_index_from_lines(destLine, lines, startIndex):
    # 获取匹配度大于等于50的匹配的行的首个索引
    dest_content = destLine.get_no_blank_content()
    for i in range(startIndex, len(lines)):
        line = lines[i]
        cur_score = get_code_match(line.get_no_blank_content(), dest_content)
        if cur_score >= CODE_MATCH_SCORE:
            return i
    return -1


class UnStableChunk(object):
    @staticmethod
    def get_default_value():
        return UnStableChunk(None,None,None)

    def __init__(self, leftLineData, centerLineData, rightLineData, leftStableLine=None, rightStableLine=None):
        self.leftLineData = leftLineData# 有可能是数组
        self.centerLineData = centerLineData# 有可能是数组
        self.rightLineData = rightLineData# 有可能是数组
        self.leftStableLine = leftStableLine
        self.rightStableLine = rightStableLine
        self.is_confilcted = False

    def get_conflicted(self):
        return self.is_confilcted

class TextMerge(object):
    def __init__(self,mergeOption):
        self.merge_option = mergeOption
        pass
    @staticmethod
    def merge_independent_line(self, chunk=UnStableChunk.get_default_value(), mergeOption=None):
        '''
        单行对比合并，先进行字符级比较，区分出简单的合并，三方如果都有不同的时候，然后执行代码匹配比较，进一步分析合并
        :param self:
        :param chunk:
        :param mergeOption:
        :return:
        '''
        if not mergeOption:
            mergeOption = self.merge_option
        l_line = chunk.leftLineData
        c_line = chunk.centerLineData
        r_line = chunk.rightLineData
        if not l_line or not c_line or not r_line:
            raise Exception("all line must not be None")
        if is_stable_line(l_line, c_line, r_line):
            return None
        else:
            modify_line_index = l_line.index if mergeOption == CompareOption.MERGE_TO_LEFT else r_line.index
            l_content = l_line.get_no_blank_content()
            c_content = c_line.get_no_blank_content()
            r_content = r_line.get_no_blank_content()
            if l_content == c_content:
                return LineModify(modify_line_index, LineModify.MODIFY_TYPE, r_line)
            elif c_content == r_content:
                return LineModify(modify_line_index, LineModify.MODIFY_TYPE, l_line)
            elif l_content == r_content:
                return LineModify(modify_line_index, LineModify.NONE_TYPE, None)
            else:
                chunk.is_confilcted = True
                return LineModify(modify_line_index, LineModify.CONFLICT_TYPE, None, chunk)

    def merge_line(self, chunk=UnStableChunk.get_default_value(), mergeOption=None):
        if not mergeOption:
            mergeOption = self.merge_option
        l_line = chunk.leftLineData
        c_line = chunk.centerLineData
        r_line = chunk.rightLineData
        if l_line and c_line and r_line:
            return self.merge_independent_line(self, chunk, mergeOption)
        else:
            if mergeOption == CompareOption.MERGE_TO_LEFT:
                if l_line and c_line:
                    if l_line.get_no_blank_content() == c_line.get_no_blank_content():
                        return LineModify(l_line.index, LineModify.DELETE_TYPE)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(l_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif l_line and r_line:
                    if l_line.get_no_blank_content() == r_line.get_no_blank_content():
                        return LineModify(l_line.index, LineModify.NONE_TYPE, None, chunk)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(l_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif c_line and r_line:
                    if l_line.get_no_blank_content() == r_line.get_no_blank_content():
                        return None
                    else:
                        chunk.is_confilcted = True
                        return LineModify(chunk.leftStableLine.index, LineModify.EMPTY_CONFLICT_TYPE, r_line, chunk)
                elif not l_line and not c_line:
                    return LineModify(chunk.leftStableLine.index, LineModify.ADD_TYPE, r_line)
                elif not l_line and not r_line:
                    return None
                elif not c_line and not r_line:
                    return LineModify(l_line.index, LineModify.NONE_TYPE, r_line)
            elif mergeOption == CompareOption.MERGE_TO_RIGHT:
                if l_line and c_line:
                    if l_line.get_no_blank_content() == c_line.get_no_blank_content():
                        return None
                    else:
                        chunk.is_confilcted = True
                        return LineModify(chunk.rightStableLine.index, LineModify.EMPTY_CONFLICT_TYPE, l_line, chunk)
                elif l_line and r_line:
                    if l_line.get_no_blank_content() == r_line.get_no_blank_content():
                        return LineModify(r_line.index, LineModify.NONE_TYPE, None, chunk)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(r_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif c_line and r_line:
                    if c_line.get_no_blank_content() == r_line.get_no_blank_content():
                        return LineModify(r_line.index, LineModify.DELETE_TYPE)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(r_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif not l_line and not c_line:
                    return LineModify(r_line.index, LineModify.NONE_TYPE, None, chunk)
                elif not l_line and not r_line:
                    return None
                elif not c_line and not r_line:
                    return LineModify(chunk.rightStableLine.index, LineModify.ADD_TYPE, l_line)
            raise Exception("no modify")





class ASCodeMerge(TextMerge):
    def __init__(self,l_cls, c_cls, r_cls, mergeOption):
        self.l_cls = l_cls
        self.c_cls = c_cls
        self.r_cls = r_cls
        self.merge_option = mergeOption

    @staticmethod
    def merge_independent_line(self=None, chunk=UnStableChunk.get_default_value(), mergeOption=None):
        '''
        单行对比合并，先进行字符级比较，区分出简单的合并，三方如果都有不同的时候，然后执行代码匹配比较，进一步分析合并
        :param self:
        :param chunk:
        :param mergeOption:
        :return:
        '''
        if not mergeOption:
            mergeOption = self.merge_option
        l_line = chunk.leftLineData
        c_line = chunk.centerLineData
        r_line = chunk.rightLineData
        if not l_line or not c_line or not r_line:
            raise Exception("all line must not be None")
        if is_stable_line(l_line, c_line, r_line):
            return None
        else:
            modify_line_index = l_line.index if mergeOption == CompareOption.MERGE_TO_LEFT else r_line.index
            l_content = l_line.get_no_blank_content()
            c_content = c_line.get_no_blank_content()
            r_content = r_line.get_no_blank_content()
            if l_content == c_content:
                return LineModify(modify_line_index, LineModify.MODIFY_TYPE, r_line)
            elif c_content == r_content:
                return LineModify(modify_line_index, LineModify.MODIFY_TYPE, l_line)
            elif l_content == r_content:
                return LineModify(modify_line_index, LineModify.NONE_TYPE,None)
            else:
                # 执行代码匹配分析
                l_c_match_score = get_code_match(l_content,c_content)
                c_r_match_score = get_code_match(c_content,r_content)
                if l_c_match_score >= CODE_MATCH_SCORE:
                    if c_r_match_score >= CODE_MATCH_SCORE:
                        if is_child(l_content,r_content):
                            return LineModify(modify_line_index, LineModify.MODIFY_TYPE, r_line)
                        elif is_child(r_content,l_content):
                            return LineModify(modify_line_index, LineModify.MODIFY_TYPE, l_line)
                        else:
                            return LineModify(modify_line_index, LineModify.NONE_TYPE, None)
                    else:
                        return LineModify(modify_line_index, LineModify.MODIFY_TYPE, r_line)
                else:
                    if c_r_match_score >= CODE_MATCH_SCORE:
                        return LineModify(modify_line_index, LineModify.MODIFY_TYPE, l_line)
                    else:
                        result_line = l_line if mergeOption == CompareOption.MERGE_TO_LEFT else r_line
                        chunk.is_confilcted = True
                        return LineModify(modify_line_index, LineModify.CONFLICT_TYPE, result_line)

    def merge_disorder_line(self, chunk=UnStableChunk.get_default_value()):
        l_line = c_line = r_line = None
        if chunk.leftLineData:
            l_line = chunk.leftLineData
        if chunk.centerLineData:
            c_line = chunk.centerLineData
        if chunk.rightLineData:
            r_line = chunk.rightLineData
        if self.merge_option == CompareOption.MERGE_TO_LEFT:
            if l_line and c_line:
                return LineModify(l_line.index, LineModify.DELETE_TYPE)
            if not l_line and not c_line:
                return LineModify(chunk.leftStableLine.index, LineModify.ADD_TYPE, r_line)
        elif self.merge_option == CompareOption.MERGE_TO_RIGHT:
            if r_line and c_line:
                return LineModify(r_line.index, LineModify.DELETE_TYPE)
            if not r_line and not c_line:
                return LineModify(chunk.rightStableLine.index, LineModify.ADD_TYPE, l_line)
        return None

    def merge_line(self, chunk=UnStableChunk.get_default_value(), mergeOption=None):
        if not mergeOption:
            mergeOption = self.merge_option
        l_line = chunk.leftLineData
        c_line = chunk.centerLineData
        r_line = chunk.rightLineData
        if l_line and c_line and r_line:
            return self.merge_independent_line(self, chunk, mergeOption)
        else:
            if mergeOption == CompareOption.MERGE_TO_LEFT:
                if l_line and c_line:
                    score = get_code_match(l_line.get_no_blank_content(), c_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return LineModify(l_line.index, LineModify.DELETE_TYPE)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(l_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif l_line and r_line:
                    score = get_code_match(l_line.get_no_blank_content(), r_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return LineModify(l_line.index, LineModify.NONE_TYPE, None, chunk)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(l_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif c_line and r_line:
                    score = get_code_match(c_line.get_no_blank_content(), r_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return None
                    else:
                        chunk.is_confilcted = True
                        return LineModify(chunk.leftStableLine.index, LineModify.EMPTY_CONFLICT_TYPE, r_line, chunk)
                elif not l_line and not c_line:
                    return LineModify(chunk.leftStableLine.index, LineModify.ADD_TYPE, r_line)
                elif not l_line and not r_line:
                    return None
                elif not c_line and not r_line:
                    return LineModify(l_line.index, LineModify.NONE_TYPE, None, chunk)
            elif mergeOption == CompareOption.MERGE_TO_RIGHT:
                if l_line and c_line:
                    score = get_code_match(l_line.get_no_blank_content(), c_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return None
                    else:
                        chunk.is_confilcted = True
                        return LineModify(chunk.rightStableLine.index, LineModify.EMPTY_CONFLICT_TYPE, l_line, chunk)
                elif l_line and r_line:
                    score = get_code_match(l_line.get_no_blank_content(), r_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return LineModify(r_line.index, LineModify.NONE_TYPE, None, chunk)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(r_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif c_line and r_line:
                    score = get_code_match(c_line.get_no_blank_content(), r_line.get_no_blank_content())
                    if score >= CODE_MATCH_SCORE:
                        return LineModify(r_line.index, LineModify.DELETE_TYPE)
                    else:
                        chunk.is_confilcted = True
                        return LineModify(r_line.index, LineModify.CONFLICT_TYPE, None, chunk)
                elif not l_line and not c_line:
                    return LineModify(r_line.index, LineModify.NONE_TYPE, None, chunk)
                elif not l_line and not r_line:
                    return None
                elif not c_line and not r_line:
                    return LineModify(chunk.rightStableLine.index, LineModify.ADD_TYPE, l_line)
            raise Exception("no modify")



import time
if __name__ == "__main__":
    codeText1 = CodeTextCtrl(render=False)
    codeText2 = CodeTextCtrl(render=False)
    codeText3 = CodeTextCtrl(render=False)
    codeText4 = CodeTextCtrl(render=False)
    l_file = r"D:/workspace/Poland/pl_client_proj/branches/PL_NarutoAlpha3.39/src/naruto.include/src/cfgData/ConfigClassAlias.as"
    c_file = r"D:/workspace/German/de_client_proj/branches/DE_NarutoAlpha3.17/src/naruto.include/src/cfgData/ConfigClassAlias.as"
    r_file = r"D:/workspace/German/de_client_proj/branches/DE_NarutoAlpha5.50/src/naruto.include/src/cfgData/ConfigClassAlias.as"
    # compare = ThreeSideAsCompare(codeText1, codeText2, codeText3, l_file, c_file, r_file, codeText4, mergeOption=CompareOption.GetDefaultValue())
    l_as_file = AsFile(l_file)
    c_as_file = AsFile(c_file)
    start_time = time.time()
    # com = find_lcseque(l_as_file.get_render_text(), c_as_file.get_render_text())
    diff_obj.diff_main(l_as_file.get_render_text(), c_as_file.get_render_text())
    com = diff_obj.get_lcs()
    print time.time() - start_time
    print com
    print "over"






