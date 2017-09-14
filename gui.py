# -*- coding: utf-8 -*-
import sys

import numpy.core._methods 
import numpy.lib.format
import numpy as np

import cv2
import PyQt5.QtWidgets as gui
from PyQt5.QtGui import QPixmap

# 加工後の画像を表示
class SubWindow(gui.QDialog):
    def __init__(self, fname, parent):
        self.parent = parent
        gui.QDialog.__init__(self, parent)
        self.fname = fname
        
    def show(self):
        hbox = gui.QHBoxLayout(self)
        pixmap = QPixmap(self.fname)
        
        self.label = gui.QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setGeometry(160, 40, 80, 30)
        
        hbox.addWidget(self.label)
        self.setLayout(hbox)
        
        self.move(300, 200)
        self.setWindowTitle(self.fname)
        self.exec_()

# 画像を漫画風に加工
# https://algorithm.joho.info/programming/python/opencv-manga-filter-py/
class ProcessManga():
    def manga_filter(self, src, screen, th1=60, th2=150):
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        screen = cv2.resize(screen,(gray.shape[1],gray.shape[0]))
        
        edge = 255 - cv2.Canny(gray, 80, 120)
        gray[gray <= th1] = 0
        gray[gray >= th2] = 255
        gray[ np.where((gray > th1) & (gray < th2)) ] = screen[ np.where((gray > th1)&(gray < th2)) ]
        return cv2.bitwise_and(gray, edge)
	
    def run(self, fname, fname_scr, fname_mod):
        img = cv2.imread(fname) 
        screen = cv2.imread(fname_scr)
        manga = self.manga_filter(img, screen)
        cv2.imwrite(fname_mod, manga)

# ファイル選択画面
class MainWindow(gui.QWidget):
    def __init__(self, parent=None):
        gui.QMainWindow.__init__(self, parent)
        layout = gui.QGridLayout()
        form = gui.QFormLayout()
        
        # 入力画像とスクリーントーンのファイルを選択
        self.inputText = gui.QLineEdit()
        btnSepFile = gui.QPushButton(u'...')
        btnSepFile.setMaximumWidth(40)
        btnSepFile.clicked.connect(self.chooseDbFile)
        boxSepFile = gui.QHBoxLayout()
        boxSepFile.addWidget(self.inputText)
        boxSepFile.addWidget(btnSepFile)
        form.addRow(u'入力画像を選択', boxSepFile)
        
        self.inputTextScr = gui.QLineEdit()
        btnSepFileScr = gui.QPushButton(u'...')
        btnSepFileScr.setMaximumWidth(40)
        btnSepFileScr.clicked.connect(self.chooseDbFileScr)
        boxSepFileScr = gui.QHBoxLayout()
        boxSepFileScr.addWidget(self.inputTextScr)
        boxSepFileScr.addWidget(btnSepFileScr)
        form.addRow(u'スクリーントーンを選択', boxSepFileScr)
        
        # 実行ボタン
        boxCtrl = gui.QHBoxLayout()
        makeWindowButton = gui.QPushButton('実行')
        makeWindowButton.clicked.connect(self.makeWindow)
        boxCtrl.addWidget(makeWindowButton)
        
        layout.addLayout(form,0,0)
        layout.addLayout(boxCtrl,1,0)
        
        self.setLayout(layout)
        self.resize(300,100)
        
    def makeWindow(self):
        fname = self.inputText.text()
        fname_scr = self.inputTextScr.text()
        fname_mod = fname + '_mod.png'
        pm = ProcessManga()
        pm.run(fname, fname_scr, fname_mod)
        
        subWindow = SubWindow(fname_mod, parent=self)
        subWindow.show()
        
    def chooseDbFile(self):
        dialog = gui.QFileDialog()
        dialog.setFileMode(gui.QFileDialog.ExistingFile)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            for f in fileNames:
                self.inputText.setText(f)
                return
        return self.inputText.setText('')
    
    def chooseDbFileScr(self):
        dialog = gui.QFileDialog()
        dialog.setFileMode(gui.QFileDialog.ExistingFile)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            for f in fileNames:
                self.inputTextScr.setText(f)
                return
        return self.inputTextScr.setText('')
    
if __name__ == '__main__':
    app = gui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
