from PyQt4.QtGui import *
from PyQt4.QtCore import *
from MenuReader import *

class MainForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      
      self.setupUI()
      
      self.menuReader = MenuReader()
      
      self.show()
      
      
   def setupUI(self):
      self.resize(400, 400)
      self.setFocusPolicy(Qt.ClickFocus)
      
      self.listLayout = QHBoxLayout(self)
      self.listLayout.setSpacing(0)
      margin = 0
      self.listLayout.setContentsMargins(margin, margin, margin, margin)
      
      self.leftList = QListWidget()
      self.createMenu(self.leftList)
      self.leftList.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.listLayout.addWidget(self.leftList)
      
      self.rightList = QListWidget()
      self.listLayout.addWidget(self.rightList)
      
      
   def createMenu(self, widget):
      addAction = QAction("Add...", widget)
      addAction.triggered.connect(self.addClicked)
      widget.insertAction(None, addAction)
      editAction = QAction("Edit...", widget)
      editAction.triggered.connect(self.editClicked)
      widget.insertAction(None, editAction)
      deleteAction = QAction("Delete", widget)
      deleteAction.triggered.connect(self.deleteClicked)
      widget.insertAction(None, deleteAction)
      
      
   def changeEvent(self, event):
      if event.type() == QEvent.ActivationChange and not self.isActiveWindow():
         print "Lost focus"
         self.close()
         
         
   def addClicked(self):
      print "Add"
      
   def editClicked(self):
      print "Edit"
      
   def deleteClicked(self):
      print "Delete"
      
      