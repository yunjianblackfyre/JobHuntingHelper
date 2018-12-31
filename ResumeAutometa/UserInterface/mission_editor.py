# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from ResumeAutometa.Foundations.utils import *
from ResumeAutometa.UserInterface.utils import QuickInterface, check_grand_setting
from ResumeAutometa.BrowserAutoMeta.helper_project.job_scraper import JobScraper
from ResumeAutometa.Config.file_paths import WEB_DRIVER_ACTION_SETTINGS

PAGE_SIZE = 10


class MissionEditor(QtGui.QWidget):
    def __init__(self, job_helper):
        super(MissionEditor, self).__init__()

        # 初始化隐藏变量
        self.helper = job_helper
        self.workers = []                           # 职位抓取蜂群
        self.working = False                        # 是否还有抓取任务在运行
        self.cur_working_count = 0                  # 当前正在运行的抓取任务
        self.mission_settings = dict()              # 抓取任务配置
        self.orig_settings = dict()                 # 原配置文件
        self.base_data_dict = dict()                # 基础任务内容
        self.small_window_dict = dict()             # 单个任务映射表
        self.row_idx2uq_idx = dict()                # 行ID基础任务ID映射表
        self.page_size = PAGE_SIZE                  # 页面大小
        self.current_page = 1                       # 当前页码

        # 初始化显示控件
        self.list_widget_show = QtGui.QListWidget()
        self.add_button = QuickInterface.gen_default_button("添加抓取任务")
        self.next_page = QuickInterface.gen_default_button("下一页")
        self.last_page = QuickInterface.gen_default_button("上一页")
        self.start_button = QuickInterface.gen_default_button("开始抓取")

        # 初始化爬取任务动态参数
        self.init_mission_settings()

        # 重新载入布局
        self.renew_layout()

    # 读取终极配置文件
    def init_mission_settings(self):
        file_name = WEB_DRIVER_ACTION_SETTINGS
        self.orig_settings = read_file_json(file_name)
        check_grand_setting(self.orig_settings)
        for site_name, site_settings in self.orig_settings.items():
            self.mission_settings[site_name] = dict()
            search_settings = site_settings["搜索选项"]
            for field, actions in search_settings.items():
                for action in actions:
                    if isinstance(action["arg"], dict):
                        choices = list(action["arg"].keys())
                        self.mission_settings[site_name][field] = choices

    # 刷新布局，用于翻页与初始化
    def renew_layout(self):
        # 重新初始化显示控件
        self.list_widget_show = QtGui.QListWidget()
        self.add_button = QuickInterface.gen_default_button("添加抓取任务")
        self.next_page = QuickInterface.gen_default_button("下一页")
        self.last_page = QuickInterface.gen_default_button("上一页")
        self.start_button = QuickInterface.gen_default_button("开始抓取")

        # 绑定按钮事件
        self.add_button.clicked.connect(self.add_new_mission)
        self.next_page.clicked.connect(self.to_next_page)
        self.last_page.clicked.connect(self.to_last_page)
        self.start_button.clicked.connect(self.start_download)

        # 初始化布局，呈现视图
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.add_button)
        layout.addWidget(self.list_widget_show)
        layout.addWidget(self.start_button)

        # 判断是否加载上一页或者下一页按钮
        if self.current_page != 1:
            layout.addWidget(self.last_page)
        if len(self.base_data_dict.keys()) > self.current_page * self.page_size:
            layout.addWidget(self.next_page)

        # 部署布局
        self.setLayout(layout)

        # 重新载入爬取任务列表
        self.reload_detail()

    # 添加新的爬取任务
    def add_new_mission(self):
        choices = list(self.mission_settings.keys())

        # 弹出对话框，提示用户选择任务类型
        choice, ok = QtGui.QInputDialog.getItem(self, "请选择网站", "招聘网站列表", choices, 0, False)
        if ok and choice:
            # 获取任务唯一ID
            unique_ids = list(self.base_data_dict.keys())
            if unique_ids:
                new_unique_id = max(unique_ids) + 1
            else:
                new_unique_id = 1

            # dyn_choices为下拉窗口，作为搜索时的过滤条件，是爬取任务重要环节 例：dyn_choices:{"地点":"上海","工作类型":"技术"}
            self.base_data_dict[new_unique_id] = {
                "mission_name": choice,
                "dyn_choices": dict(),
                "search_words": "请输入搜索词",
                "pagination": 1
            }
            for field in self.mission_settings[choice].keys():
                defualt_choice = self.mission_settings[choice][field][0]
                self.base_data_dict[new_unique_id]["dyn_choices"][field] = defualt_choice
            self.switch_layout()

    # 下一页按钮触发事件
    def to_next_page(self):
        self.current_page += 1
        self.switch_layout()

    # 上一页按钮触发事件
    def to_last_page(self):
        self.current_page -= 1
        self.switch_layout()

    # 翻页事件调用方法
    def switch_layout(self):
        # 清除当前显示列表行ID与隐藏任务列表元素ID映射表
        self.row_idx2uq_idx = dict()

        # 递归清除当前视图
        current_layout = self.layout()
        self.list_widget_show.clear()
        QtGui.QWidget().setLayout(current_layout)

        # 重新载入布局
        self.renew_layout()

    # 重新载入显式任务列表
    def reload_detail(self):
        row_index = 0
        unique_id_list = list(self.base_data_dict.keys())
        start_point = (self.current_page - 1) * self.page_size
        for unique_id in unique_id_list[start_point:start_point + self.page_size]:
            self.load_list_item(row_index, unique_id)
            row_index += 1

    # 重新载入显式任务
    def load_list_item(self, row_index, unique_id):
        # 初始化变量
        self.row_idx2uq_idx[row_index] = unique_id
        mission_name = self.base_data_dict[unique_id]["mission_name"]
        search_words = self.base_data_dict[unique_id]["search_words"]
        dyn_choices = self.base_data_dict[unique_id]["dyn_choices"]
        dyn_elements = []
        widget_layout = QtGui.QHBoxLayout()

        # 初始化窗口静态元素
        list_item = QtGui.QListWidgetItem()
        widget = QtGui.QWidget()
        widget_text = QtGui.QLabel(mission_name)
        widget_search_words = DirLineEdit(self, unique_id, search_words)
        widget_remove_button = QuickInterface.gen_default_button("删除任务")
        widget_set_pagination = PaginationSpinBox(self, unique_id)

        # 初始化窗口动态下拉框
        for field, choice in dyn_choices.items():
            widget_field_filter = DynComboBox(self, unique_id, mission_name, field, choice)
            widget_field_filter.setFixedSize(80, 20)
            dyn_elements.append(widget_field_filter)

        # 调整文本框、文本输入框、删除按钮之大小
        widget_text.setFixedSize(80, 20)
        widget_search_words.setFixedSize(200, 20)
        widget_remove_button.setFixedSize(150, 20)

        # 绑定删除任务按键事件
        self.connect(widget_remove_button, QtCore.SIGNAL("clicked()"),
                     lambda who=unique_id: self.delete_row(who))

        # 初始化显式任务元素布局
        widget_layout.addWidget(widget_text)
        widget_layout.addWidget(widget_search_words)
        for widgetFF in dyn_elements:
            widget_layout.addWidget(widgetFF)
        widget_layout.addWidget(widget_set_pagination)
        widget_layout.addWidget(widget_remove_button)
        widget_layout.addStretch()
        widget_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        widget.setLayout(widget_layout)
        list_item.setSizeHint(widget.sizeHint())
        self.list_widget_show.addItem(list_item)
        self.list_widget_show.setItemWidget(list_item, widget)

    # 删除按钮触发事件
    def delete_row(self, index):
        if index in self.small_window_dict.keys():
            self.small_window_dict.pop(index)
        if index in self.base_data_dict.keys():
            self.base_data_dict.pop(index)
        self.switch_layout()

    # 加载任务参数，准备启动浏览器
    def build_mission_detail(self, raw_mission):
        mission_name = raw_mission["mission_name"]
        mission_pagination = raw_mission["pagination"]
        mission_detail = {
            "搜索选项": [
                ["搜索页地址", ""]
            ],
            "翻页次数": mission_pagination
        }
        for field, choice in raw_mission["dyn_choices"].items():
            mission_detail["搜索选项"].append([field, choice])
        mission_detail["搜索选项"].append(["搜索关键词", raw_mission["search_words"]])
        static_settings = self.orig_settings[mission_name]
        return mission_name, mission_detail, static_settings

    # 开始下载按钮触发事件
    def start_download(self):
        if self.working:
            self.set_log_stream("小助手：请稍等哦，还有抓取任务正在运行")
            return
        self.working = True
        self.cur_working_count = 0
        self.set_tutorial("crawl")  # 通知教程，当前状态为正在抓取
        self.workers = []
        for value in self.base_data_dict.values():
            mission_name, mission_detail, static_settings = self.build_mission_detail(value)
            worker = ScrapWorker(self, mission_name, mission_detail, static_settings)
            self.workers.append(worker)
            self.cur_working_count += 1
        for worker in self.workers:
            self.connect(worker, QtCore.SIGNAL('log'), self.set_log_stream)
            worker.start()

    # 小助手信息通知触发事件
    def set_log_stream(self, msg):
        self.helper.list_widget_log.addItem(msg)
        if len(self.helper.list_widget_log) > 40:
            self.helper.list_widget_log.takeItem(0)

    # 教程信息通知触发事件
    def set_tutorial(self, last_action):
        self.helper.renew_tutorial(last_action)


# 搜索词编辑窗口
class DirLineEdit(QtGui.QLineEdit, QtCore.QObject):
    def __init__(self, main_window, unique_id, init_string):
        super(DirLineEdit, self).__init__()
        self.setText(init_string)
        self.unique_id = unique_id
        self.main_window = main_window
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self, string):
        self.main_window.base_data_dict[self.unique_id]["search_words"] = string


# 过滤条件下拉窗口
class DynComboBox(QtGui.QComboBox):
    def __init__(self, main_window, unique_id, mission_name, field, current_choice):
        super(DynComboBox, self).__init__()
        self.unique_id = unique_id
        self.main_window = main_window
        self.mission_name = mission_name
        self.field = field

        choices = self.main_window.mission_settings[mission_name][field]
        self.addItems(choices)
        index = self.findText(current_choice, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)
        self.currentIndexChanged.connect(self.selection_change)

    def selection_change(self, i):
        self.main_window.base_data_dict[self.unique_id]["dyn_choices"][self.field] = self.currentText()


# 翻页次数设置窗口
class PaginationSpinBox(QtGui.QSpinBox):
    def __init__(self, main_window, unique_id):
        super(PaginationSpinBox, self).__init__()
        self.unique_id = unique_id
        self.main_window = main_window

        self.setMaximum(50)
        self.setMinimum(1)
        self.setPrefix("翻页次数：")
        current_choice = self.main_window.base_data_dict[self.unique_id]["pagination"]
        self.setValue(current_choice)
        self.valueChanged.connect(self.pagination_changed)

    def pagination_changed(self):
        self.main_window.base_data_dict[self.unique_id]["pagination"] = self.value()


# 职位抓取工蜂
class ScrapWorker(QtCore.QThread):
    def __init__(self, editor, mission_name, mission_detail, static_settings):
        QtCore.QThread.__init__(self)
        self.editor = editor
        self.mission_name = mission_name
        self.mission_detial = mission_detail
        self.static_settings = static_settings
        self.bucket = []

    def run(self):
        task_executor = JobScraper(mission_name=self.mission_name, static_settings=self.static_settings,
                                   dynamic_sequence=self.mission_detial)
        for msg_info in task_executor.run():
            msg_content = msg_info[1]
            self.emit(QtCore.SIGNAL('log'), msg_content)
        self.bucket = task_executor.get_eggs()
        if self.editor.cur_working_count > 0:
            self.editor.cur_working_count -= 1
        if self.editor.cur_working_count == 0:
            self.editor.working = False

    def get_eggs(self):
        eggs = self.bucket
        return eggs

    def empty_bucket(self):
        self.bucket = []


"""
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MissionEditor()
    window.resize(720, 960)
    window.show()
    sys.exit(app.exec_())
"""
