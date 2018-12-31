# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from ResumeAutometa.Computation.simm import simm
from ResumeAutometa.Computation.preprocessor import CContentClassifier
from ResumeAutometa.Computation.preprocessor import ProdContentPreproc
from ResumeAutometa.Computation.preprocessor import string2vector
from ResumeAutometa.Foundations.utils import read_file_json, write_data2json
from ResumeAutometa.UserInterface.utils import QuickInterface, check_grand_setting, read_json_list_safe
from ResumeAutometa.BrowserAutoMeta.helper_project.resume_thrower import ResumeThrower
from ResumeAutometa.Config.file_paths import WEB_DRIVER_ACTION_SETTINGS, RESUME_HISTORY

PAGE_SIZE = 10


class JobEditor(QtGui.QWidget):
    def __init__(self, helper):
        super(JobEditor, self).__init__()
        file_name = WEB_DRIVER_ACTION_SETTINGS
        self.orig_settings = read_file_json(file_name)
        self.throw_thread = ThrowWorker(self, self.orig_settings)

        # 初始化隐藏变量
        self.helper = helper
        self.base_data_dict = dict()                    # 职位内容
        self.sort_id2base_id = dict()                   # 排序索引基础索引映射表
        self.base_id2sort_id = dict()                   # 基础索引排序索引映射表
        self.resume_info = dict()                       # 简历详情
        self.unique_job_set = set()                     # 职位唯一标识
        self.row_idx2unq_idx = dict()                   # 视图列表元素与职位内容之映射
        self.smart_sort_state = False                   # 智能排序是否启用
        self.page_size = PAGE_SIZE                      # 视图列表元素最大个数
        self.current_page = 1                           # 视图当前页码
        self.working = False                            # 是否还有抓取任务在运行
        self.content_classifier = CContentClassifier()  # 简历或职位向量生成器
        self.content_preproc = ProdContentPreproc()     # 简历或职位标签提取器

        self.throw_history = read_json_list_safe(RESUME_HISTORY)
        self.throw_history = set(self.throw_history)
        check_grand_setting(self.orig_settings)

        # 初始化登陆开关
        self.switchboard = {
            "wait_login": True,
            "confirm_permission": False
        }

        # 初始化各种显式控件
        self.list_widget_show = QtGui.QListWidget()
        self.job_detail = JobDetailWindow()
        self.read_button = QuickInterface.gen_default_button("读取职位")
        self.read_resume_button = QuickInterface.gen_default_button("读取简历")
        self.smart_sort_checkbox = QtGui.QCheckBox("职位智能排序")

        self.next_page = QuickInterface.gen_default_button("下一页")
        self.last_page = QuickInterface.gen_default_button("上一页")

        self.set_all_button = QuickInterface.gen_default_button("全选本页职位")
        self.throw_button = QuickInterface.gen_default_button("投递职位")
        self.login_confirm_button = QuickInterface.gen_default_button("登陆确认")
        self.progress = QtGui.QProgressBar()

        # 绑定后台进程与信号处理方法
        self.connect(self.throw_thread, QtCore.SIGNAL('log'), self.set_log_stream)
        self.connect(self.throw_thread, QtCore.SIGNAL('progress'), self.set_progress)

        # 重新载入布局
        self.reload_layout()

    # ################################ 信号处理函数 ################################
    # 读取职位
    def to_front_page(self):
        self.set_tutorial("browse")  # 通知教程
        self.current_page = 1
        self.reload_base_data_dict()
        self.reset_layout()

    # 读取简历
    def read_resume(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'c://', "Text files (*.txt)")
        if fname:
            fcontent = open(fname, "rb")
            self.resume_info["职位描述"] = fcontent.read().decode()
            self.gen_content_vector(self.resume_info)
            self.gen_sort_info()

    # 智能排序开关
    def smart_sort_switch(self):
        if self.smart_sort_state:
            self.smart_sort_state = False
            self.switch_base_index(index_method="sort2base")
        else:
            self.smart_sort_state = True
            self.switch_base_index(index_method="base2sort")

    # 翻下一页
    def to_next_page(self):
        self.current_page += 1
        self.reset_layout()

    # 翻上一页
    def to_last_page(self):
        self.current_page -= 1
        self.reset_layout()

    # 本页面职位勾选投递
    def set_all_checked(self):
        for index in range(self.list_widget_show.count()):
            item_widget = self.list_widget_show.itemWidget(self.list_widget_show.item(index))
            item_widget.children()[-1].setChecked(True)

            unique_idx = self.row_idx2unq_idx.get(index, 0)
            if unique_idx in self.base_data_dict.keys():
                if self.base_data_dict[unique_idx]["是否投递"]:
                    self.base_data_dict[unique_idx]["是否投递"] = False
                else:
                    self.base_data_dict[unique_idx]["是否投递"] = True

    # 显示职位详情
    def show_job_detail(self, index):
        unique_id = self.row_idx2unq_idx.get(index)
        if unique_id is not None:
            job_show = ""

            job_resume_match_score = str(self.base_data_dict[unique_id].get("匹配指数", ""))
            job_tag_info = self.base_data_dict[unique_id].get("职位特征", "")
            job_detail = self.base_data_dict[unique_id]["职位描述"]

            if job_resume_match_score:
                job_show += "该职位与您的简历匹配得分：" + job_resume_match_score + "\n"
            if job_tag_info:
                job_show += "职位特征：" + job_tag_info + "\n"
            job_show = job_show + job_detail

            self.job_detail.children()[-1].setPlainText(job_show)

    # 删除职位
    def delete_row(self, index):
        if index in self.base_data_dict.keys():
            self.base_data_dict.pop(index)
        self.reset_layout()

    # 职位勾选投递
    def mark4throw(self):
        check_box = self.sender()
        index = check_box.get_unique_id()
        # self.set_log_stream("state changed for data %s" % index)

        if index in self.base_data_dict.keys():
            if self.base_data_dict[index]["是否投递"]:
                self.base_data_dict[index]["是否投递"] = False
            else:
                self.base_data_dict[index]["是否投递"] = True

    # 开始投递
    def start_throw(self):
        if self.working:
            self.set_log_stream("小助手：请稍等哦，还有抓取任务正在运行")
            return

        self.working = True
        mission_dict = {"mission_detail": [], "login_info": dict()}
        id_mark4removal = []
        for job_unique_id, job_content in self.base_data_dict.items():
            job_source = job_content["职位来源"]
            job_url = job_content["职位唯一标识"]
            job_name = job_content["职位名称"]
            job_ready = job_content["是否投递"]
            if job_ready:
                id_mark4removal.append(job_unique_id)
                mission_dict["mission_detail"].append([job_name, job_url, job_source])
                if job_source not in mission_dict["login_info"].keys():
                    mission_dict["login_info"][job_source] = self.orig_settings[job_source]["登陆页面"]

        # 删除已经投递的职位内容
        for job_unique_id in id_mark4removal:
            self.base_data_dict.pop(job_unique_id)

        # 刷新职位编辑窗口
        self.current_page = 1
        self.reset_layout()

        # 启动投递线程
        if mission_dict["mission_detail"]:
            self.set_log_stream("小助手：投递程序正式开始！")
            self.throw_thread.give_order(mission_dict, self.switchboard)
            self.throw_thread.start()
            self.set_tutorial("throw")
        else:
            self.set_log_stream("小助手：您还没有加载投递任务哦~")

    # 登陆确认
    def login_confirm(self):
        if self.switchboard["confirm_permission"]:
            self.switchboard["confirm_permission"] = False
            self.switchboard["wait_login"] = False

    # 更新进度条
    def set_progress(self, pnumber):
        self.progress.setValue(pnumber)

    # 小助手信息通知触发事件
    def set_log_stream(self, msg):
        self.helper.list_widget_log.addItem(msg)
        if len(self.helper.list_widget_log) > 40:
            self.helper.list_widget_log.takeItem(0)

    # 教程信息通知触发事件
    def set_tutorial(self, last_action):
        self.helper.renew_tutorial(last_action)

    # ################################ 隐藏函数 ################################
    # 重新加载布局
    def reload_layout(self):
        # 初始化各种控件
        self.list_widget_show = QtGui.QListWidget()
        self.job_detail = JobDetailWindow()
        self.read_button = QuickInterface.gen_default_button("读取职位")
        self.read_resume_button = QuickInterface.gen_default_button("读取简历")
        self.smart_sort_checkbox = QtGui.QCheckBox("职位智能排序")

        self.next_page = QuickInterface.gen_default_button("下一页")
        self.last_page = QuickInterface.gen_default_button("上一页")

        self.set_all_button = QuickInterface.gen_default_button("全选本页职位")
        self.throw_button = QuickInterface.gen_default_button("投递职位")
        self.login_confirm_button = QuickInterface.gen_default_button("登陆确认")
        self.progress = QtGui.QProgressBar()

        # 绑定按钮事件
        self.read_button.clicked.connect(self.to_front_page)
        self.read_resume_button.clicked.connect(self.read_resume)
        self.smart_sort_checkbox.clicked.connect(self.smart_sort_switch)

        self.next_page.clicked.connect(self.to_next_page)
        self.last_page.clicked.connect(self.to_last_page)

        self.set_all_button.clicked.connect(self.set_all_checked)
        self.throw_button.clicked.connect(self.start_throw)
        self.login_confirm_button.clicked.connect(self.login_confirm)
        self.list_widget_show.currentRowChanged.connect(self.show_job_detail)

        # 初始化布局，呈现视图
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.read_button)
        layout.addWidget(self.read_resume_button)
        layout.addWidget(self.smart_sort_checkbox)
        layout.addWidget(self.list_widget_show)

        if self.smart_sort_state:
            self.smart_sort_checkbox.setChecked(True)
        else:
            self.smart_sort_checkbox.setChecked(False)

        # 判断是否加载上一页或者下一页按钮
        if self.current_page != 1:
            layout.addWidget(self.last_page)
        if len(self.base_data_dict.keys()) > self.current_page * self.page_size:
            layout.addWidget(self.next_page)

        layout.addWidget(self.job_detail)
        layout.addWidget(self.set_all_button)
        layout.addWidget(self.throw_button)
        layout.addWidget(self.login_confirm_button)
        layout.addWidget(self.progress)

        self.setLayout(layout)
        self.reload_job_table()

    # 重启布局
    def reset_layout(self):
        # 清除当前id映射表
        self.row_idx2unq_idx = dict()

        # 递归清除当前视图
        current_layout = self.layout()
        self.list_widget_show.clear()
        QtGui.QWidget().setLayout(current_layout)

        # 重新加载布局
        self.reload_layout()

    # 重新读取基础职位数据
    def reload_base_data_dict(self):
        if self.helper.stack_mission_editor.working:
            self.set_log_stream("小助手：请稍等哦，还有抓取任务正在运行")
            return
        egg_count = 0
        tmp_buckets = []

        for worker in self.helper.stack_mission_editor.workers:
            tmp_buckets.append([])
            for egg in worker.get_eggs():
                tmp_buckets[-1].append(egg)

        if not tmp_buckets:
            self.set_log_stream("小助手：还没有抓取任何职位哦~")
            return

        bucket_max_size = max([len(bucket) for bucket in tmp_buckets])
        if bucket_max_size > 0:
            self.base_data_dict = dict()
            self.unique_job_set = set()
            # print("There are %s buckets, biggest bucket size %s" % (len(tmp_buckets), bucket_max_size))
            for idx in range(bucket_max_size):
                for bucket in tmp_buckets:
                    if idx < len(bucket):
                        unique_job = bucket[idx]["职位唯一标识"]    # 不允许重复的职位出现
                        if unique_job not in self.unique_job_set:
                            self.base_data_dict[egg_count] = bucket[idx]
                            self.base_data_dict[egg_count]["职位ID"] = egg_count
                            self.gen_content_vector(self.base_data_dict[egg_count])
                            egg_count += 1

            # 职位内容加载完成后，清除WORKER中抓取到的职位内容
            for worker in self.helper.stack_mission_editor.workers:
                worker.empty_bucket()

            # 重新生成排序信息
            self.sort_id2base_id = dict()
            self.base_id2sort_id = dict()
            self.gen_sort_info()

    # 重新加载职位可视化列表
    def reload_job_table(self):
        row_index = 0
        unique_id_list = list(self.base_data_dict.keys())
        start_point = (self.current_page - 1) * self.page_size
        for unique_id in unique_id_list[start_point:start_point + self.page_size]:
            self.load_list_item(row_index, unique_id)
            row_index += 1

    # 加载单个职位元素
    def load_list_item(self, row_index, unique_id):
        # 初始化变量
        self.row_idx2unq_idx[row_index] = unique_id
        job_name = self.base_data_dict[unique_id]["职位名称"]
        job_source = self.base_data_dict[unique_id]["职位来源"]
        job_url = self.base_data_dict[unique_id]["职位唯一标识"]

        # 初始化窗口元素
        list_item = QtGui.QListWidgetItem()
        widget = QtGui.QWidget()

        # 初始化职位元素标题
        if job_url in self.throw_history:
            widget_job_name = QuickInterface.gen_red_label(job_name)
        else:
            widget_job_name = QtGui.QLabel(job_name)
        widget_job_source = QtGui.QLabel(job_source)
        widget_check_box = MyCheckBox("选择投递", unique_id)
        widget_remove_button = QuickInterface.gen_default_button("删除")

        # 设置窗口元素大小
        widget_job_name.setFixedSize(300, 20)
        widget_job_source.setFixedSize(100, 20)

        # 绑定按键时间
        self.connect(widget_remove_button, QtCore.SIGNAL("clicked()"),
                     lambda who=unique_id: self.delete_row(who))
        widget_check_box.clicked.connect(self.mark4throw)

        # 其他特殊事务
        if self.base_data_dict[unique_id]["是否投递"]:
            widget_check_box.setChecked(True)

        # 初始化布局
        widget_layout = QtGui.QHBoxLayout()
        widget_layout.addWidget(widget_job_name)
        widget_layout.addWidget(widget_job_source)
        widget_layout.addWidget(widget_remove_button)
        widget_layout.addWidget(widget_check_box)
        widget_layout.addStretch()
        widget_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        widget.setLayout(widget_layout)
        list_item.setSizeHint(widget.sizeHint())
        self.list_widget_show.addItem(list_item)
        self.list_widget_show.setItemWidget(list_item, widget)

    def switch_base_index(self, index_method="base2sort"):
        if not self.sort_id2base_id:
            self.set_log_stream("小助手：排序需要您同时提供简历和职位哦")
            return
        if index_method == "base2sort":
            tmp_data_dict = dict()
            for key, value in self.base_data_dict.items():
                sort_id = self.base_id2sort_id[key]
                tmp_data_dict[sort_id] = value
            self.base_data_dict = tmp_data_dict
            self.current_page = 1
            self.reset_layout()
        elif index_method == "sort2base":
            tmp_data_dict = dict()
            for key, value in self.base_data_dict.items():
                base_id = self.sort_id2base_id[key]
                tmp_data_dict[base_id] = value
            self.base_data_dict = tmp_data_dict
            self.current_page = 1
            self.reset_layout()

    def gen_content_vector(self, element):
        try:
            content = element["职位描述"]
            content_keyword_dict = self.content_preproc.gen_words(content)
            sorted_tags = sorted(content_keyword_dict.items(), key=lambda tup: tup[1], reverse=True)
            tag_detail = ','.join([tag_detail[0] for tag_detail in sorted_tags])
            _, doc_vector_str = self.content_classifier.classify(content_keyword_dict)
            element["职位向量"] = doc_vector_str
            element["职位特征"] = tag_detail
        except:
            pass

    def gen_sort_info(self):
        # 重新计算排序得分之前，要确保内容词典unique_id复原
        if self.smart_sort_state:
            self.smart_sort_state = False
            self.smart_sort_checkbox.setChecked(False)
            self.switch_base_index(index_method="sort2base")

        if self.resume_info and self.base_data_dict:
            resume_vector_str = self.resume_info.get("职位向量")
            self.sort_id2base_id = dict()
            self.base_id2sort_id = dict()
            if resume_vector_str is None:
                for unique_id in self.base_data_dict.keys():
                    self.sort_id2base_id[unique_id] = unique_id
                    self.base_id2sort_id[unique_id] = unique_id
            else:
                for unique_id in self.base_data_dict.keys():
                    job_info = self.base_data_dict[unique_id]
                    job_vector_str = job_info.get("职位向量")

                    if job_vector_str is not None:
                        job_vector = string2vector(job_vector_str)
                        resume_vector = string2vector(resume_vector_str)
                        score = simm(job_vector, resume_vector)
                        self.base_data_dict[unique_id]["匹配指数"] = score
                    else:
                        self.base_data_dict[unique_id]["匹配指数"] = 0.0
                jobs_sorted_by_score = sorted(self.base_data_dict.values(), key=lambda d: d["匹配指数"], reverse=True)
                for job_idx in range(len(jobs_sorted_by_score)):
                    job_base_id = jobs_sorted_by_score[job_idx]["职位ID"]
                    self.sort_id2base_id[job_idx] = job_base_id
                    self.base_id2sort_id[job_base_id] = job_idx


class JobDetailWindow(QtGui.QWidget):
    def __init__(self, input_text=""):
        super(JobDetailWindow, self).__init__()
        log_output = QtGui.QTextEdit()
        log_output.setReadOnly(True)
        log_output.setLineWrapMode(QtGui.QTextEdit.NoWrap)

        font = log_output.font()
        font.setFamily("Courier")
        font.setPointSize(10)

        log_output.moveCursor(QtGui.QTextCursor.End)
        log_output.setCurrentFont(font)

        log_output.setPlainText(input_text)

        sb = log_output.verticalScrollBar()
        sb.setValue(sb.maximum())

        widget_layout = QtGui.QHBoxLayout()
        widget_layout.addWidget(log_output)
        self.setLayout(widget_layout)


class MyCheckBox(QtGui.QCheckBox):
    def __init__(self, text, unique_id):
        super(MyCheckBox, self).__init__(text)
        self.unique_id = unique_id

    def get_unique_id(self):
        return self.unique_id


class ThrowWorker(QtCore.QThread):
    def __init__(self, editor, orig_settings):
        QtCore.QThread.__init__(self)
        self.editor = editor
        self.mission = dict()
        self.orig_settings = orig_settings
        self.switchboard = dict()
        self.progress_step = 0

    def give_order(self, mission, switchboard):
        self.mission = mission
        self.switchboard = switchboard
        self.progress_step = len(self.mission["mission_detail"])
        self.progress_step = 100/self.progress_step

    def clear_order(self):
        self.mission = dict()
        self.switchboard = dict()
        self.progress_step = 0
        self.editor.working = False
        write_data2json(list(self.editor.throw_history), RESUME_HISTORY)

    def run(self):
        handler = ResumeThrower(self.mission, self.orig_settings, self.switchboard)
        summation = 0.0
        for msg_info in handler.run():
            msg_cat = msg_info[0]
            msg_content = msg_info[1]
            if len(msg_info) == 3:
                msg_detail = msg_info[2]
                self.editor.throw_history.add(msg_detail["url"])
            self.emit(QtCore.SIGNAL('log'), msg_content)
            if msg_cat == "progress":
                summation += self.progress_step
                self.emit(QtCore.SIGNAL('progress'), summation)
        self.clear_order()


"""
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = JobEditor()
    window.resize(720, 960)
    window.show()
    sys.exit(app.exec_())
"""