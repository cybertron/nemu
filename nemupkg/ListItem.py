from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

class ListItem(QPushButton):
   def __init__(self, item, parent = None):
      QPushButton.__init__(self, parent)
      self.item = item
      self.mouseOver = False
      self.ignoreLeave = False
      self.setText(item.name)
      self.setIcon(QIcon(item.icon))
      self.setIconSize(QSize(32, 32))
      self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
      self.setMaximumHeight(75)
      self.setFont(QFont(self.font().family(), 12))
      
      
   def enterEvent(self, event):
      self.mouseOver = True
      
      
   def leaveEvent(self, event):
      if not self.ignoreLeave:
         self.mouseOver = False
      
   def mousePressEvent(self, event):
      if event.button() == Qt.RightButton:
         self.ignoreLeave = True
      QPushButton.mousePressEvent(self, event)
      
      