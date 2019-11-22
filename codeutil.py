#coding:utf-8
import math
from const import ScanState, AsKeyWord
from data import LineData,ClsData,File
import re

CODE_SPLIT_CHARS = [".",",","(",")","{","}","+","&","|","=",":",";"," ","!","[","]","<",">"]#AS代码分割符号
CODE_MATCH_SCORE = 50
get_as_property_name = re.compile(ur".*[(var)|(const)]\s+(\w+)([:;=]).*")

class CodeError(object):
    NONE_ERROR = 0
    MISS_CHAR = 1
    SAME_PROPERTY = 2
    SAME_FUNCTION = 3
    SAME_CLASS = 4
    msg_dic = {NONE_ERROR:"It is all right, No error checked.",MISS_CHAR:"Maybe miss '{' or '}',check please!", SAME_PROPERTY:"Found same property name,check please!",
               SAME_FUNCTION:"Found same function name,check please!", SAME_CLASS:"Found same class name, check please!"}

    @staticmethod
    def get_state_msg(state):
        msg = CodeError.msg_dic[state]
        return msg

def is_child(parent,child):
    '''
    是否为父子代码（子代码元素包含并且多父代码元素）
    :param parent:父代码
    :param child:子代码
    :return: Boolean
    '''
    parent_arr = split_as_code(parent)
    child_arr = split_as_code(child)
    if len(child_arr) <= len(parent_arr):
        return False
    for i in range(0,len(parent_arr)):
        word = parent_arr[i]
        if word not in child_arr:
            return False
    return True


def split_as_code(codeStr):
    word = ""
    word_arr = []
    for i in range(0, len(codeStr)):
        char = codeStr[i]
        if char not in CODE_SPLIT_CHARS:
            word += char
        else:
            if len(word) > 0:
                word_arr.append(word)
                word = ""
    if len(word) > 0:
        word_arr.append(word)
    return word_arr

# 将多个数组拼成一个数组，并去掉重复的元素
def get_all_element_by_arr(*params):
    arr = []
    for i in range(0, len(params)):
        arr_parm = params[i]
        for j in range(0, len(arr_parm)):
            element = arr_parm[j]
            if element not in arr:
                arr.append(element)
    return arr

def cal_cos(text1,text2):
    word_arr1 = split_as_code(text1)
    word_arr2 = split_as_code(text2)
    word_all = get_all_element_by_arr(word_arr1, word_arr2)
    num_arr1 = []
    num_arr2 = []
    for i in range(0, len(word_all)):
        word = word_all[i]
        value1 = word_arr1.count(word)
        num_arr1.append(value1)
        value2 = word_arr2.count(word)
        num_arr2.append(value2)
    # 计算余弦相似度
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(num_arr1)):
        sum += num_arr1[i] * num_arr2[i]
        sq1 += pow(num_arr1[i], 2)
        sq2 += pow(num_arr2[i], 2)
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 4) * 100
    except ZeroDivisionError:
        result = 0.0
    return result

def get_code_match(text1, text2,codeSwitch=True):
    if text1 == text2:
        return 100.0
    index1 = text1.find("=")
    index2 = text2.find("=")
    if codeSwitch and index1 != -1 and index2 != -1:# 如有代码中赋值 ，则进行左右分开计算相似度，左右50%权重
        prefix1 = text1[:index1]
        prefix2 = text2[:index2]
        suffix1 = text1[index1+1:]
        suffix2 = text2[index2+1:]
        if prefix1 == prefix2:
            left_score = 100.0
        else:
            left_score = cal_cos(prefix1,prefix2)
        if suffix1 == suffix2:
            right_score = 100.0
        else:
            right_score = cal_cos(suffix1,suffix2)
        score = left_score*0.5 + right_score*0.5
        return score
    else:
        return cal_cos(text1,text2)

def check_as_file_error(textCtrl):
    cls_dic = {}
    cur_function_arr = None  # 当前正在遍历的方法
    function_has_get_or_set = ""
    state = ScanState.CODE_STATE
    cur_cls = ClsData("null")  # 当前正在遍历的类
    comment_flag = ""
    inner_package = False  # 是否包内
    inner_class = False  # 在类模块
    inner_function = False  # 在函数模块
    function_level = -1  # function 所处的嵌套层级
    class_level = -1
    package_level = -1
    level = 0
    cache_cmd_lock = False
    cache_cmd = ""  # 当前正在进行的模块
    last_cmd = ""  # 上次扫描到的词
    for index in range(0, textCtrl.text.GetLineCount()):
        line =  textCtrl.text.GetLineText(index) # 去除末尾的换行符
        cur_cmd = ""  # 当前扫描的单词
        last_cmd = ""  # 上次扫描的单词
        update_cmd = False
        cur_line_data = LineData(index, 0, 0, line)
        cur_line_data.end_index = len(line)
        str_flag = ""
        if cache_cmd_lock == False:
            cache_cmd = ""
        if (state == ScanState.STRING_STATE) or (
                state == ScanState.COMMENT_STATE and comment_flag == AsKeyWord.SINGLE_COMMENT_FLAG):  # 换行字符阅读状态清零
            state = ScanState.CODE_STATE
        for charIndex in range(0, len(line)):
            char = line[charIndex]
            code = ord(char)
            if update_cmd:
                last_cmd = cur_cmd
                cur_cmd = ""
            if (code != 32 and code != 9 and char != "{" and char != "}" and char != "(" and char != ")" and char != ";"):
                cur_cmd = cur_cmd + char
                update_cmd = False
            else:  #
                update_cmd = True  # 标志更新清空重新读取
            if not inner_function and cur_cmd in AsKeyWord.CODE_CMD_ARR:  # 在function中也会有var 等关键字，故需要判断是否在function 中遍历
                cache_cmd = cur_cmd
            # 注释阅读模式
            if state == ScanState.COMMENT_STATE:
                if comment_flag == "":
                    raise Exception("scan comment state but found comment_flag is empty", 1)
                if comment_flag == AsKeyWord.MUTI_COMMENT_FLAG_START:  # 多行注释，扫描注释结束符号
                    if cur_cmd.endswith(AsKeyWord.MUTI_COMMENT_FLAG_OVER):
                        state = ScanState.CODE_STATE
                        cur_line_data.start_index = charIndex + 1
                        comment_flag = ""
                        cur_cmd = ""
                    else:
                        pass
                elif comment_flag == AsKeyWord.SINGLE_COMMENT_FLAG:  # 单行注释，直接跳转下一行
                    state = ScanState.CODE_STATE
                    break
            # 字符阅读模式
            elif state == ScanState.STRING_STATE:
                if str_flag == "":
                    raise Exception("scan string state but found str_flag is empty", 1)
                if str_flag == char:  # 发现了字符串的结束符号
                    str_flag = ""
                    state = ScanState.CODE_STATE
                    cur_cmd = ""
                pass
            # 代码阅读模式
            elif state == ScanState.CODE_STATE:
                if char == "{":
                    level += 1
                if cur_cmd.endswith(AsKeyWord.MUTI_COMMENT_FLAG_START) or cur_cmd.endswith(
                        AsKeyWord.SINGLE_COMMENT_FLAG):
                    state = ScanState.COMMENT_STATE
                    comment_flag = AsKeyWord.MUTI_COMMENT_FLAG_START if cur_cmd.endswith(
                        AsKeyWord.MUTI_COMMENT_FLAG_START) else AsKeyWord.SINGLE_COMMENT_FLAG
                    cur_cmd = ""
                elif char == AsKeyWord.STRING_FLAG1 or char == AsKeyWord.STRING_FLAG2:
                    state = ScanState.STRING_STATE
                    str_flag = char
                    cur_cmd = ""
                elif cache_cmd == AsKeyWord.CODE_PACKAGE:
                    # 发现包声明
                    if cache_cmd_lock == False:
                        package_line = cur_line_data
                    cache_cmd_lock = True
                    if char == "{":
                        cache_cmd_lock = False
                        cache_cmd = ""
                        inner_package = True
                        package_level = level
                        cls_dic["inner_cls"] = ClsData(None)
                        cur_cls = cls_dic["inner_cls"]
                elif cache_cmd == AsKeyWord.CODE_IMPORT:
                    # self._add_to_arr(cur_cls.import_arr, cur_line_data)
                    pass
                elif cache_cmd == AsKeyWord.CODE_CLASS or cache_cmd == AsKeyWord.CODE_INTERFACE:
                    if cache_cmd_lock == False:
                        cur_cls.class_line_data = cur_line_data
                        if cache_cmd == AsKeyWord.CODE_INTERFACE:
                            cur_cls.is_interface = True
                    cache_cmd_lock = True
                    if inner_class == False:
                        if cur_cmd == AsKeyWord.CODE_EXTENDS:
                            cls_name = last_cmd
                            cur_cls.cls_name = last_cmd
                        elif char == "{":
                            if cur_cls.cls_name == None:
                                # 该类没有继承
                                cur_cls.cls_name = last_cmd
                            cache_cmd_lock = False
                            cache_cmd = ""
                            inner_class = True
                            class_level = level
                        if inner_class and (inner_package == False):
                            if cls_dic.has_key(cls_name):
                                return CodeError.SAME_CLASS
                            cls_dic[cls_name] = cur_cls
                elif cache_cmd == AsKeyWord.CODE_CONST or cache_cmd == AsKeyWord.CODE_VAR:
                    if not inner_class:
                        return CodeError.MISS_CHAR
                    lineStr = cur_line_data.get_show_content().strip()
                    matchObj = get_as_property_name.match(lineStr)
                    name = matchObj.group(1)
                    if cur_cls.property_arr.count(name) != 0:
                        return CodeError.SAME_PROPERTY
                    else:
                        cur_cls.property_arr.append(name)
                        break
                elif cache_cmd == AsKeyWord.CODE_FUNCTION:
                    if not inner_class:
                        return CodeError.MISS_CHAR
                    if cur_function_arr == None:
                        cur_function_arr = []
                        function_has_get_or_set = ""
                    # self._add_to_arr(cur_function_arr, cur_line_data)
                    cache_cmd_lock = True
                    if cur_cmd == AsKeyWord.CODE_GET or cur_cmd == AsKeyWord.CODE_SET:
                        function_has_get_or_set = cur_cmd
                    if inner_function == False:
                        if char == "(":
                            if function_has_get_or_set == "":
                                name = cur_cmd
                            else:
                                name = function_has_get_or_set + "/" + cur_cmd
                            if cur_cls.function_dic.has_key(name):
                                return CodeError.SAME_FUNCTION
                            cur_cls.function_dic[name] = cur_function_arr
                        else:
                            if cur_cls.is_interface:
                                if char == ";":
                                    cache_cmd_lock = False
                                    cache_cmd = ""
                                    cur_function_arr = None
                            elif char == "{":
                                inner_function = True
                                function_level = level
                    else:
                        if char == "}":
                            if level == function_level:
                                # function结构体结束了
                                cache_cmd_lock = False
                                cache_cmd = ""
                                cur_function_arr = None
                                inner_function = False
                else:
                    pass
                if char == "}":
                    if level == class_level:
                        inner_class = False
                        cur_cls = ClsData(None)  # 初始化cur_cls为下一个类做准备
                    if level == package_level:
                        inner_package = False
                    level -= 1
    if level != 0:
        return CodeError.MISS_CHAR
    else:
        return CodeError.NONE_ERROR




if __name__=="__main__":
    line1 = 'a.b.c'
    line2 ='a.b'
    line3 = 'a.b.c.e'
    print get_code_match(line1,line3,True)
    # print get_code_match(line1,line3)
    # print get_code_match(line3,line2)
    # fileUrl = r"D:/workspace/French/fr_client_proj/trunk/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity/bringinMoney/BMEntryView.as"
    # file = File(fileUrl,True)
    # lines = file.get_line_datas()
    # for i in range(0, len(lines)):
    #     line = lines[i].get_show_content()
    #     matchObj = get_as_property_name.match(line)
    #     if matchObj:
    #         print matchObj.groups()

