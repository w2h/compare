#coding:utf-8
import os
import json
import time
# from data import *
import svn.remote
import urllib
# import time
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

import wx
import wx.lib.sized_controls as sc

app = wx.App(0)

frame = sc.SizedFrame(None, -1, "A sized frame")

pane = frame.GetContentsPane()
pane.SetSizerType("horizontal")

b1 = wx.Button(pane, wx.ID_ANY)
t1 = wx.TextCtrl(pane, -1)
t1.SetSizerProps(expand=True)

frame.Show()

app.MainLoop()



