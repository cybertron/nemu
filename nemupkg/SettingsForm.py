from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
from MenuReader import *
from MenuItem import *

class SettingsForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.parent = parent
      self.accepted = False
      
      self.setupUI()
      
      
   def setupUI(self):
      self.setWindowTitle('Nemu Settings')
      self.mainLayout = QVBoxLayout(self)
      
      self.tabs = QTabWidget(self)
      self.mainLayout.addWidget(self.tabs)
      
      importPage = QWidget()
      importPageLayout = QVBoxLayout(importPage)
      self.importFileText = QLineEdit()
      self.importFileSelect = QPushButton('System')
      self.importFileSelect.clicked.connect(self.importSelectClicked)
      self.importFileUser = QPushButton('User')
      self.importFileUser.clicked.connect(self.importUserClicked)
      self.addWidgets(importPageLayout, 'Menu File', [self.importFileText, self.importFileSelect, self.importFileUser])
      
      themes = self.getIconThemes()
      self.themeCombo = QComboBox()
      self.themeCombo.addItems(themes)
      self.themeCombo.setToolTip('Use icons from this theme if possible')
      self.addWidgets(importPageLayout, 'Preferred Icon Theme', [self.themeCombo])
      
      self.replaceCheck = QCheckBox('Replace Existing')
      self.replaceCheck.setToolTip('Replace current menu with imported one - otherwise the imported menu will be merged')
      importPageLayout.addWidget(self.replaceCheck)
      
      self.importButton = QPushButton('Import')
      self.importButton.clicked.connect(self.importClicked)
      importPageLayout.addWidget(self.importButton)
      
      self.importProgress = QProgressBar()
      importPageLayout.addWidget(self.importProgress)
      
      self.importStatus = QLabel()
      self.importStatus.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
      importPageLayout.addWidget(self.importStatus)
      
      aboutPage = QWidget()
      aboutPageLayout = QVBoxLayout(aboutPage)
      aboutText = QTextEdit()
      aboutText.setAlignment(Qt.AlignCenter)
      aboutText.append('Nemu\n')
      aboutText.append('Copyright 2012 Ben Nemec\n')
      aboutText.append("Distributed under the GPLv3\n")
      aboutText.append("Web: TBD\n")
      aboutText.append("E-Mail: cybertron@nemebean.com\n")
      aboutText.setReadOnly(True)
      aboutPageLayout.addWidget(aboutText)
      
      self.tabs.addTab(importPage, 'Import Menu')
      self.tabs.addTab(aboutPage, 'About')
      
      self.bottomButtonLayout = QHBoxLayout()
      self.okButton = QPushButton('OK')
      self.okButton.clicked.connect(self.okClicked)
      self.bottomButtonLayout.addWidget(self.okButton)
      
      self.cancelButton = QPushButton('Cancel')
      self.cancelButton.clicked.connect(self.close)
      self.bottomButtonLayout.addWidget(self.cancelButton)
      
      self.mainLayout.addLayout(self.bottomButtonLayout)
      
      self.resize(500, 250)
      
      
   def addWidgets(self, layout, name, widgets):
      tempLayout = QHBoxLayout()
      tempLayout.addWidget(QLabel(name))
      for i in widgets:
         tempLayout.addWidget(i)
      layout.addLayout(tempLayout)
      
      
   def okClicked(self):
      self.accepted = True
      self.close()
      
      
   def importSelectClicked(self):
      filename = QFileDialog.getOpenFileName(directory = '/etc/xdg/menus')
      if filename != '':
         self.importFileText.setText(filename)
         
   def importUserClicked(self):
      filename = QFileDialog.getOpenFileName(directory = os.path.expanduser('~/.config/menus'))
      if filename != '':
         self.importFileText.setText(filename)
         
         
   def getIconThemes(self):
      retval = ['']
      for i in os.listdir('/usr/share/icons'):
         currPath = os.path.join('/usr/share/icons', i)
         if os.path.isdir(currPath):
            cursor = False
            for j in os.listdir(currPath):
               if j == 'cursors':
                  cursor = True
            if not cursor:
               retval.append(i)
            
      return retval
      
      
   def importClicked(self):
      if self.replaceCheck.isChecked():
         answer = QMessageBox.warning(self, 'Are you sure?', 'This action will erase your current menu.  Continue?', QMessageBox.Yes | QMessageBox.No)
         if answer != QMessageBox.Yes:
            return
            
      # Our due diligence done, it's time to do the import
      MenuItem.iconTheme = str(self.themeCombo.currentText())
      filename = str(self.importFileText.text())
      directory = os.path.join(os.path.dirname(filename), 'applications-merged')
      applicationsMerged = []
      if os.path.isdir(directory):
         applicationsMerged = os.listdir(directory)
         applicationsMerged[:] = [i for i in applicationsMerged if i.endswith('.menu')]
         applicationsMerged[:] = [os.path.join(directory, i) for i in applicationsMerged]
      files = [filename] + applicationsMerged
      
      workingItems = []
      for f in files:
         self.importStatus.setText('Importing ' + f)
         qApp.processEvents()
         reader = MenuReader(f)
         newItems = reader.menuItems
         self.removeEmptyFolders(newItems)
         
         self.mergeMenus(workingItems, newItems)
            
      if self.replaceCheck.isChecked():
         self.parent.menuItems = workingItems
      else:
         self.mergeMenus(self.parent.menuItems, workingItems)
         
      # Looking for icons is slow - just do it once
      self.importStatus.setText('Loading icons')
      self.importProgress.setRange(0, len(self.parent.menuItems))
      count = 0
      for i in self.parent.menuItems:
         self.importProgress.setValue(count)
         i.findIcon()
         count += 1
      self.importStatus.setText('Done')
      self.importProgress.setValue(len(self.parent.menuItems))
         
      self.parent.refresh()
      
      
   def removeEmptyFolders(self, items):
      removed = True
      while removed:
         toRemove = []
         removed = False
         for i in items:
            if i.folder:
               empty = True
               for j in items:
                  if j.parent == i:
                     empty = False
                     break
               if empty:
                  toRemove.append(i)
                  removed = True
         items[:] = [i for i in items if i not in toRemove]
                  
      
      
   def mergeMenus(self, items, mergeItems):
      parentMap = dict()
      for i in mergeItems:
         if i.parent in parentMap:
            i.parent = parentMap[i.parent]
         dup = None
         for j in items:
            if self.checkDup(i, j):
               dup = j
               break
         if dup == None:
            items.append(i)
         else:
            parentMap[i] = dup
            
            
   def checkDup(self, i, j):
      if i.name == j.name:
         iParent = i.parent
         jParent = j.parent
         while iParent != None and jParent != None and iParent.name == jParent.name:
            iParent = iParent.parent
            jParent = jParent.parent
         if iParent == None and jParent == None:
            return True
      return False
      