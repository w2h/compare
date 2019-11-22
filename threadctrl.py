#coding:utf-8
import threading
import thread
import time

class ThreadFunObj(object):
    def start(self):
        pass

    def stop(self):
        pass

class MyThread(threading.Thread):
    STATIC_ID = 0
    def __init__(self,threadName, threadFunObj, onCompleteFuc=None):
        threading.Thread.__init__(self)
        self.thread_fun_obj = threadFunObj
        self.setName(threadName)
        self.complete_fuc = onCompleteFuc
        MyThread.STATIC_ID += 1
        self.id = MyThread.STATIC_ID
    def run(self):
        self.thread_fun_obj.start()
        if self.complete_fuc:
            self.complete_fuc()
    def __del__(self):
        del self.complete_fuc
        del self.thread_fun_obj
        print self.getName()+"over"

    def destory(self):
        self.thread_fun_obj.stop()
        print self.getName()+"is breaked"



class ThreadInstance(object):
    Instance = None
    def __init__(self, rootFrame):
        if ThreadInstance.Instance:
            raise Exception("instance is exists")
        self.root_frame = rootFrame
        ThreadInstance.Instance = self
        self.is_start = False
    def _loop(self, name, level):
        index = 1
        isBusy = True
        while True:
            time.sleep(1)
            threadList = threading.enumerate()
            if len(threadList) > 1:
                isBusy = False
                for t in threadList:
                    if isinstance(t, MyThread):
                        self.root_frame.SetStatusText(t.getName()+"."*index)
                        isBusy = True
                        index += 1
                        if index > 3:
                            index = 1
                        break
            if not isBusy:
                self.root_frame.SetStatusText("ready")
    def start(self):
        if self.is_start:
            return
        thread.start_new_thread(self._loop, ("MainLoop", 1))
        self.is_start = True

    def stop_all(self):
        threadList = threading.enumerate()
        if len(threadList) > 1:
            for t in threadList:
                if isinstance(t, MyThread):
                    t.destory()

    def stop_by_thread_id(self, id):
        threadList = threading.enumerate()
        if len(threadList) > 1:
            for t in threadList:
                if isinstance(t, MyThread):
                    if t.id == id:
                        t.destory()










