#coding:utf-8

from const import *
from pathutils import *

class FilterData(object):
    @staticmethod
    def get_default_value():
        return FilterData(None)

    def __init__(self,filterString):
        '''
        :param includePost: 分号分割的字符串
        :param excludePost: 分号分割的字符串
        '''
        self.filterString = filterString#包含
        self.init_data()

    def init_data(self):
        self.include_arr = []
        self.exclude_arr = []
        if self.filterString:
            arr = self.filterString.split(";")
            for it in arr:
                if it.startswith("-"):
                    self.exclude_arr.append(it[1:])
                else:
                    self.include_arr.append(it)

    def equare(self, inFilter):
        if inFilter:
            return self.filterString == inFilter.filterString
        return True

    def include(self,fileName):
        index = fileName.find(".")
        if index != -1:
            return fileName[index:] in self.include_arr
        return False

    def exclude(self,fileName):
        index = fileName.find(".")
        if index != -1:
            return fileName[index:] not in self.exclude_arr
        return True

    def enable(self):
        if self.filterString:
            return True
        else:
            return False

class CompareFilter(object):
    ALL = "All"
    MERGEABLE="MergeAble"
    CONFLICT= "Conflict"
    SAME = "Same"
    NONE = "None"

class CompareOption:
    MERGE_TO_LEFT = 1
    MERGE_TO_RIGHT = 2
    def __init__(self,textFormat = FileFormat.AS, ignoreBlank=True,ignoreComment=True,deepCompare=False,mergeOption=MERGE_TO_LEFT,filter=None):
        self.merge_option = mergeOption
        self.ignore_blank = ignoreBlank
        self.ignore_comment = ignoreComment
        self.deep_compare = deepCompare
        self.file_format = textFormat
        self.filter = filter
    @staticmethod
    def GetDefaultValue():
        return CompareOption(filter=FilterData(".as"))
    @staticmethod
    def GetFileFormatByUrl(file):
        suffix = get_suffix_by_url(file)
        if suffix == ".as":
            return FileFormat.AS
        elif suffix == ".prefab":
            return FileFormat.PREFAB
        else:
            return FileFormat.NormalText


class PageData(object):
    def __init__(self,left_path = None, center_path = None, right_path  = None, cmpOption = CompareOption.GetDefaultValue()):
        self.leftPath = left_path
        self.centerPath = center_path
        self.rightPath = right_path
        self.cmp_option = cmpOption
    def get_output_path(self):
        output_path = self.leftPath
        if self.cmp_option == CompareOption.MERGE_TO_RIGHT:
            output_path = self.rightPath
        return output_path

    def get_label(self):
        left = self.leftPath[self.leftPath.rfind("/")+1:]
        right = self.rightPath[self.rightPath.rfind("/")+1:]
        if left == right:
            return left
        else:
            return left + " <--> " + right

    def set_cmp_option(self, option):
        self.cmp_option = option

class LineData:
    @staticmethod
    def GetlineData(text):
        return LineData(-1, 0, 1, str(text)+"\n")

    def __init__(self,lineIndex, startIndex=0,endIndex=-1,content=""):
        # 行索引(从0开始)
        self.index = lineIndex
        self.start_index = startIndex
        self.end_index = endIndex
        self.content = content
        # 该行在比较时所在的行索引，从0开始
        self.show_line_num = -1
        # 比较时增加的后缀，一般没有，只有在包定义行或类定义行和“{”分成了两行，才需要增加
        self.show_suffix = None
        # 该行在比较时后面是否增加了空行
        self.add_empty_line_num = 0
    def get_show_content(self):
        '''获取展示的字符，一般会包含前面的tab符号'''
        if self.content:
            return self.content[self.start_index:self.end_index]
        return ""
    def get_no_blank_content(self):
        '''
        获取非空字符
        :return:
        '''
        if self.content:
            return self.content[self.start_index:self.end_index].strip().strip("\t")
        return ""
    def clone(self):
            return LineData(self.index, self.start_index, self.end_index, self.content)

class LineModify(object):
    '''
    三方合并的修改
    '''
    DELETE_TYPE = 1
    MODIFY_TYPE = 2
    ADD_TYPE = 3
    NONE_TYPE = 4# 比对之后不做任何操作，保持原样
    CONFLICT_TYPE = 5 #冲突
    EMPTY_CONFLICT_TYPE = 6#空行冲突（为了更好显示效果，和普通文本冲突，加上特别效果）
    def __init__(self, lineIndex, type, lineDatas=None,chunk=None):
        self.lineIndex = lineIndex
        self.type = type
        self.lineDatas = lineDatas


class File:
    def __init__(self, fileUrl, ignoreBlankLine = True):
        self.url = fileUrl.replace("\\", "/").decode("utf-8")
        self.ignore_blank_line = ignoreBlankLine
        self.lines = self._readFile()

    def _readFile(self):
        lines = None
        if self.url.startswith("http"):
            parent, name = split_path_name_and_parent(self.url)
            r_client = remote.RemoteClient(parent)
            self.content = r_client.cat(name)
            lines = self.content.split("\n")
        else:
            with open(self.url, "r") as file:
                lines = file.readlines()
                self.content = file.read()
        lines[0] = lines[0].replace('\xef\xbb\xbf', '')
        return lines

    def get_line_datas(self):
        line_datas = []
        for index in range(0, len(self.lines)):
            line = self.lines[index].strip("\n")  # 去除末尾的换行符
            if self.ignore_blank_line and line.strip("\t").strip() == "":
                continue
            cur_line_data = LineData(index, 0, len(line), line)
            line_datas.append(cur_line_data)
        return line_datas

    def get_render_text(self):
        result_str = ""
        for index in range(0, len(self.lines)):
            result_str += self.lines[index]
        return result_str
    def destory(self):
        self.content = None
        self.lines = None

class XmlFile(File):
    def __init__(self, fileUrl):
        File.__init__(self,fileUrl)

class ClsData:
    def __init__(self, fileUrl, clsName = None):
        self.url = fileUrl
        self.cls_name = clsName
        self.class_line_data = None
        self.property_arr = []
        self.function_dic = {}
        self.import_arr = []
        self.is_interface = False # 是否为接口

    def get_all_line_datas(self):
        new_lines = []
        import_arr = self.import_arr
        for index in range(0, len(import_arr)):
            data = import_arr[index]
            new_lines.append(data)
        class_line = self.class_line_data.get_show_content()
        new_lines.append(self.class_line_data)
        if not class_line.endswith("{"):
            new_lines.append(LineData(-1,0,1,"{"))
        property_arr = self.property_arr
        for index in range(0, len(property_arr)):
            data = property_arr[index]
            new_lines.append(data)
        for function_name in self.function_dic:
            function_arr = self.function_dic[function_name]
            for index in range(0, len(function_arr)):
                data = function_arr[index]
                new_lines.append(data)
        new_lines.append(LineData(-1, 0, 1, "}"))
        return new_lines



'''
AS文件对象，主要负责解析AS文件，并将其整理好为对比做准备
'''
class AsFile(File):
    def __init__(self, fileUrl,ignoreBlankLine=True,ignoreComment=True):
        File.__init__(self,fileUrl,ignoreBlankLine)
        self.ignore_comment = ignoreComment
        self.lines = self._readFile()
        self.name = self.url[self.url.rfind("/"):-3]
        self.inner_cls= ClsData(self.url)
        self.outer_cls_dic = {}
        self.package_line = LineData(0)
        self.other_lines = []
        self._private_exceute()

    def get_class_render_arr(self,cls=ClsData("")):
        new_lines = []
        if cls == None:
            return []
        import_arr = cls.import_arr
        for index in range(0, len(import_arr)):
            data = import_arr[index]
            new_lines.append(data.get_show_content())
        class_line = cls.class_line_data.get_show_content()
        if not class_line.endswith("{"):
            class_line = class_line + "{"
        new_lines.append(class_line)
        property_arr = cls.property_arr
        for index in range(0, len(property_arr)):
            data = property_arr[index]
            new_lines.append(data.get_show_content())
        for function_name in cls.function_dic:
            function_arr = cls.function_dic[function_name]
            for index in range(0,len(function_arr)):
                data = function_arr[index]
                function_line = data.get_show_content()
                new_lines.append(function_line)
        new_lines.append("\t}")
        return new_lines

    def get_render_text(self):
        new_lines = []
        lines = self.lines
        package_line = self.package_line.get_show_content()
        self.package_line.show_line_num = 0
        if not package_line.endswith("{"):
            package_line = package_line + "{"
        new_lines.append(package_line)
        inner_cls = self.inner_cls
        if inner_cls == None:
            raise Exception("can not find inner cls",1)
        cls_arr = self.get_class_render_arr(self.inner_cls)
        new_lines.extend(cls_arr)
        new_lines.append("}")
        for key in self.outer_cls_dic:
            cls = self.outer_cls_dic[key]
            cls_arr = self.get_class_render_arr(cls)
            new_lines.extend(cls_arr)
        result_str = ""
        for otherLine in self.other_lines:
            new_lines.append(otherLine.get_show_content())
        for index in range(0,len(new_lines)):
            result_str = result_str + new_lines[index]+"\n"
        return result_str

    def _add_to_arr(self,arr,data):
        if not data in arr:
            arr.append(data)

    def _check_blank_line(self):
        if not self.ignore_blank_line:
            return
        def ignore_blank_line(arr,isIgnoreComment):
            new_arr = []
            for index in range(0, len(arr)):
                data = arr[index]
                if self.ignore_comment:
                    if not data.get_show_content().strip().strip("\t") == "":
                        new_arr.append(data)
                else:
                    if not data.content.strip().strip("\t") == "":
                        new_arr.append(data)
            return new_arr
        def check_cls_blank_line(cls):
            empty_line = 0
            import_arr = cls.import_arr
            new_import_arr = ignore_blank_line(import_arr,self.ignore_comment)
            empty_line += len(cls.import_arr) - len(new_import_arr)
            cls.import_arr = new_import_arr
            new_property_arr = ignore_blank_line(cls.property_arr,self.ignore_comment)
            empty_line += len(cls.property_arr) - len(new_property_arr)
            cls.property_arr = new_property_arr
            for function_name in cls.function_dic:
                function_arr = cls.function_dic[function_name]
                new_function_arr = ignore_blank_line(function_arr,self.ignore_comment)
                empty_line += len(function_arr) - len(new_function_arr)
                cls.function_dic[function_name] = new_function_arr
            return empty_line
        ignorelines = check_cls_blank_line(self.inner_cls)
        for key in self.outer_cls_dic:
            cls = self.outer_cls_dic[key]
            value = check_cls_blank_line(cls)
            ignorelines += value
        return ignorelines

    def _private_exceute(self):
        lines = self.lines
        cur_function_arr = None  # 当前正在遍历的方法
        function_has_get_or_set = ""
        state = ScanState.CODE_STATE
        cur_cls = ClsData(self.url) #当前正在遍历的类
        comment_flag = ""
        inner_package = False # 是否包内
        inner_class = False # 在类模块
        inner_function = False # 在函数模块
        function_level = -1 # function 所处的嵌套层级
        class_level = -1
        package_level = -1
        level = 0
        cache_cmd_lock = False
        cache_cmd = "" # 当前正在进行的模块
        cur_cmd = ""# 当前扫描的单词
        readed_cmd = "" #扫描到一个完整的词语
        last_read_cmd = ""
        update_cmd = False
        for index in range(0, len(lines)):
            line = lines[index].strip("\n")#去除末尾的换行符
            if self.ignore_blank_line and line.strip("\t").strip() == "":
                continue
            # cur_cmd = ""# 当前扫描的单词
            # readed_cmd = "" #上次扫描的单词
            # update_cmd = False
            cur_line_data = LineData(index, 0, 0, line)
            cur_line_data.end_index = len(line)
            str_flag = ""
            update_cmd = True# 换行要更新当前关键字
            if cache_cmd_lock == False:
                cache_cmd = ""
                cur_cmd = ""  # 当前扫描的单词
                last_read_cmd = readed_cmd
                readed_cmd = ""  # 上次扫描的单词

            if (state == ScanState.STRING_STATE) or (state == ScanState.COMMENT_STATE and comment_flag == AsKeyWord.SINGLE_COMMENT_FLAG):# 换行字符阅读状态清零
                state = ScanState.CODE_STATE
            for charIndex in range(0, len(line)):
                char = line[charIndex]
                code = ord(char)
                if update_cmd:
                    last_read_cmd = readed_cmd
                    readed_cmd = cur_cmd
                    cur_cmd = ""
                    update_cmd = False
                if (code != 32 and code != 9 and char != "{" and char != "}" and char != "(" and char != ")" and char != ";"):
                    cur_cmd = cur_cmd + char
                    update_cmd = False
                elif cur_cmd != "":#
                    update_cmd = True #标志更新清空重新读取
                    last_read_cmd = readed_cmd
                    readed_cmd = cur_cmd
                    if not inner_function and cur_cmd in AsKeyWord.CODE_CMD_ARR: # 在function中也会有var 等关键字，故需要判断是否在function 中遍历
                        cache_cmd = cur_cmd
                # 注释阅读模式
                if state == ScanState.COMMENT_STATE:
                    if comment_flag == "":
                        raise Exception("scan comment state but found comment_flag is empty",1)
                    if comment_flag == AsKeyWord.MUTI_COMMENT_FLAG_START:# 多行注释，扫描注释结束符号
                        if cur_cmd.endswith(AsKeyWord.MUTI_COMMENT_FLAG_OVER):
                            state = ScanState.CODE_STATE
                            cur_line_data.start_index = charIndex + 1
                            comment_flag = ""
                            cur_cmd = ""
                        else:
                            pass
                    elif comment_flag == AsKeyWord.SINGLE_COMMENT_FLAG: # 单行注释，直接跳转下一行
                        state = ScanState.CODE_STATE
                        break
                # 字符阅读模式
                elif state == ScanState.STRING_STATE:
                    if self.ignore_comment:
                        cur_line_data.end_index = charIndex + 1
                    if str_flag == "":
                        raise Exception("scan string state but found str_flag is empty",1)
                    if str_flag == char:# 发现了字符串的结束符号
                        str_flag = ""
                        state = ScanState.CODE_STATE
                        cur_cmd = ""
                    pass
                # 代码阅读模式
                elif state == ScanState.CODE_STATE:
                    if self.ignore_comment:
                        cur_line_data.end_index = charIndex + 1
                    if cur_cmd.endswith(AsKeyWord.MUTI_COMMENT_FLAG_START) or cur_cmd.endswith(AsKeyWord.SINGLE_COMMENT_FLAG):
                        state = ScanState.COMMENT_STATE
                        comment_flag = AsKeyWord.MUTI_COMMENT_FLAG_START if cur_cmd.endswith(AsKeyWord.MUTI_COMMENT_FLAG_START) else AsKeyWord.SINGLE_COMMENT_FLAG
                        cur_cmd = ""
                        if self.ignore_comment:
                            cur_line_data.end_index = charIndex - 1
                    elif char == AsKeyWord.STRING_FLAG1 or char == AsKeyWord.STRING_FLAG2:
                        state = ScanState.STRING_STATE
                        str_flag = char
                        cur_cmd = ""
                    elif cache_cmd == AsKeyWord.CODE_PACKAGE:
                        #发现包声明
                        if cache_cmd_lock == False:
                            self.package_line = cur_line_data
                        cache_cmd_lock = True
                        if char == "{":
                            cache_cmd_lock = False
                            cache_cmd = ""
                            inner_package = True
                            package_level = level
                            self.inner_cls = ClsData(self.url)
                            cur_cls = self.inner_cls
                    elif cache_cmd == AsKeyWord.CODE_IMPORT:
                        self._add_to_arr(cur_cls.import_arr,cur_line_data)
                    elif cache_cmd == AsKeyWord.CODE_CLASS or cache_cmd == AsKeyWord.CODE_INTERFACE:
                        if cache_cmd_lock == False:
                            cur_cls.class_line_data = cur_line_data
                            if cache_cmd == AsKeyWord.CODE_INTERFACE:
                                cur_cls.is_interface = True
                        cache_cmd_lock = True
                        if inner_class == False:
                            if cur_cls.cls_name == None and (readed_cmd == AsKeyWord.CODE_EXTENDS or readed_cmd == AsKeyWord.CODE_IMPLEMENTS):
                                cur_cls.cls_name = last_read_cmd
                            if char == "{":
                                if cur_cls.cls_name == None:
                                    cur_cls.cls_name = readed_cmd
                                cache_cmd_lock = False
                                cache_cmd = ""
                                inner_class = True
                                class_level = level
                            if inner_class and (inner_package == False):
                                if self.outer_cls_dic.has_key(cur_cls.cls_name):
                                    raise Exception("find the same name class:"+cur_cls.cls_name,1)
                                self.outer_cls_dic[cur_cls.cls_name] = cur_cls
                    elif inner_class and (cache_cmd == AsKeyWord.CODE_CONST or cache_cmd == AsKeyWord.CODE_VAR):
                        self._add_to_arr(cur_cls.property_arr, cur_line_data)
                    elif inner_class and cache_cmd == AsKeyWord.CODE_FUNCTION:
                        if cur_function_arr == None:
                            cur_function_arr = []
                            function_has_get_or_set = ""
                            function_package = ""
                            if last_read_cmd != "" and last_read_cmd not in AsKeyWord.FUNCTION_PACKAGE:
                                function_package = line.strip()[0:line.strip().find(AsKeyWord.CODE_FUNCTION)]
                        self._add_to_arr(cur_function_arr, cur_line_data)
                        cache_cmd_lock = True
                        if function_has_get_or_set == "" and(readed_cmd == AsKeyWord.CODE_GET or readed_cmd == AsKeyWord.CODE_SET):
                            function_has_get_or_set = readed_cmd
                        if inner_function == False:
                            if char == "(":
                                if function_has_get_or_set == "":
                                    name = readed_cmd
                                else:
                                    name = function_has_get_or_set +"/"+ readed_cmd
                                if function_package != "":
                                    name = function_package + "/" + name
                                if cur_cls.function_dic.has_key(name):
                                    raise Exception("find same name function:"+name,1)
                                cur_cls.function_dic[name] = cur_function_arr
                                if cur_cls.is_interface:
                                    cache_cmd_lock = False
                                    cache_cmd = ""
                                    cur_function_arr = None
                            elif char == "{":
                                inner_function = True
                                function_level = level
                    else:
                        pass
                    if char == "}":
                        level = level - 1
                        if level == package_level:
                            inner_package = False
                            package_level = -1
                        if level == class_level:
                            inner_class = False
                            cur_cls = ClsData(self.url)  # 初始化cur_cls为下一个类做准备
                            class_level = -1
                        if level == function_level:
                            # function结构体结束了
                            cache_cmd_lock = False
                            cache_cmd = ""
                            cur_function_arr = None
                            inner_function = False
                            function_level = -1
                    elif char == "{":
                        level = level + 1
                        # print "char:"+char
                        pass
        self._check_blank_line()

    def destory(self):
        self.content = ""
        self.lines = None
        self.inner_cls = None
        self.outer_cls_dic = None

class PrefabElement(object):
    def __init__(self,type,fileId,url=None,guidId = None):
        self.type = type
        self.fileId = fileId
        self.url = url
        self.guidId = guidId
        self.line_datas = []

    def get_base_property_value(self,name):
        lines = self.line_datas
        for i in range(0, len(lines)):
            line = lines[i]
            match_obj = PrefabKeyWord.ELEMENT_VALUE_REG.match(line)
            if match_obj:
                spaceNum = len(match_obj.group(1))
                lineName = match_obj.group(2)
                if lineName == name:
                    value = match_obj.group(3)
                    return value
        return None


class PrefabFile(File):
    def __init__(self,fileUrl, ignoreBlankLine = False):
        File.__init__(self, fileUrl, ignoreBlankLine)
        self.element_dic = {}
        self.root = None
        self.praseFile()

    def destory(self):
        File.destory(self)
        del self.element_dic
        del self.root

    def praseFile(self):
        lines = self.lines
        line = lines[0].strip("\n").rstrip()
        self.yaml_version_line = LineData(0, 0, len(line), line)
        line = lines[1].strip("\n").rstrip()
        self.unity_tag_line = LineData(1, 0, len(line), line)
        curElement = None
        for index in range(2, len(lines)):
            line = lines[index].strip("\n").rstrip()
            curLineData = LineData(index, 0, len(line), line)
            if line[:3] == "---":
                match_obj = PrefabKeyWord.ELEMENT_LINE_REG.match(line)
                if match_obj:
                    type = match_obj.group(1)
                    fileId = match_obj.group(2)
                    if type == 1001:
                        if self.root:
                            raise Exception("found more root prefab:"+self.url)
                        self.root = curElement
                    curElement = PrefabElement(type, fileId, self.url)
                    curElement.line_datas.append(curLineData)
                    self.element_dic[fileId] = curElement
                else:
                    curElement.line_datas.append(curLineData)
            else:
                curElement.line_datas.append(curLineData)

    def get_line_datas(self):
        line_arr = []
        for key in self.element_dic:
            e = self.element_dic[key]
            line_arr.extend(e.line_datas)
        return line_arr


import time

if __name__=="__main__":
    as_file = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window\UILobbyTask2.prefab"
    start_time = time.time()
    file = PrefabFile(as_file)
    print "time:"+str(time.time() - start_time)
    print len(file.get_line_datas())