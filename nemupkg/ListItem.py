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
      self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
      self.setMaximumHeight(75)
      
      
   def enterEvent(self, event):
      print "Enter"
      self.mouseOver = True
      
      
   def leaveEvent(self, event):
      print "Leave"
      if not self.ignoreLeave:
         self.mouseOver = False
      
   def mousePressEvent(self, event):
      if event.button() == Qt.RightButton:
         self.ignoreLeave = True
      
      