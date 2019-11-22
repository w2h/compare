#encoding=utf-8
import xlrd
import os
import re,types,sys
from xlutils.copy import copy
reload(sys)
sys.setdefaultencoding('utf-8')
reg_i18n = re.compile(ur'I18n.lang\((\S+?)\)') #匹配这样的字符串：I18n.lang("as_include_c195d230e416f8e42ab8b81d44754d27")
package_reg = re.compile(ur"^package\s*\w*")
import_reg = re.compile(ur"^import\s+\w.+?[;|\n]")
class_reg = re.compile(ur"^public\s+class\s+\w+\{*")
global_var_reg = re.compile(ur"\s+(const)|(var)\s+\S+.*=\s*\S+")
function_reg = re.compile(ur".+\bfunction\b\s+(\w+)\((\w+:\w+).+")
local_var_reg = re.compile(ur"(\w+\s*)=(\s*I18n.lang\([\"\'](\S+?)[\"\']\)).*")
string_reg = re.compile(ur"[\"|\']\w+[\"|\']")

get_as_property_name = re.compile(ur".*[(var)|(const)]\s+(\w+?)([:;=]).*")


class AsObject:
    PACKAGE_LINE=1
    CLASS_LINE=2
    FUNCTION_BLOCK=3
    CLASS_VAR_LINE=4
    IMPORT_LINE=5
    def __init__(self,content,startIndex,endIndex,type):
        self.content = content
        self.start_index = startIndex
        self.end_index = endIndex



str = "private static const _asset:ViewAwardsUI;"
match_obj = get_as_property_name.search(str)
print match_obj.groups()