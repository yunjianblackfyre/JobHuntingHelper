#!/usr/bin/python
#-*- coding:utf-8 -*-

import sys, os
from PyQt4 import QtGui, QtCore


class MediaFeed(QtGui.QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)

        menu = QtGui.QMenu()

        aboutAction = menu.addAction("About")
        aboutAction.triggered.connect(self.aboutMenu)

        exitAction = menu.addAction("Exit")
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.setContextMenu(menu)
        self.activated.connect(self.systemIcon)

    def aboutMenu(self):
        print("This should be some information.")

    def systemIcon(self, reason):
        w = QtGui.QWidget()
        if reason == QtGui.QSystemTrayIcon.Trigger:
            print("Clicked.")
            w.show()


def main():
    app = QtGui.QApplication(sys.argv)
    mediaFeed = MediaFeed(QtGui.QIcon("icons/venom.jpg"), None)

    mediaFeed.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
