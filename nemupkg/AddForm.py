from PyQt4.QtGui import *

class AddForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.accepted = False
      self.mainLayout = QVBoxLayout(self)
      
      self.nameBox = QLineEdit()
      self.addPair('Name', self.nameBox)
      
      self.commandBox = QLineEdit()
      self.addPair('Command', self.commandBox)
      
      buttonLayout = QHBoxLayout()
      self.okButton = QPushButton('OK')
      self.okButton.clicked.connect(self.okClicked)
      buttonLayout.addWidget(self.okButton)
      
      self.cancelButton = QPushButton('Cancel')
      self.cancelButton.clicked.connect(self.close)
      buttonLayout.addWidget(self.cancelButton)
      
      self.mainLayout.addLayout(buttonLayout)
      
      
   def addPair(self, name, widget):
      tempLayout = QHBoxLayout()
      tempLayout.addWidget(QLabel(name))
      tempLayout.addWidget(widget)
      self.mainLayout.addLayout(tempLayout)
      
      
   def okClicked(self):
      self.accepted = True
      self.name = str(self.nameBox.text())
      self.command = str(self.commandBox.text())
      self.close()
      