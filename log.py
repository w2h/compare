#coding=utf-8

class Logger(object):
    def __init__(self, path):
        self.file_path = path
        # self.file = open(self.file_path, "w")
        print "logger init"

    def log_line(self,txt):
        return
        self.file.write(txt)
        # self.file.flush()

    def log_list(self,list):
        return
        self.file.writelines(list)
        # self.file.flush()

    def close(self):
        # self.file.close()
        print "log saved"

logger = Logger("log.txt")