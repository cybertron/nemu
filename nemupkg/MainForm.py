from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pickle
import os
from MenuReader import *
from AddForm import *
from MenuItem import *
from ListWidget import *
from ListItem import *

class MainForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.holdOpen = False
      self.menuItems = []
      self.currentItem = None
      
      self.configDir = os.path.expanduser('~/.nemu')
      if not os.path.isdir(self.configDir):
         os.mkdir(self.configDir)
      self.menuFile = os.path.expanduser('~/.nemu/menu')
      if os.path.exists(self.menuFile):
         with open(self.menuFile) as f:
            self.menuItems = pickle.load(f)
      
      self.setupUI()
      
      self.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.createMenu(self)
      
      self.menuReader = MenuReader()
      
      self.refresh()
      
      self.show()
      
      
   def setupUI(self):
      self.resize(400, 400)
      self.setFocusPolicy(Qt.ClickFocus)
      self.setWindowFlags(Qt.FramelessWindowHint)
      desktop = qApp.desktop()
      screenSize = desktop.availableGeometry()
      self.move(screenSize.x(), screenSize.y() + screenSize.height() - 400)
      
      self.buttonListLayout = QVBoxLayout(self)
      
      self.backButton = QPushButton('Back')
      self.backButton.clicked.connect(self.backClicked)
      self.buttonListLayout.addWidget(self.backButton)
      
      self.listLayout = QHBoxLayout()
      self.buttonListLayout.addLayout(self.listLayout)
      self.listLayout.setSpacing(0)
      margin = 0
      self.listLayout.setContentsMargins(margin, margin, margin, margin)
      
      self.leftList = ListWidget()
      self.listLayout.addWidget(self.leftList)
      
      self.rightList = ListWidget()
      self.listLayout.addWidget(self.rightList)
      
      
   def createMenu(self, widget):
      addAction = QAction("Add...", self)
      addAction.triggered.connect(self.addClicked)
      widget.insertAction(None, addAction)
      editAction = QAction("Edit...", self)
      editAction.triggered.connect(self.editClicked)
      widget.insertAction(None, editAction)
      deleteAction = QAction("Delete", self)
      deleteAction.triggered.connect(self.deleteClicked)
      widget.insertAction(None, deleteAction)
      
      
   def changeEvent(self, event):
      if event.type() == QEvent.ActivationChange and not self.isActiveWindow() and not self.holdOpen:
         print "Lost focus"
         self.close()
         
         
   def addClicked(self):
      form = AddForm()
      
      self.holdOpen = True
      form.exec_()
      self.holdOpen = False
      
      if form.accepted:
         item = MenuItem()
         item.name = form.name
         item.command = form.command
         item.parent = self.currentItem
         item.folder = form.folder
         self.menuItems.append(item)
         self.refresh()
      
   def editClicked(self):
      print "Edit"
      
   def deleteClicked(self):
      print "Delete"
      
      
   def refresh(self):
      self.leftList.clear()
      self.rightList.clear()
      if self.currentItem != None:
         currParent = self.currentItem.parent
         for i in self.menuItems:
            if i.parent == currParent:
               newItem = ListItem(i)
               newItem.clicked.connect(self.itemClicked)
               self.leftList.add(newItem)
      
      for i in self.menuItems:
         if i.parent == self.currentItem:
            print "Adding", i.name
            newItem = ListItem(i)
            newItem.clicked.connect(self.itemClicked)
            self.rightList.add(newItem)
      
      filename = os.path.join(self.configDir, 'menu')
      with open(filename, 'w') as f:
         pickle.dump(self.menuItems, f)
            
      
   def itemClicked(self):
      sender = self.sender()
      if sender.item.folder:
         self.currentItem = sender.item
         self.refresh()
      else:
         os.system(sender.item.command + '&')
         self.close()
         
         
   def backClicked(self):
      if self.currentItem:
         self.currentItem = self.currentItem.parent
         self.refresh()
      