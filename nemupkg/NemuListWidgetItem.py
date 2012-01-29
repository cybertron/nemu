from PyQt4.QtGui import *

class NemuListWidgetItem(QListWidgetItem):
   def __init__(self, item, parent = None):
      QListWidgetItem.__init__(self, parent)
      self.command = item.command
      self.setText(item.name)