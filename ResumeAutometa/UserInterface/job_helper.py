import sys
from PyQt4.QtGui import *
from ResumeAutometa.UserInterface.mission_editor import MissionEditor
from ResumeAutometa.UserInterface.job_editor import JobEditor
from ResumeAutometa.UserInterface.utils import QuickInterface, get_chrome_path
from ResumeAutometa.UserInterface.utils import TUTORIAL_INFO
from ResumeAutometa.Config.file_paths import CRAWL_JOB_TOTEM, THROW_RESUME_TOTEM, MAIN_TOTEM, CHROME_WEBDRIVER_PATH_FILE


class JobHelper(QWidget):

    def __init__(self):
        super(JobHelper, self).__init__()
        self.tutorial = False

        try:
            # 子模块初始化
            _ = get_chrome_path(CHROME_WEBDRIVER_PATH_FILE)
            self.stack_mission_editor = MissionEditor(self)
            self.stack_job_editor = JobEditor(self)

            self.Stack = QStackedWidget(self)
            self.Stack.addWidget(self.stack_mission_editor)
            self.Stack.addWidget(self.stack_job_editor)

            # 主窗口布局初始化
            hgrid = QGridLayout(self)
            hgrid.setSpacing(10)

            # 添加主窗口按钮
            icon_job_scrap = QIcon(CRAWL_JOB_TOTEM)
            self.button_job_scrap = QuickInterface.gen_default_button('我要抓职位')
            self.button_job_scrap.setIcon(icon_job_scrap)

            icon_resume_throw = QIcon(THROW_RESUME_TOTEM)
            self.button_resume_throw = QuickInterface.gen_default_button('我要投简历')
            self.button_resume_throw.setIcon(icon_resume_throw)

            self.button_tutorial_switch = QuickInterface.gen_default_button('打开教程')

            self.button_job_scrap.clicked.connect(lambda: self.display(0))
            self.button_resume_throw.clicked.connect(lambda: self.display(1))
            self.button_tutorial_switch.clicked.connect(self.hide_helper)
        except Exception as e:
            print("初始化失败，错误%s, 请检查文件格式是否损坏!" % str(e))
            sys.exit(-1)

        hgrid.addWidget(self.button_job_scrap, 0, 0)
        hgrid.addWidget(self.button_resume_throw, 1, 0)
        hgrid.addWidget(self.button_tutorial_switch, 2, 0)

        # 添加子模块
        hgrid.addWidget(self.Stack, 0, 1, 5, 1)

        # 添加小助手窗口
        self.list_widget_log = QListWidget()
        hgrid.addWidget(self.list_widget_log, 3, 0)

        # 添加教程窗口
        self.tutorial_content = QTextEdit()
        self.tutorial_content.setReadOnly(True)
        self.tutorial_content.setLineWrapMode(QTextEdit.NoWrap)

        font = self.tutorial_content.font()
        font.setFamily("Courier")
        font.setPointSize(10)

        self.tutorial_content.moveCursor(QTextCursor.End)
        self.tutorial_content.setCurrentFont(font)
        self.tutorial_content.setPlainText(TUTORIAL_INFO["init"])

        sb = self.tutorial_content.verticalScrollBar()
        sb.setValue(sb.maximum())
        hgrid.addWidget(self.tutorial_content, 4, 0)
        self.tutorial_content.hide()

        # 启动主窗口程序
        self.setLayout(hgrid)
        self.setGeometry(500, 500, 1000, 500)
        self.setWindowTitle('简历投递小助手')
        self.setWindowIcon(QIcon(MAIN_TOTEM))
        self.show()

    def display(self, i):
        if i == 1:
            self.renew_tutorial("load")
        self.Stack.setCurrentIndex(i)

    def renew_tutorial(self, last_action):
        tutorial_content = TUTORIAL_INFO[last_action]
        self.tutorial_content.setPlainText(tutorial_content)

    def hide_helper(self):
        if self.tutorial:
            self.tutorial = False
            self.button_tutorial_switch.setText("打开教程")
            self.tutorial_content.hide()
        else:
            self.tutorial = True
            self.button_tutorial_switch.setText("关闭教程")
            self.tutorial_content.show()


def main():
    app = QApplication(sys.argv)
    ex = JobHelper()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()