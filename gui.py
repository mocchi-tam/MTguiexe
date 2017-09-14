# -*- coding: utf-8 -*-
import os
import sys
import shutil

import numpy.core._methods 
import numpy.lib.format
import cv2
from pandas import DataFrame, Series

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QGridLayout
from PyQt5.QtWidgets import QFormLayout, QLineEdit, QFileDialog

tmp_dir = './tmp/'

class SubWindow(QDialog):
    def __init__(self, val, mfname, parent):
        self.parent = parent
        QDialog.__init__(self, parent)
        self.outdir = tmp_dir
        self.pos_x = [280,250,200,120,360,370,380,390,450]
        self.pos_y = [70,130,200,300,60,120,190,270,420]
        self.n_pos = len(self.pos_x)
        self.count = 0
        self.n_file = val
        self.fname = self.outdir + 'img' + str(self.count).zfill(4) + '.png'
        self.mfname = mfname + '.csv'
        self.tag = [0 for i in range(self.n_pos)]
        self.list = DataFrame(columns=[str(i) for i in range(self.n_pos+1)])
    
    def show(self):
        self.GUI()
        
    def GUI(self):
        # img
        hbox = QHBoxLayout(self)
        pixmap = QPixmap(self.fname)
        
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setGeometry(160, 40, 80, 30)
        
        but = []
        
        # forward
        butf = QPushButton('Next', self)
        butf.move(600, 0)
        butf.clicked[bool].connect(self.NextImg)
        
        # backward
        butb = QPushButton('Back', self)
        butb.move(10, 0)
        butb.clicked[bool].connect(self.PrevImg)
        
        # button 0
        for j in range(self.n_pos):
            but.append(QPushButton(str(j+1), self))
            but[j].setCheckable(True)
            but[j].resize(30,30)
            but[j].move(self.pos_x[j], self.pos_y[j])
            but[j].clicked[bool].connect(self.TableTouch)
        
        hbox.addWidget(self.label)
        self.setLayout(hbox)
        
        self.move(300, 200)
        self.setWindowTitle(self.fname)
        self.exec_()
        
    def TableTouch(self, pressed):
        source = self.sender()
        val = 1 if pressed else 0
        
        but_id = int(source.text())
        self.tag[but_id-1] = val
        print(but_id, val)
        
    def NextImg(self, pressed):
        print(self.tag)
        index = [self.count]
        index.extend(self.tag)
        se = Series(index, index=self.list.columns)
        self.list = self.list.append(se, ignore_index=True)
        
        self.count += 1
        self.showimg(self.count)
        
    def PrevImg(self, pressed):
        self.list = self.list.drop(len(self.list)-1)
        self.count -= 1
        self.showimg(self.count)

    def showimg(self, count):
        index = str(count).zfill(4)
        
        self.fname = self.outdir + 'img' + index + '.png'
        
        if not os.path.isfile(self.fname):
            print("end")
            self.list.to_csv(self.mfname, index=False)
            sys.exit()
        
        pixmap = QPixmap(self.fname)
        self.label.setPixmap(pixmap)
        
        self.setWindowTitle(self.fname)
    
    def closeEvent(self, event):
        print("close")
        self.list.to_csv(self.mfname, index=False)
        event.accept()

class ProcessMovie():
    def __init__(self, fname):
        self.fname = fname
        
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir, exist_ok=True)
        
    def finish(self):
        shutil.rmtree(tmp_dir)
        
    def run(self):
        mov = cv2.VideoCapture(self.fname)
        print('seccuessfully read file...', self.fname)
        i_frame = 0
        n_frame = 0
        
        while(True):
            ret, cap = mov.read()
            if ret == False:
                break
            
            if i_frame%(29) == 0:
                print(n_frame)
                img = cap
                img = cv2.resize(img, (720,480))
                fname = tmp_dir + 'img' + str(n_frame).zfill(4) + '.png'
                cv2.imwrite(fname, img)
                
                n_frame += 1
                
            i_frame += 1
        
        if n_frame == 0:
            raise Exception
            
        print('process finished')
        return n_frame
        
class MainWindow(QWidget):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        layout = QGridLayout()
        form = QFormLayout()
        
        self.inputText = QLineEdit()
        btnSepFile = QPushButton(u'...')
        btnSepFile.setMaximumWidth(40)
        btnSepFile.clicked.connect(self.chooseDbFile)
        boxSepFile = QHBoxLayout()
        boxSepFile.addWidget(self.inputText)
        boxSepFile.addWidget(btnSepFile)
        form.addRow(u'入力動画を選択', boxSepFile)
        
        boxCtrl = QHBoxLayout()
        makeWindowButton = QPushButton('実行')
        makeWindowButton.clicked.connect(self.makeWindow)
        boxCtrl.addWidget(makeWindowButton)
        
        layout.addLayout(form,0,0)
        layout.addLayout(boxCtrl,1,0)
        
        self.setLayout(layout)
        self.resize(300,100)
        
    def makeWindow(self):
        string = self.inputText.text()
        pm = ProcessMovie(string)
        self.mfname = string
        
        try:
            val = pm.run()
            print('successfully read file')
            subWindow = SubWindow(val, self.mfname, parent=self)
            subWindow.show()
        except:
            print('movie file does not exist!')
        finally:
            pm.finish()
            
    def chooseDbFile(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            for f in fileNames:
                self.inputText.setText(f)
                return
        return self.inputText.setText('')
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    sys.exit(app.exec_())
