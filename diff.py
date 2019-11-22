#coding=utf-8
#对比算法模块
def get_line_by_index(lines, indexs):
    result = []
    if len(indexs) > 0:
        for i in range(0, len(indexs)):
            result.append(lines[indexs[i]])
    return result

def get_index_by_commstring(source, dest):
    result = []
    if len(dest) > 0:
        curIndex = 0
        for i in range(0, len(source)):
            if source[i] == dest[curIndex]:
                result.append(i)
                curIndex += 1
            if curIndex >= len(dest):
                break
    return result

#以开始索引和结束索引，取出这块的索引，不包含结束索引，包含开始索引
def get_all_index_by_start_and_end(start, end):
    arr = []
    # start = int(start)
    # end = int(end)
    for i in range(start, end):
        arr.append(i)
    return arr


# 从公共字符串索引中，提取出需要对比的块（也就是diff3算法中的unstable chunk）
def get_diff_lcs_index(text,arr):
    diff_arr = []
    for i in range(0,len(arr)):
        if i == 0:
            lines = arr[i]
            if lines > 0:
                diff_arr.append((0, lines))
        else:
            lines = arr[i] - arr[i-1]
            if lines > 1:
                diff_arr.append((arr[i-1] + 1, lines - 1))
    lines = len(text) - arr[-1]
    if lines > 1:
        diff_arr.append((arr[-1] + 1, lines - 1))
    return diff_arr

 #找出公共的前缀
def diff_commonPrefix(text1, text2):
    # Quick check for common null cases.
    if not text1 or not text2 or text1[0] != text2[0]:
        return 0
    # Binary search.
    pointermin = 0
    pointermax = min(len(text1), len(text2))
    pointermid = pointermax
    pointerstart = 0
    while pointermin < pointermid:
        if text1[pointerstart:pointermid] == text2[pointerstart:pointermid]:
            pointermin = pointermid
            pointerstart = pointermin
        else:
            pointermax = pointermid
        pointermid = int((pointermax - pointermin) / 2 + pointermin)
    return pointermid

# 找出公共的后缀
def diff_commonSuffix(text1, text2):
    # Quick check for common null cases.
    if not text1 or not text2 or text1[-1] != text2[-1]:
        return 0
    # Binary search.
    pointermin = 0
    pointermax = min(len(text1), len(text2))
    pointermid = pointermax
    pointerend = 0
    while pointermin < pointermid:
        if (text1[-pointermid:len(text1) - pointerend] ==
                text2[-pointermid:len(text2) - pointerend]):
            pointermin = pointermid
            pointerend = pointermin
        else:
            pointermax = pointermid
        pointermid = int((pointermax - pointermin) / 2 + pointermin)
    return pointermid
# 匹配字符中间的公共串
def diff_halfMatch(text1, text2):
    # Do the two texts share a substring which is at least half the length of the
    # longer text?
    # 找出字符串中间部分超过一半的公共字符串
    if len(text1) > len(text2):
        (longtext, shorttext) = (text1, text2)
    else:
        (shorttext, longtext) = (text1, text2)
    if len(longtext) < 10 or len(shorttext) < 1:
        return None  # Pointless.

    def find(obj, dest, startIndex=0):
        if isinstance(obj, list):
            if dest in obj:
                result = obj.index(dest)
                if result >= startIndex:
                    return result
                else:
                    return -1
            else:
                return -1
        else:
            return obj.find(dest, startIndex)

    def diff_halfMatchI(longtext, shorttext, i):
        seed = longtext[i:i + len(longtext) / 4]
        best_common = ''
        j = find(shorttext, seed)
        best_longtext_a = ""
        best_longtext_b = ""
        best_shorttext_a = ""
        best_shorttext_b = ""
        while j != -1:
            prefixLength = diff_commonPrefix(longtext[i:], shorttext[j:])
            suffixLength = diff_commonSuffix(longtext[:i], shorttext[:j])
            # print "%s|%s+%s|%s vs. %s|%s+%s|%s" %
            #     (my_suffix[0], my_suffix[2], my_prefix[2], my_prefix[0],
            #     my_suffix[1], my_suffix[2], my_prefix[2], my_prefix[1])
            if len(best_common) < suffixLength + prefixLength:
                best_common = (shorttext[j - suffixLength:j] +
                               shorttext[j:j + prefixLength])
                best_longtext_a = longtext[:i - suffixLength]
                best_longtext_b = longtext[i + prefixLength:]
                best_shorttext_a = shorttext[:j - suffixLength]
                best_shorttext_b = shorttext[j + prefixLength:]
            j = find(shorttext, seed, j + 1)

        if len(best_common) >= len(longtext) / 2:
            return (best_longtext_a, best_longtext_b,
                    best_shorttext_a, best_shorttext_b, best_common)
        else:
            return None

    # First check if the second quarter is the seed for a half-match.
    hm1 = diff_halfMatchI(longtext, shorttext, (len(longtext) + 3) / 4)
    # Check again based on the third quarter.
    hm2 = diff_halfMatchI(longtext, shorttext, (len(longtext) + 1) / 2)
    if not hm1 and not hm2:
        return None
    elif not hm2:
        hm = hm1
    elif not hm1:
        hm = hm2
    else:
        # Both matched.  Select the longest.
        if len(hm1[4]) > len(hm2[4]):
            hm = hm1
        else:
            hm = hm2

    # A half-match was found, sort out the return data.
    if len(text1) > len(text2):
        (text1_a, text1_b, text2_a, text2_b, mid_common) = hm
    else:
        (text2_a, text2_b, text1_a, text1_b, mid_common) = hm
    return (text1_a, text1_b, text2_a, text2_b, mid_common)


class Diff_Proxy(object):
    def __init__(self):
        self.diff_obj = DiffObj2()
        self.diff_obj1 = DiffObj2()
        self.diff_obj2 = DiffObj2()

    def diff(self, text1, text2):
        self.input_text1 = text1
        self.input_text2 = text2
        l_index = diff_commonPrefix(text1, text2)
        self.commonPrefix = text1[:l_index]
        r_index = diff_commonSuffix(text1, text2)
        if r_index > 0:
            self.commonSuffix = text1[-r_index:]
            text1 = text1[l_index:-r_index]
            text2 = text2[l_index:-r_index]
        else:
            self.commonSuffix = []
            text1 = text1[l_index:]
            text2 = text2[l_index:]
        hm = diff_halfMatch(text1, text2)
        self.commonCenter = []
        self.text1_prefix_index = len(self.commonPrefix)
        self.text1_suffix_index = len(self.input_text1) - r_index
        if hm:
            text1_left, text1_right, text2_left, text2_right, centerText = hm
            self.commonCenter = centerText
            self.text1_l_index = len(self.commonPrefix) + len(text1_left)
            self.text1_r_index = len(self.commonPrefix) + len(text1_left) + len(self.commonCenter)
            self.diff_obj1.diff(text1_left, text2_left)
            self.diff_obj2.diff(text1_right, text2_right)
        else:
            self.diff_obj.diff(text1, text2)


    def get_lcs(self,isArr=False):
        result_arr = []
        if len(self.commonPrefix) > 0:
            result_arr.extend(self.commonPrefix)
        if len(self.commonCenter) > 0:
            result_arr.extend(self.diff_obj1.get_lcs(isArr))
            result_arr.extend(self.commonCenter)
            result_arr.extend(self.diff_obj2.get_lcs(isArr))
        else:
            result_arr.extend(self.diff_obj.get_lcs(isArr))
        if len(self.commonSuffix) > 0:
            result_arr.extend(self.commonSuffix)
        if isArr:
            return result_arr
        else:
            return "".join(result_arr)

    def get_lcs_indexs_by_text1(self):
        def modify_index_arr(arr, offset):
            for i in range(0, len(arr)):
                arr[i] = arr[i] + offset
            return arr
        def make_index_arr(start, len):
            arr = []
            for i in range(0, len):
                arr.append(start + 0)
            return arr
        result_arr =[]
        if len(self.commonPrefix) > 0:
            result_arr.extend(make_index_arr(0,len(self.commonPrefix)))
        if len(self.commonCenter) > 0:
            l_lcs = self.diff_obj1.get_lcs_indexs_by_text1()
            if len(l_lcs) > 0:
                result_arr.extend(modify_index_arr(l_lcs, self.text1_prefix_index))
            if len(self.commonCenter) > 0:
                result_arr.extend(modify_index_arr(make_index_arr(0, len(self.commonCenter)), self.text1_l_index))
            r_lcs = self.diff_obj2.get_lcs_indexs_by_text1()
            if len(r_lcs) > 0:
                result_arr.extend(modify_index_arr(r_lcs, self.text1_r_index))
        else:
            lcs = self.diff_obj.get_lcs_indexs_by_text1()
            if len(lcs) > 0:
                result_arr.extend(modify_index_arr(lcs, self.text1_prefix_index))
        if len(self.commonSuffix) > 0:
            result_arr.extend(modify_index_arr(make_index_arr(0, len(self.commonSuffix)), self.text1_suffix_index))
        return result_arr

class DiffObj(object):
    def __init__(self):
        self.DIFF_EQUAL = 0
        self.DIFF_DELETE = -1
        self.DIFF_INSERT = 1
        self.DIFF_PATH_DIAGONA = '↖'
        self.DIFF_PATH_VERTICAL = '↑'
        self.DIFF_PATH_HORIZONTAL = '←'
        self.dp = []
        self.path = []

    def diff(self,text1,text2):

        self.text1 = text1
        self.text2 = text2
        len1 = len(self.text1)
        len2 = len(self.text2)
        self.init(self.text1, self.text2)

        #空间优化
        k = 1
        k_subtract_one = 0
        for i in range(1,len1 + 1):
            for j in range(1,len2 + 1):
                if (self.text1[i - 1] == self.text2[j - 1]):
                    self.dp[k][j] = self.dp[k_subtract_one][j - 1] + 1
                    self.path[i][j] = self.DIFF_PATH_DIAGONA
                elif (self.dp[k_subtract_one][j] > self.dp[k][j - 1]):
                    self.dp[k][j] = self.dp[k_subtract_one][j]
                    self.path[i][j] = self.DIFF_PATH_VERTICAL
                else:
                    self.dp[k][j] = self.dp[k][j - 1]
                    self.path[i][j] = self.DIFF_PATH_HORIZONTAL
            k_subtract_one = k
            k = int(not k)

        # diff_result = self.get_diffs_from_path()
        # return diff_result
        return None

    def init(self,text1,text2):
        len1 = len(text1)
        len2 = len(text2)
        self.dp = []
        self.path = []
        # 空间优化2 * len2
        for i in range(0,2):
            self.dp.append([])
            for j in range(0, len2+1):
                self.dp[i].append(0)
        for i in range(0,len1+1):
            self.path.append([])
            for j in range(0, len2+1):
                self.path[i].append(0)

    def get_lcs(self,isArr=False):
        self.lcs = ""
        text = self.text1
        arr = []

        def path_lcs(i, j):
            if i == 0 or j == 0:
                return
            if (self.path[i][j] == self.DIFF_PATH_DIAGONA):
                path_lcs(i - 1, j - 1)
                self.lcs += text[i - 1]
                arr.append(text[i - 1])
            elif(self.path[i][j] == self.DIFF_PATH_VERTICAL):
                path_lcs(i - 1, j)
            elif (self.path[i][j] == self.DIFF_PATH_HORIZONTAL):
                path_lcs(i, j - 1)
        path_lcs(len(self.text1), len(self.text2))
        if isArr:
            return arr
        return self.lcs
    def get_lcs_indexs_by_text1(self):
        self.lcs_indexs = []
        def path_lcs(i, j):
            if i == 0 or j == 0:
                return
            if (self.path[i][j] == self.DIFF_PATH_DIAGONA):
                path_lcs(i - 1, j - 1)
                self.lcs_indexs.append(i - 1)
            elif (self.path[i][j] == self.DIFF_PATH_VERTICAL):
                path_lcs(i - 1, j)
            elif (self.path[i][j] == self.DIFF_PATH_HORIZONTAL):
                path_lcs(i, j - 1)

        path_lcs(len(self.text1), len(self.text2))
        return self.lcs_indexs

    def get_diffs_from_path(self):
        diffs = []
        path = self.path
        text1 = self.text1
        text2 = self.text2

        def path_diffs(i, j):
            if(i == 0 or j == 0):
                if(i != 0):
                    if isinstance(text1,str):
                        diffs.append([self.DIFF_DELETE, text1[0:i]])
                    else:
                        diffs.append([self.DIFF_DELETE, "".join(text1[0:i])])
                if(j != 0):
                    if isinstance(text2,str):
                        diffs.append([self.DIFF_INSERT, text2[0:j]])
                    else:
                        diffs.append([self.DIFF_INSERT, "".join(text2[0:j])])
                return
            if(self.path[i][j] == self.DIFF_PATH_DIAGONA):
                path_diffs(i - 1, j - 1)
                diffs.append([self.DIFF_EQUAL, text1[i - 1]])
            elif(path[i][j] == self.DIFF_PATH_VERTICAL):
                path_diffs(i - 1, j)
                diffs.append([self.DIFF_DELETE, text1[i - 1]])
            elif(path[i][j] == self.DIFF_PATH_HORIZONTAL):
                path_diffs(i, j - 1)
                diffs.append([self.DIFF_INSERT, text2[j - 1]])
        path_diffs(len(text1), len(text2))
        self.diffs = diffs
        return diffs
    def mergeDiffs(self,df):
        if (not df or not len(df)):
            return []
        diffs = []
        lst_op = df[0][0]
        lst_st = df[0][1]
        for i in range(0,len(df)):
            while (i < len(df) and df[i][0] == lst_op):
                lst_st += df[i][1]
                i += 1
            diffs.append([lst_op, lst_st])
            lst_st = ''
            if (i >= len(df)):
                break
            lst_op = df[i][0]
            lst_st = df[i][1]
        if (lst_st):
            diffs.append([lst_op, lst_st])
        return diffs


class DiffObj2(object):
    def __init__(self):
        self.m = None
        self.d = None
        self.s1 = []
        self.s2 = []
        pass
    def diff(self, s1, s2):
        if len(s1) == 0 or len(s2) == 0:
            return
        # 生成字符串长度加1的0矩阵，m用来保存对应位置匹配的结果
        m = [[0 for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]
        # d用来记录转移方向
        d = [[None for x in range(len(s2) + 1)] for y in range(len(s1) + 1)]

        self.m = m
        self.d = d
        self.s1 = s1
        self.s2 = s2

        for p1 in range(len(s1)):
            for p2 in range(len(s2)):
                if s1[p1] == s2[p2]:  # 字符匹配成功，则该位置的值为左上方的值加1
                    m[p1 + 1][p2 + 1] = m[p1][p2] + 1
                    d[p1 + 1][p2 + 1] = 'ok'
                elif m[p1 + 1][p2] > m[p1][p2 + 1]:  # 左值大于上值，则该位置的值为左值，并标记回溯时的方向
                    m[p1 + 1][p2 + 1] = m[p1 + 1][p2]
                    d[p1 + 1][p2 + 1] = 'left'
                else:  # 上值大于左值，则该位置的值为上值，并标记方向up
                    m[p1 + 1][p2 + 1] = m[p1][p2 + 1]
                    d[p1 + 1][p2 + 1] = 'up'

    def get_lcs(self,isArr=False):
        if len(self.s1) == 0 or len(self.s2) == 0:
            if isArr:
                return []
            return ''
        s = []
        s1 = self.s1
        s2 = self.s2
        m = self.m
        d = self.d
        (p1, p2) = (len(s1), len(s2))
        while m[p1][p2]:  # 不为None时
            c = d[p1][p2]
            if c == 'ok':  # 匹配成功，插入该字符，并向左上角找下一个
                s.append(s1[p1 - 1])
                p1 -= 1
                p2 -= 1
            if c == 'left':  # 根据标记，向左找下一个
                p2 -= 1
            if c == 'up':  # 根据标记，向上找下一个
                p1 -= 1
        s.reverse()
        if isArr:
            return s
        return ''.join(s)

    def get_lcs_indexs_by_text1(self):
        if len(self.s1) == 0 or len(self.s2) == 0:
            return []
        s = []
        indexs = []
        s1 = self.s1
        s2 = self.s2
        m = self.m
        d = self.d
        (p1, p2) = (len(s1), len(s2))
        while m[p1][p2]:  # 不为None时
            c = d[p1][p2]
            if c == 'ok':  # 匹配成功，插入该字符，并向左上角找下一个
                s.append(s1[p1 - 1])
                indexs.append(p1 - 1)
                p1 -= 1
                p2 -= 1
            if c == 'left':  # 根据标记，向左找下一个
                p2 -= 1
            if c == 'up':  # 根据标记，向上找下一个
                p1 -= 1
        indexs.reverse()
        return indexs

diff_obj = Diff_Proxy()