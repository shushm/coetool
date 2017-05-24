# -*- coding: utf-8 -*-

"""
Doc...

"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
import tempfile
from coetoolcore import *


class CoetoolGui(QMainWindow):
    def __init__(self):
        super(CoetoolGui, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0

        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        
        hbox = QHBoxLayout()
        
        self.leftTxt = QTextEdit()
        self.leftTxt.setFontFamily('Courier')
        self.leftTxt.setReadOnly(1)
        self.rightImg = self.scrollArea

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.leftTxt)
        splitter.addWidget(self.rightImg)
        splitter.setSizes([400, 400])
               
        hbox.addWidget(splitter)
        QApplication.setStyle(QStyleFactory.create('Cleanlooks'))
        
        self.setCentralWidget(splitter)
        
        self.setWindowTitle("coetool")
        self.statusBar().showMessage('coetool loaded...')
            
        self.resize(800, 500)

        self.createActions()
        self.createMenus()

    def open(self):

        fileName, _ = QFileDialog.getOpenFileName(self, "Open file",
                QDir.currentPath())
        
        if fileName:
            self.setWindowTitle("coetool - "+fileName)
            self.statusBar().showMessage(fileName+' loaded')
            
            if QFileInfo(fileName).suffix() == 'coe':
                
                self.conversion = CoeConverter(fileName)
                
                with open(fileName, encoding='utf-8') as coefile:
                    contents = coefile.read()
                    self.leftTxt.setPlainText(contents)
                
                self.imageLabel.setPixmap(QPixmap.fromImage(self.conversion.img))
                self.scaleFactor = 1.0

                self.printAct.setEnabled(True)
                self.fitToWindowAct.setEnabled(True)
                self.updateActions()
                self.saveImgAct.setEnabled(True)
                        
                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()
            
            else:
            
                image = QImage(fileName)  
                if image.isNull():        
                    QMessageBox.information(self, "coetool",
                            "Cannot load %s." % fileName)
                    return
                
                self.statusBar().showMessage(fileName+' loaded')  #
                self.imageLabel.setPixmap(QPixmap.fromImage(image))
                self.scaleFactor = 1.0

                self.printAct.setEnabled(True)
                self.fitToWindowAct.setEnabled(True)
                self.updateActions()
                self.saveCoeAct.setEnabled(True)
                
                if not self.fitToWindowAct.isChecked():
                    self.imageLabel.adjustSize()
                
                tmpcoe = tempfile.NamedTemporaryFile(suffix='.coe', delete=False)
                tmpcoe.close()
                self.conversion = CoeConverter(fileName)
                self.conversion.createCoe(tmpcoe.name)
                
                with open(tmpcoe.name, encoding='utf-8') as coefile:
                    contents = coefile.read()
                    self.leftTxt.setPlainText(contents)
                
                

    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()
    
    def saveCoe(self):
        coefilename, filter = QFileDialog.getSaveFileName(self, 'Save .coe file',
                QDir.currentPath(), 'COE file (*.coe)')
        self.conversion.createCoe(coefilename+'.coe')
        self.statusBar().showMessage(coefilename+'.coe written to disk')
    
    def saveImg(self):
        filters='BMP image (*.bmp);;JPG image (*.jpg);; PNG image (*.png)'
        imgfilename, selected_filter = QFileDialog.getSaveFileName(self, 'Save image file',
                QDir.currentPath(),filters )
        ext = (selected_filter.split()[0].lower())
        self.conversion.exportImg(imgfilename+'.'+ext, ext)
        self.statusBar().showMessage(imgfilename+'.'+ext+' written to disk')
    
    def about(self):
        QMessageBox.about(self, "About coetool",
                "<p><b>coetool</b> is a cli or gui program to convert "
                "from .coe files (VGA memory map) to image files "
                "and the other way around, load an image and generate .coe file.</p> "
                "<p>Also it is possible to zoom images, export and view raw bytes.</p>"
                "<p>jaXvi - april 2014 </p>")

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)

        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)
        
        self.saveCoeAct = QAction("Save .coe...", self, enabled=False, triggered=self.saveCoe)
        
        self.saveImgAct = QAction("Save image...", self, enabled=False, triggered=self.saveImg)
        
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl++",
                enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+-",
                enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+S",
                enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self, enabled=False,
                checkable=True, shortcut="Ctrl+F", triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveCoeAct)
        self.fileMenu.addAction(self.saveImgAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
        
    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 20.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.2)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    coetoolgui = CoetoolGui()
    coetoolgui.show()
    sys.exit(app.exec_())
