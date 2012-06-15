from PyQt4.QtGui import *
import os

class AddForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.accepted = False
      self.mainLayout = QVBoxLayout(self)
      
      self.nameBox = QLineEdit()
      self.addPair('Name', self.nameBox)
      
      self.commandBox = QLineEdit()
      commandBrowse = QPushButton('Browse')
      commandBrowse.clicked.connect(self.commandBrowseClicked)
      self.addTriple('Command', self.commandBox, commandBrowse)
      
      self.workingBox = QLineEdit()
      self.addPair('Working Directory', self.workingBox)
      
      self.iconBox = QLineEdit()
      iconSelect = QPushButton('Select')
      iconSelect.clicked.connect(self.iconSelectClicked)
      self.addTriple('Icon', self.iconBox, iconSelect)
      
      self.folderCheck = QCheckBox('Folder')
      self.mainLayout.addWidget(self.folderCheck)
      
      buttonLayout = QHBoxLayout()
      self.okButton = QPushButton('OK')
      self.okButton.clicked.connect(self.okClicked)
      buttonLayout.addWidget(self.okButton)
      
      self.cancelButton = QPushButton('Cancel')
      self.cancelButton.clicked.connect(self.close)
      buttonLayout.addWidget(self.cancelButton)
      
      self.mainLayout.addLayout(buttonLayout)
      
      self.resize(400, 100)
      
      
   def addPair(self, name, widget):
      tempLayout = QHBoxLayout()
      tempLayout.addWidget(QLabel(name))
      tempLayout.addWidget(widget)
      self.mainLayout.addLayout(tempLayout)
      
      
   def addTriple(self, name, first, second):
      tempLayout = QHBoxLayout()
      tempLayout.addWidget(QLabel(name))
      tempLayout.addWidget(first)
      tempLayout.addWidget(second)
      self.mainLayout.addLayout(tempLayout)
      
      
   def okClicked(self):
      self.accepted = True
      self.name = str(self.nameBox.text())
      self.command = str(self.commandBox.text())
      self.working = str(self.workingBox.text())
      self.folder = self.folderCheck.isChecked()
      self.icon = str(self.iconBox.text())
      self.close()
      
      
   def commandBrowseClicked(self):
      filename = QFileDialog.getOpenFileName()
      self.commandBox.setText(filename)
      
      
   def iconSelectClicked(self):
      startDir = '/usr/share/icons'
      if self.iconBox.text() != '':
         startDir = os.path.dirname(str(self.iconBox.text()))
      filename = QFileDialog.getOpenFileName(directory = startDir)
      if filename != '':
         self.iconBox.setText(filename)

      
   def populateFields(self):
      self.nameBox.setText(self.name)
      self.commandBox.setText(self.command)
      self.workingBox.setText(self.working)
      self.folderCheck.setChecked(self.folder)
      self.iconBox.setText(self.icon)
      