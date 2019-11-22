def get_parent_path(path):
    return path[0:path.rfind("/")]

import os
def is_svn_url_exists(url):
    state = os.system("svn info "+url)
    return state == 0

import svn.remote as remote
def is_svn_url_dir(url):
    r = remote.RemoteClient(url)
    return r.info()["entry_kind"] == "dir"

def is_url_dir(url):
    if url.startswith("http"):
        return is_svn_url_dir(url)
    else:
        return os.path.isdir(url)
def is_url_exists(url):
    if url.startswith("http"):
        return is_svn_url_exists(url)
    else:
        return os.path.exists(url)

def split_path_name_and_parent(path):
    index = path.rfind("/")
    return path[:index], path[index+1:]

def get_suffix_by_url(url):
    index = url.rfind(".")
    return url[index:]
