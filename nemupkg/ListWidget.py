from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLayout, QSizePolicy
from PyQt5.QtCore import Qt

class ListWidget(QScrollArea):
   def __init__(self, clearMouseOver, parent = None):
      QScrollArea.__init__(self, parent)
      self.clearMouseOver = clearMouseOver
      self.mouseOver = False
      
      self.widget = QWidget() # Just adding the layout directly doesn't work right, so wrap it in a QWidget
      self.setWidget(self.widget)
      self.setWidgetResizable(True)
      self.setMouseTracking(True)
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
      
   
   def mousePressEvent(self, event):
      if event.button() == Qt.RightButton:
         self.clearMouseOver()
         self.mouseOver = True
      QScrollArea.mousePressEvent(self, event)
      
