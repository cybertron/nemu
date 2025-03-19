from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QFont
import os
from .IconCache import *


class ListItem(QPushButton):
   iconCache = IconCache()
   def __init__(self, item, clearMouseOver, parent = None):
      QPushButton.__init__(self, parent)
      self.item = item
      self.clearMouseOver = clearMouseOver
      self.mouseOver = False
      self.setText(item.name)
      self.setIcon(ListItem.iconCache[item.icon])
      self.setIconSize(QSize(24, 24))
      self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
      self.setMaximumHeight(75)
      self.setMinimumHeight(35)
      self.setFont(QFont(self.font().family(), 12))
      self.setStyleSheet('text-align: left')
      self.setToolTip(item.name)
      
      
   def mousePressEvent(self, event):
      if event.button() == Qt.MouseButton.RightButton:
         self.clearMouseOver()
         self.mouseOver = True
      QPushButton.mousePressEvent(self, event)
      
      
      
