#coding=utf-8
import re

class ScanState:
    COMMENT_STATE = 1 #注释阅读状态
    STRING_STATE = 2 #字符串阅读状态
    CODE_STATE = 3 #代码批量阅读状态，寻找声明行

class AsKeyWord:
    MUTI_COMMENT_FLAG_START = "/*"
    MUTI_COMMENT_FLAG_OVER = "*/"
    SINGLE_COMMENT_FLAG = "//"
    STRING_FLAG1 = "'"
    STRING_FLAG2 = '"'
    CODE_PACKAGE = "package"
    CODE_IMPORT = "import"
    CODE_CLASS = "class"
    CODE_VAR = "var"
    CODE_CONST = "const"
    CODE_FUNCTION = "function"
    CODE_EXTENDS = "extends"
    CODE_IMPLEMENTS = "implements"
    CODE_SET = "set"
    CODE_GET = "get"
    CODE_INTERFACE = "interface"
    CODE_PUBLIC = "public"
    CODE_PRIVATE = "private"
    CODE_PROTECTED = "protected"
    CODE_INTERNAL = "internal"
    CODE_STATIC = "static"
    CODE_CMD_ARR = [CODE_PACKAGE,CODE_IMPORT,CODE_CLASS,CODE_VAR,CODE_CONST,CODE_FUNCTION,CODE_INTERFACE]
    FUNCTION_PACKAGE = [CODE_PUBLIC, CODE_PRIVATE, CODE_PROTECTED, CODE_INTERNAL]

class PrefabKeyWord:
    CLASS_FLAG = "!u!"
    FILEID_FLAG = "&"
    ELEMENT_FLAG = "---"
    ELEMENT_LINE_REG = re.compile(ur"---\s!u!([0-9]+)\s&([0-9]+)")
    ELEMENT_VALUE_REG = re.compile(ur"(\s*)(.+?):(.*)")

class FileFormat:
    AS = "ActionScript"
    XML = "Xml"
    NormalText = "NormalText"
    PREFAB = "Prefab"




if __name__=="__main__":
    s = "MonoBehaviour:"
    match_obj = PrefabKeyWord.ELEMENT_VALUE_REG.match(s)
    if match_obj:
        print len(match_obj.group(3))
