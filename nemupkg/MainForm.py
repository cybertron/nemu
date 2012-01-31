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
      self.initSettings()
      
      self.configDir = os.path.expanduser('~/.nemu')
      if not os.path.isdir(self.configDir):
         os.mkdir(self.configDir)
      self.menuFile = os.path.expanduser('~/.nemu/menu')
      self.menuItems = self.loadConfig(self.menuFile, self.menuItems)
      self.favoritesFile = os.path.expanduser('~/.nemu/favorites')
      self.favorites = self.loadConfig(self.favoritesFile, self.favorites)
      self.settingsFile = os.path.expanduser('~/.nemu/settings')
      self.settings = self.loadConfig(self.settingsFile, self.settings)
      
      self.setupUI()
      
      self.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.createMenu(self)
      
      self.menuReader = MenuReader()
      
      self.refresh()
      
      self.show()
      
      
   def initSettings(self):
      self.settings = dict()
      self.settings['width'] = 400
      self.settings['height'] = 400
      
      
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename) as f:
            return pickle.load(f)
      else:
         return default
      
      
   def setupUI(self):
      self.resize(self.settings['width'], self.settings['height'])
      self.setWindowFlags(Qt.FramelessWindowHint)
      desktop = qApp.desktop()
      screenSize = desktop.availableGeometry(QCursor.pos())
      self.move(screenSize.x(), screenSize.y() + screenSize.height() - self.height())
      
      self.buttonListLayout = QVBoxLayout(self)
      self.setMargins(self.buttonListLayout)
      
      self.buttonLayout = QHBoxLayout()
      self.setMargins(self.buttonLayout)
      self.buttonListLayout.addLayout(self.buttonLayout, 0)
      
      self.backButton = QPushButton('Favorites')
      self.backButton.clicked.connect(self.backClicked)
      self.buttonLayout.addWidget(self.backButton)
      
      self.currentLabel = QLabel()
      self.currentLabel.setAlignment(Qt.AlignHCenter)
      self.buttonLayout.addWidget(self.currentLabel)
      
      self.listSplitter = QSplitter()
      self.buttonListLayout.addWidget(self.listSplitter, 1)
      #self.setMargins(self.listLayout)
      
      self.leftList = ListWidget()
      self.listSplitter.addWidget(self.leftList)
      
      self.rightList = ListWidget()
      self.listSplitter.addWidget(self.rightList)
      
      # Has to be done after adding widgets to the splitter or the size will get reset again
      if 'splitterState' in self.settings:
         self.listSplitter.restoreState(self.settings['splitterState'])
      
   def setMargins(self, layout, margin = 0):
      layout.setSpacing(margin)
      layout.setContentsMargins(margin, margin, margin, margin)
      
      
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
         
   def closeEvent(self, event):
      self.settings['splitterState'] = self.listSplitter.saveState()
      self.settings['width'] = self.width()
      self.settings['height'] = self.height()
      with open(self.settingsFile, 'w') as f:
         pickle.dump(self.settings, f)
         
         
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
         self.setCurrentItem(sender.item)
         self.refresh()
      else:
         os.system(sender.item.command + '&')
         self.close()
         
         
   def backClicked(self):
      if self.currentItem:
         self.setCurrentItem(self.currentItem.parent)
         self.refresh()
         
         
   def setCurrentItem(self, item):
      self.currentItem = item
      if item != None:
         self.currentLabel.setText(item.name)
         if item.parent != None:
            self.backButton.setText(item.parent.name)
         else:
            self.backButton.setText('Favorites')
      else:
         self.currentLabel.setText('')
         self.backButton.setText('Favorites')
      