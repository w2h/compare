#coding=utf-8
import os
import requests
import json
import time
from data import *
import svn.remote
import urllib
import time
import base64
from diff_match_patch import diff_obj
# from diff import diff_obj

# url = r"D:\workspace\German\de_client_proj\branches\DE_NarutoAlpha5.50\src\naruto.activity\src\com\tencent\morefun\naruto\plugin\activity\comeback\ComebackPanel.as"
# url = url.replace("\\","/")
# lines = open(url,mode="r").readlines()
# print len(lines)
# i = 0
# line = LineData(0, 0, 10, "abcdefghigh")
# p = "show_line_num"
# print getattr(line,p)
svn_root_url = ur'http://tc-svn.tencent.com/narutoI18n/de_client_proj/branches/DE_NarutoAlpha5.50/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity/comeback/ComebackPanel.as'
# svn_root = svn.remote.RemoteClient(svn_root_url)
str1 = "cbcdef"
str2 = "bbcdefsdf"
a =2
b =3
c = 2

arr = [1,2,3,4,5]
del arr[1]
lt = 10
# l_url  = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window/UILobbyTask3_new.prefab".replace(
#                 "\\", "/")
# r_url  = r"G:\naruto_next_proj\release\god_trunk\TheNextMOBA\Assets\Resources\Prefabs\UI\Task\Window/UILobbyTask3.prefab".replace(
#                 "\\", "/")

l_url = r"D:\workspace\Poland\pl_client_proj\branches\PL_NarutoAlpha3.39\src\naruto.welfare\src\com\tencent\morefun\naruto\plugin\welfare\views\combat\CombatTabItemRenderer.as"
r_url = r"D:\workspace\German\de_client_proj\branches\DE_NarutoAlpha5.50\src\naruto.welfare\src\com\tencent\morefun\naruto\plugin\welfare\views\combat\CombatTabItemRenderer.as"
l_file = File(l_url)
r_file = File(r_url)
l_ct = l_file.lines
r_ct = r_file.lines
# l_ct = "var npcIcon:Sprite;"
# r_ct = "var npcIcon:Image;"
# arr = diff_obj.diff_main(l_ct, r_ct)
# lcs = diff_obj.diff_levenshtein(arr)
# t1 = diff_obj.diff_text1(arr)
# t2 = diff_obj.diff_text2(arr)
# print "t:"+str(time.time() - st)
# print "finish"
arr = [x for x in range(10)]
st = time.time()
arr.pop(2)
arr.pop(2)
le = len(arr)
# with open("Compare_icon.ico",'rb') as f:
#     base64_data = base64.b64encode(f.read())
#     print base64_data.decode()


# print "1" is "1"
# l = svn_root.list(True)
# for value in l:
#     print value["kind"]
# print svn_root.info()["entry_kind"]
# svn_root.checkout(r"E:\workspace\i18n_tools_proj\trunk\xlstools\asmerge\openService",depth="empty")
# print os.system("svn info "+svn_root_url)
# os.system("svn co "+svn_root_url+" --depth=empty")
# os.chdir("openService")
# print os.getcwd()
# os.system("svn update IPage.as")
# print os.path.exists("http://tc-svn.tencent.com/narutoI18n/fr_client_proj/trunk/src/naruto.activity/src/com/tencent/morefun/naruto/plugin/activity/openService")
os.chdir(os.getcwd())

p = os.popen('svn info')
s = unicode(p.read().decode("gbk"))
lines = s.split("\n")
for line in lines:
    if line.startswith(u"最后修改的版本"):
        print line

def get_svn_revision(s):
    s = unicode(p.read().decode("utf-8"))
    lines = s.split("\n")
    for line in lines:
        if line.startswith(u"Last Changed Rev"):
            arr = line.split(" ")
            return arr[-1]


def get_svn_diff_files(path):
    os.chdir(path)
    p = os.popen("svn info -r BASE")
    curR = get_svn_revision(p.read().decode())
    p = os.popen("svn info -r HEAD")
    newR = get_svn_revision(p.read().decode())

    p = os.popen("svn diff -r"+curR+":"+newR)
    s = unicode(p.read().decode())
    lines = s.split("\n")
    arr = []
    for line in lines:
        if line.startswith("Index:"):
            value = line.split(" ")
            file = value[-1]
            arr.append(file)
    return arr




def getrevision(path):
    os.chdir(path)
    p = os.popen('svn info')
    s = unicode(p.read().decode("gbk"))
    lines = s.split("\n")
    for line in lines:
        if line.startswith(u"最后修改的版本"):
            print line

