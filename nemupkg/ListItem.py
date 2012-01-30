from PyQt4.QtGui import *
import os

class ListItem(QPushButton):
   def __init__(self, item, parent = None):
      QPushButton.__init__(self, parent)
      self.item = item
      self.setText(item.name)
      self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
      self.setMaximumHeight(75)
      
      self.clicked.connect(self.runCommand)
      
      
   def runCommand(self):
      os.system(self.item.command)
      