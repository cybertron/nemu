from PyQt4.QtGui import *

class ListWidget(QScrollArea):
   def __init__(self, parent = None):
      QScrollArea.__init__(self, parent)
      self.widget = QWidget() # Just adding the layout directly doesn't work right, so wrap it in a QWidget
      self.setWidget(self.widget)
      self.setWidgetResizable(True)
      self.createLayout()
      
      
   def createLayout(self):
      self.layout = QVBoxLayout(self.widget)
      self.layout.setSpacing(0)
      self.layout.setContentsMargins(0, 0, 0, 0)
      self.layout.setSizeConstraint(QLayout.SetMinimumSize)

      
   def add(self, item):
      self.layout.addWidget(item)
      
   def clear(self):
      QWidget().setLayout(self.layout)
      self.createLayout()
      