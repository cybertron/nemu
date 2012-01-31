from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pickle
import os
import copy
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
      self.allItems = []
      self.favorites = []
      self.currentItem = None
      
      self.configDir = os.path.expanduser('~/.nemu')
      if not os.path.isdir(self.configDir):
         os.mkdir(self.configDir)
      self.menuFile = os.path.expanduser('~/.nemu/menu')
      self.menuItems = self.loadConfig(self.menuFile, self.menuItems)
      self.favoritesFile = os.path.expanduser('~/.nemu/favorites')
      self.favorites = self.loadConfig(self.favoritesFile, self.favorites)
      
      self.setupUI()
      
      self.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.createMenu(self)
      
      self.menuReader = MenuReader()
      
      self.refresh()
      
      self.show()
      
      
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename) as f:
            return pickle.load(f)
      else:
         return default
      
      
   def setupUI(self):
      self.resize(400, 400)
      self.setFocusPolicy(Qt.ClickFocus)
      self.setWindowFlags(Qt.FramelessWindowHint)
      desktop = qApp.desktop()
      screenSize = desktop.availableGeometry(QCursor.pos())
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
      addFavoriteAction = QAction('Add to Favorites', self)
      addFavoriteAction.triggered.connect(self.addFavoriteClicked)
      widget.insertAction(None, addFavoriteAction)
      addAction = QAction("New...", self)
      addAction.triggered.connect(self.newClicked)
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
         
         
   def newClicked(self):
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
         item.icon = form.icon
         self.menuItems.append(item)
         self.refresh()
      
   def editClicked(self):
      form = AddForm()
      item = self.getClicked().item
      
      form.name = item.name
      form.command = item.command
      form.folder = item.folder
      form.icon = item.icon
      form.populateFields()
      
      self.holdOpen = True
      form.exec_()
      self.holdOpen = False
      
      if form.accepted:
         item.name = form.name
         item.command = form.command
         item.folder = form.folder
         item.icon = form.icon
         self.refresh()
      
      
   def deleteClicked(self):
      self.delete(self.getClicked().item)
      self.refresh()
      
   # Delete item and all of its children so we don't leave around orphaned items
   def delete(self, item):
      for i in self.menuItems:
         if i.parent == item:
            self.delete(i)
      if item in self.menuItems:
         self.menuItems.remove(item)
      if item in self.favorites:
         self.favorites.remove(item)
      
      
   def addFavoriteClicked(self):
      self.favorites.append(copy.copy(self.getClicked().item))
      self.refresh()
      
      
   def getClicked(self):
      for i in self.allItems:
         if i.mouseOver:
            return i
      
      
   def refresh(self):
      self.leftList.clear()
      self.rightList.clear()
      self.allItems = []
      if self.currentItem != None:
         currParent = self.currentItem.parent
         for i in self.menuItems:
            if i.parent == currParent:
               newItem = self.createItem(i)
               self.leftList.add(newItem)
      else:
         for i in self.favorites:
            newItem = self.createItem(i)
            self.leftList.add(newItem)
      
      for i in self.menuItems:
         if i.parent == self.currentItem:
            newItem = self.createItem(i)
            self.rightList.add(newItem)
      
      # Save the current menu status
      with open(self.menuFile, 'w') as f:
         pickle.dump(self.menuItems, f)
      with open(self.favoritesFile, 'w') as f:
         pickle.dump(self.favorites, f)
         
   def createItem(self, item):
      newItem = ListItem(item)
      newItem.clicked.connect(self.itemClicked)
      self.allItems.append(newItem)
      return newItem
            
      
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
      