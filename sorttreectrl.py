#coding=utf-8
import wx
import os
from pathutils import *
import svn.remote as remote
from threadctrl import *
from event import *
from data import *


class TreeItemData(object):
    FILE = 1
    DIR = 0
    CONFLICT_BACK_COLOR = wx.Colour(255, 227, 227)
    CONFLICT_TEXT_COLOR = wx.Colour(255, 0, 0)
    NORMAL_BACK_COLOR = wx.Colour(212,212,212)
    NORMAL_TEXT_COLOR = wx.Colour(0,0,0)
    MERGED_BACK_COLOR = wx.Colour(213,255,255)
    MERGED_TEXT_COLOR = wx.Colour(0,191,191)
    def __init__(self,isDir=False,url=None,name=None, relative_path=None):
        '''
        :param isDir: is dir or file
        :param url: the url of file in the disk
        :param name: the file name
        :param relative_path: The path relative to the root directory
        '''
        self.isDir = isDir
        self.url = url
        self.name = name
        self.relative_path = relative_path
        self.compare_result = CompareFilter.NONE

class SortTreeCtr(wx.TreeCtrl):

    def __init__(self,parent,root):
        wx.TreeCtrl.__init__(self,parent,id=wx.ID_ANY,style=wx.TR_NO_BUTTONS)
        self._item_dic = {}
        self.root = root
        self.file_filter = FilterData.get_default_value()
        self.merge_filter = CompareFilter.ALL
        self.praseThread = None
        self.ready = False

        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, size=wx.Size(16, 16)))
        imglist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16, 16)))
        self.AssignImageList(imglist)

    def set_item_conflict(self,item):
        self.SetItemBackgroundColour(item, TreeItemData.CONFLICT_BACK_COLOR)
        self.SetItemTextColour(item, TreeItemData.CONFLICT_TEXT_COLOR)

    def set_item_merged(self, item):
        self.SetItemBackgroundColour(item, TreeItemData.MERGED_BACK_COLOR)
        self.SetItemTextColour(item, TreeItemData.MERGED_TEXT_COLOR)

    def set_item_normal(self,item):
        self.SetItemBackgroundColour(item, TreeItemData.NORMAL_BACK_COLOR)
        self.SetItemTextColour(item, TreeItemData.NORMAL_TEXT_COLOR)

    def refresh_filters(self, inFilter):
        if not self.file_filter.equare(inFilter):
            self.file_filter = inFilter
            self.clear()
            self._init_tree()

    def get_ready(self):
        return self.ready


    def clear(self):
        self.DeleteAllItems()
        self._item_dic.clear()
        self.ready = False
        if self.praseThread:
            self.praseThread.destory()


    def set_path(self, path):
        self.root = path
        self._init_tree()
    def get_path(self):
        return self.root


    def _init_tree(self):
        root = self.root
        if not is_url_exists(root):
            print "not find path:" + str(root)
            return
        if not is_url_dir(root):
            print "not dir:" + str(root)
            return
        dirName = root[root.rfind("/") + 1:]
        rootParent = root[:root.rfind("/")]
        rootNode = self.AddRoot(dirName, image=0)
        self.SetItemData(rootNode, TreeItemData(True, self.root, dirName, "root"))
        if root.startswith("http"):
            prase = PraseSvnTree(self, rootNode, root, rootParent, self.file_filter)
            self.praseThread = MyThread("远程解析SVN目录", prase, self._on_prase_complete)
            self.praseThread.start()
        else:
            prase = PraseLocalTree(self, rootNode, root, rootParent, self.file_filter)
            self.praseThread = MyThread("解析本地目录", prase, self._on_prase_complete)
            self.praseThread.start()

    def _on_prase_complete(self):    # tree.ExpandAll()
        self.SortChildren(self.GetRootItem())
        self.praseThread = None
        self.ready = True
        evt = FrameEvent(id=wx.ID_ANY, type=FrameEventType.TREE_READY)
        self.ProcessEvent(evt)

    def refresh_merge_filter(self, mergeFilter):
        if self.merge_filter != mergeFilter:
            if self.merge_filter == CompareFilter.ALL:
                self.merge_filter = mergeFilter
                for key in self._item_dic:
                    item, data = self._item_dic[key]
                    if not data.isDir and data.compare_result != mergeFilter:
                        self.Delete(item)
            else:
                pass
                # 重新用已有的数据渲染一次树
        self.clean_tree()
    def clean_tree(self):
        root = self.GetRootItem()
        def checkNode(curItem,cookie):
            hasFile = False
            nextItem = curItem
            while nextItem:
                curItem = nextItem
                nextItem, cookie = self.GetNextChild(curItem, cookie)
                if self.ItemHasChildren(curItem):
                    child,cookie = self.GetFirstChild(curItem)
                    child_has_file = checkNode(child,cookie)
                    if not child_has_file:
                        self.Delete(child)
                    hasFile = child_has_file or hasFile
                else:
                    itemData = self.GetItemData(curItem)
                    if not itemData.isDir:
                        hasFile = True
                    else:
                        self.Delete(curItem)
            return hasFile
        checkNode(root, wx.ID_ANY)


    def ge_item_by_relative_path(self, path):
        if self._item_dic.has_key(path):
            return self._item_dic[path]
        return None
    def get_item_data_by_relative_path(self,path):
        return self.ge_item_by_relative_path(path)[1]

    def Delete(self, item, destory=False):
        if destory:
            data = self.GetItemData(item)
            del self._item_dic[data.relative_path]
        wx.TreeCtrl.Delete(self, item)

    def SetItemData(self, item, data):
        wx.TreeCtrl.SetItemData(self, item, data)
        self._item_dic[data.relative_path] = (item, data)

    def get_item_dic(self):
        return self._item_dic

    def OnCompareItems(self, item1, item2):
        data1 = self.GetItemData(item1)
        data2 = self.GetItemData(item2)
        if (data1 != None and data2 != None):
            if data1.isDir:
                if data2.isDir:
                    return 1 if data1.name.lower() > data2.name.lower() else -1
                else:
                    return -1
            else:
                if data2.isDir:
                    return 1
                else:
                    return 1 if data1.name.lower() > data2.name.lower() else -1
        return 0

    def Destory(self):
        self.clear()
        wx.TreeCtrl.Destroy(self)


class PraseSvnTree(ThreadFunObj):
    def __init__(self,tree, parentNode, url, rootParent, inFilter=None):
        self.tree = tree
        self.parentNode = parentNode
        self.url = url
        self.rootParent = rootParent
        self.filter = inFilter
        self.running_flag = False

    def start(self):
        self.running_flag = True
        self.praseTree(self.tree, self.parentNode, self.url, self.rootParent)
        self.running_flag = False

    def praseTree(self, tree, parentNode, url, rootParent):
        svnRoot = remote.RemoteClient(url)
        fileList = svnRoot.list(True)
        has_child = False
        for svnFile in fileList:
            if not self.running_flag:
                return
            has_item = False
            file = svnFile["name"]
            filePath = url+"/"+file
            relative_path = filePath[len(url) + 1:]
            # print "relative_path:", relative_path
            if svnFile['kind'] == "dir":
                childNode = tree.AppendItem(parentNode, file, TreeItemData.DIR)
                tree.SetItemData(childNode, TreeItemData(True, filePath, file, relative_path))
                dir_has_child = self.praseTree(tree,childNode, filePath, rootParent)
                if not dir_has_child:
                    tree.Delete(childNode, True)
                has_child = dir_has_child or has_child
            else:
                if self.filter != None:
                    if self.filter.enable():
                        if not self.filter.include(file):
                            continue
                        if not self.filter.exclude(file):
                            continue
                childNode = tree.AppendItem(parentNode, file, TreeItemData.FILE)
                tree.SetItemData(childNode, TreeItemData(False, filePath, file, relative_path))
                has_child = True
        return has_child

    def stop(self):
        self.running_flag = False

    def __del__(self):
        del self.tree
        del self.parentNode
        del self.url
        del self.rootParent
        del self.filter
        print "解析类清理完成"


class PraseLocalTree(PraseSvnTree):

    def praseTree(self, tree, parentNode, url, rootParent):
        has_child = False
        for file in os.listdir(url):
            if not self.running_flag:
                return
            filePath = os.path.join(url, file).replace("\\", "/")
            relative_path = filePath[len(rootParent) + 1:]
            # print "relative_path:", relative_path
            if os.path.isdir(filePath):
                childNode = tree.AppendItem(parentNode, file, TreeItemData.DIR)
                tree.SetItemData(childNode, TreeItemData(True, filePath, file, relative_path))
                dir_has_child = self.praseTree(tree, childNode, filePath, rootParent)
                if not dir_has_child:
                    tree.Delete(childNode, True)
                has_child = dir_has_child or has_child
            else:
                if self.filter != None:
                    if self.filter.enable():
                        if not self.filter.include(file):
                            continue
                        if not self.filter.exclude(file):
                            continue
                childNode = tree.AppendItem(parentNode, file, TreeItemData.FILE)
                tree.SetItemData(childNode, TreeItemData(False, filePath, file, relative_path))
                has_child = True
        return has_child





class TreeController(object):
    '''
    三方对比对于文件夹列表的同步控制
    '''

    EXPAND_OPRA = 1
    COLLAPSE_OPERA = 0

    def __init__(self):
        self._tree_arr = []
        self.scroll_ctrl = TreeCompareScrollCtrl()

        pass
    def destory(self):
        for tree in self._tree_arr:
            tree.Unbind(wx.EVT_TREE_ITEM_ACTIVATED)
        self._tree_arr = None
        self.scroll_ctrl.destory()

    def register_tree(self, tree):
        self.scroll_ctrl.add_tree(tree)
        if tree not in self._tree_arr:
            tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_tree_activated)
            self._tree_arr.append(tree)
            return True
        else:
            return False

    def _on_tree_activated(self, evt):
        item = evt.GetItem()
        tree = evt.GetEventObject()
        text = tree.GetItemText(item)
        item_data = tree.GetItemData(item)
        if not item_data.isDir:
            evt = FrameEvent(id=evt.GetId(), type=FrameEventType.OPEN_FILE, data=item_data)
            EventManager.get_instance().ProcessEvent(evt)
        else:
            # label = self._get_tree_label(evt.GetEventObject(), evt.GetItem())
            if tree.ItemHasChildren(item):
                if tree.IsExpanded(item):
                    self._opera_other_tree(tree, item_data, TreeController.COLLAPSE_OPERA)
                else:
                    self._opera_other_tree(tree, item_data, TreeController.EXPAND_OPRA)
        evt.Skip()

    def _opera_other_tree(self, cur_tree, itemData, type):
        for tree in self._tree_arr:
            if cur_tree is not tree:
                curChild = tree.ge_item_by_relative_path(itemData.relative_path)[0]
                if curChild == None:
                    continue
                # 打开文件夹
                if type == TreeController.EXPAND_OPRA:
                    tree.Expand(curChild)
                    # print "expand"
                # 关闭文件夹
                elif type == TreeController.COLLAPSE_OPERA:
                    tree.Collapse(curChild)
                    # print "collapse"
                # tree.ScrollTo(curChild)


    # 获取Item的相对路径
    def _get_tree_label(self, tree, itemId):
        resultStr = tree.GetItemText(itemId)
        curItemId = itemId
        while (tree.GetRootItem() != curItemId):
            curItemId = tree.GetItemParent(curItemId)
            resultStr = resultStr + "/" + tree.GetItemText(curItemId)
        return resultStr

    # 滑动到指定的item（同时进行同样的动作，折叠或打开），如果没有，则滑到最近的item-   ---------------------------------------------
    def _get_tree_item(self, tree, label):
        if not tree:
            return None
        curChild = tree.GetRootItem()
        # print "root:"+tree.GetItemText(curChild)
        if label.find("/") == -1:
            labelArr = [label]
        else:
            labelArr = label.split("/")
            labelArr.reverse()
            print "label:"
            print labelArr
            curChild, cookie = tree.GetFirstChild(curChild)
            print curChild
            for index in range(1, len(labelArr)):
                curLabel = labelArr[index]
                print "cur:" + curLabel
                while (tree.GetItemText(curChild) != curLabel):
                    curChild, cookie = tree.GetNextChild(curChild, cookie)
                    if curChild.IsOk == False:
                        break
                if curChild.IsOk == False:
                    break
                if index < len(labelArr) - 1:
                    curChild, cookie = tree.GetFirstChild(curChild)
        return curChild


class TreeCompareScrollCtrl(object):
    def __init__(self):
        self.tree_arr = []
        pass
    def add_tree(self, tree):
        if tree not in self.tree_arr:
            self.tree_arr.append(tree)
            tree.Bind(wx.EVT_PAINT, self._on_scroll_change)


    def _on_scroll_change(self,evt):
        tree = evt.GetEventObject()
        firstItem = tree.GetFirstVisibleItem()
        if firstItem and firstItem.IsOk():
            itemData = tree.GetItemData(firstItem)
            for otherTree in self.tree_arr:
                if otherTree is not tree:
                    item,data = otherTree.ge_item_by_relative_path(itemData.relative_path)
                    if item:
                        otherTree.ScrollTo(item)
            evt.Skip()

    def destory(self):
        for tree in self.tree_arr:
            tree.Unbind(wx.EVT_SCROLLWIN)
        self.tree_arr = None
