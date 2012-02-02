from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

class ListItem(QPushButton):
   def __init__(self, item, parent = None):
      QPushButton.__init__(self, parent)
      self.item = item
      self.mouseOver = False
      self.setText(item.name)
      self.setIcon(QIcon(item.icon))
      self.setIconSize(QSize(24, 24))
      self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
      self.setMaximumHeight(75)
      self.setMinimumHeight(35)
      self.setFont(QFont(self.font().family(), 12))
      self.setStyleSheet('text-align: left')
      
      
   def mousePressEvent(self, event):
      if event.button() == Qt.RightButton:
         self.mouseOver = True
      QPushButton.mousePressEvent(self, event)
      
      