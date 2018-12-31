# 注意文件读取的代码在Release时，要进行统一封装
import sys
# import time
import json
# import urllib
# import traceback
from PyQt4 import QtCore, QtGui
from urllib.parse import urlparse
from ResumeAutometa.UserInterface.quick_interface import QuickInterface
from ResumeAutometa.BrowserAutoMeta.helper_project.resume_thrower import ResumeThrower


class DownloadThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.mission = dict()
        self.switchboard = dict()
        self.progress_step = 0

    def give_order(self, mission, switchboard):
        self.mission = mission
        self.switchboard = switchboard
        for key, value in self.mission.items():
            if value:
                self.progress_step += len(value)
        self.progress_step = 100/self.progress_step

    def clear_order(self):
        self.mission = dict()
        self.switchboard = dict()
        self.progress_step = 0

    def run(self):
        handler = ResumeThrower(self.mission, self.switchboard)
        summation = 0.0
        for msg_info in handler.run():
            msg_cat = msg_info[0]
            msg_content = msg_info[1]
            self.emit(QtCore.SIGNAL('log'), msg_content)
            if msg_cat == "progress":
                summation += self.progress_step
                self.emit(QtCore.SIGNAL('progress'), summation)
        self.clear_order()


        '''
        try:
            listItems = self.list_widget.selectedItems()
            for item in listItems:
                self.list_widget.removeItemWidget(self.list_widget.row(item))
        except:
            print traceback.format_exc()
        '''


class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.mission = dict()
        self.list_widget_log = QtGui.QListWidget()
        self.read_button = QuickInterface.gen_default_button('读取投递任务文件')
        self.start_button = QuickInterface.gen_default_button("开始投递")

        self.login_confirm_button = QuickInterface.gen_default_button("确认登陆")
        self.progress = QtGui.QProgressBar()
        self.switchboard = {"wait_login": True, "confirm_permission": False}
        self.download_thread = DownloadThread()

        self.read_button.clicked.connect(self.read_file)
        self.start_button.clicked.connect(self.start_download)
        self.login_confirm_button.clicked.connect(self.login_confirm)

        self.connect(self, QtCore.SIGNAL('log'), self.set_log_stream)
        self.connect(self.download_thread, QtCore.SIGNAL('log'), self.set_log_stream)
        self.connect(self.download_thread, QtCore.SIGNAL('progress'), self.set_progress)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.read_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.login_confirm_button)
        layout.addWidget(self.list_widget_log)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def check_url(self, site_name, url):
        try:
            url_info = urlparse(url)
            url_netloc = url_info.netloc
            if site_name in url_netloc:
                result = True
            else:
                result = False
        except:
            result = False
        return result

    def check_file(self, fname):
        try:
            fcontent = open(fname, "r")
            self.mission = json.load(fcontent)
            if not isinstance(self.mission, dict):
                self.mission = dict()
                result = False
            else:
                result = True
                for key, value in self.mission.items():
                    if not isinstance(key, str) or not isinstance(value, list):
                        self.mission = dict()
                        result = False
                        break
                    else:
                        tmp_list = []
                        for url in value:
                            if self.check_url(key, url):
                                tmp_list.append(url)
                            else:
                                self.emit(QtCore.SIGNAL('log'), "小助手：这好像有点对不上哦 %s， %s" % (key, url))
                        self.mission[key] = tmp_list
        except:
            result = False
        return result

    def read_file(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c://', "Text files (*.txt)")
        if fname:
            if self.check_file(fname):
                self.emit(QtCore.SIGNAL('log'), "小助手：文件读取成功！")
            else:
                self.emit(QtCore.SIGNAL('log'), "小助手：抱歉文件损坏了...")

    def start_download(self):
        if self.mission:
            self.emit(QtCore.SIGNAL('log'), "小助手：投递程序正式开始！")
            self.download_thread.give_order(self.mission, self.switchboard)
            self.download_thread.start()
        else:
            self.emit(QtCore.SIGNAL('log'), "小助手：您还没有加载投递任务哦~")

    def login_confirm(self):
        if self.switchboard["confirm_permission"]:
            self.switchboard["confirm_permission"] = False
            self.switchboard["wait_login"] = False

    def set_progress(self, pnumber):
        self.progress.setValue(pnumber)

    def set_log_stream(self, msg):
        self.list_widget_log.addItem(msg)
        if len(self.list_widget_log) > 20:
            self.list_widget_log.takeItem(0)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())