from PyQt4.QtGui import *

class ListWidget(QWidget):
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      self.createLayout()
      
      
   def createLayout(self):
      self.layout = QVBoxLayout(self)
      self.layout.setSpacing(0)
      self.layout.setContentsMargins(0, 0, 0, 0)

      
   def add(self, item):
      self.layout.addWidget(item)
      
   def clear(self):
      QWidget().setLayout(self.layout)
      self.createLayout()