from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
import pickle
import os
import copy
import sys
from MenuReader import *
from AddForm import *
from MenuItem import *
from ListWidget import *
from ListItem import *
from SettingsForm import *
from IconCache import *

class MainForm(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.holdOpen = False
      self.menuItems = []
      self.allItems = []
      self.favorites = []
      self.currentItem = None
      self.connected = False
      self.menuFile = os.path.expanduser('~/.nemu/menu')
      self.favoritesFile = os.path.expanduser('~/.nemu/favorites')
      self.settingsFile = os.path.expanduser('~/.nemu/settings')
      self.initSettings()
      
      self.connectToRunning()
      
      self.server = QLocalServer()
      self.server.newConnection.connect(self.handleConnection)
      QLocalServer.removeServer('nemuSocket')
      self.server.listen('nemuSocket')
      
      if not self.connected:
         self.configDir = os.path.expanduser('~/.nemu')
         if not os.path.isdir(self.configDir):
            os.mkdir(self.configDir)
         self.menuItems = self.loadConfig(self.menuFile, self.menuItems)
         self.favorites = self.loadConfig(self.favoritesFile, self.favorites)
         # Don't load directly into self.settings so we can add new default values as needed
         tempSettings = self.loadConfig(self.settingsFile, self.settings)
         for key, value in tempSettings.items():
            self.settings[key] = value
         
         # This should never happen, but unfortunately bugs do, so clean up orphaned items.
         # We need to do this because these items won't show up in the UI, but may interfere with
         # merges if they duplicate something that is being merged in.
         self.menuItems[:] = [i for i in self.menuItems if i.parent == None or i.parent in self.menuItems]
      
      self.setupUI()
      
      self.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.createMenu(self)
      
      self.refresh()
      
      if len(self.menuItems) == 0:
         self.firstRun()
      
      self.show()
      
      
   def initSettings(self):
      self.settings = dict()
      self.settings['width'] = 400
      self.settings['height'] = 400
      self.settings['quit'] = False
      
      
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename) as f:
            return pickle.load(f)
      else:
         return default
      
      
   def setupUI(self):
      self.resize(self.settings['width'], self.settings['height'])
      self.setWindowFlags(Qt.FramelessWindowHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
      self.setWindowTitle('Nemu')
      
      iconPath = os.path.join(os.path.dirname(__file__), 'images')
      iconPath = os.path.join(iconPath, 'nemu.png')
      self.setWindowIcon(QIcon(iconPath))
      
      self.place()
      
      self.buttonListLayout = QVBoxLayout(self)
      self.setMargins(self.buttonListLayout)
      
      self.buttonLayout = QHBoxLayout()
      self.setMargins(self.buttonLayout)
      self.buttonListLayout.addLayout(self.buttonLayout, 0)
      
      self.settingsButton = QPushButton()
      self.settingsButton.setIcon(QIcon(iconPath))
      self.settingsButton.setMinimumHeight(35)
      self.settingsButton.clicked.connect(self.settingsClicked)
      self.buttonLayout.addWidget(self.settingsButton, 0)
      
      self.backButton = QPushButton('Favorites')
      self.backButton.setMinimumHeight(35)
      self.backButton.clicked.connect(self.backClicked)
      self.buttonLayout.addWidget(self.backButton, 1)
      
      self.currentLabel = QLabel()
      self.currentLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.buttonLayout.addWidget(self.currentLabel, 1)
      
      self.sizeGrip = QSizeGrip(self)
      self.sizeGrip.setMinimumSize(QSize(25, 25))
      self.buttonLayout.addWidget(self.sizeGrip, 0, Qt.AlignRight | Qt.AlignTop)
      
      self.listSplitter = QSplitter()
      self.buttonListLayout.addWidget(self.listSplitter, 1)
      
      self.leftList = ListWidget(self.clearListMouseOver)
      self.listSplitter.addWidget(self.leftList)
      
      self.rightList = ListWidget(self.clearListMouseOver)
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
         self.hideOrClose()
         
   def hideOrClose(self):
      if self.settings['quit']:
         self.close()
      else:
         self.hide()
         
   def closeEvent(self, event):
      self.saveSettings()
      
   def hideEvent(self, event):
      self.saveSettings()
      
   def saveSettings(self):
      self.settings['splitterState'] = self.listSplitter.saveState()
      self.settings['width'] = self.width()
      self.settings['height'] = self.height()
      with open(self.settingsFile, 'w') as f:
         pickle.dump(self.settings, f)
         
   def place(self):
      desktop = qApp.desktop()
      screenSize = desktop.availableGeometry(QCursor.pos())
      self.move(screenSize.x(), screenSize.y() + screenSize.height() - self.height())
         
         
   def newClicked(self):
      form = AddForm()
      
      self.holdOpen = True
      form.exec_()
      self.holdOpen = False
      
      if form.accepted:
         item = MenuItem()
         item.name = form.name
         item.command = form.command
         item.folder = form.folder
         item.icon = form.icon
         item.findIcon()
         
         clicked = self.getClicked()
         if clicked:
            parent = clicked.item.parent
         elif self.leftList.mouseOver:
            if self.currentItem != None:
               parent = self.currentItem.parent
            else:
               parent = None
         else:
            parent = self.currentItem
         item.parent = parent
         
         self.menuItems.append(item)
         self.refresh()
      
   def editClicked(self):
      form = AddForm()
      clicked = self.getClicked()
      if clicked == None:
         return
      item = clicked.item
      
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
         item.findIcon()
         self.refresh()
      
      
   def deleteClicked(self):
      clicked = self.getClicked()
      if clicked == None:
         return
      self.delete(clicked.item)
      self.refresh()
      
   # Delete item and all of its children so we don't leave around orphaned items
   def delete(self, item):
      for i in self.menuItems:
         if i.parent == item:
            i.deleted = True
      
      if item in self.menuItems:
         item.deleted = True
      if item in self.favorites:
         self.favorites.remove(item)
      
      
   def addFavoriteClicked(self):
      newFavorite = copy.copy(self.getClicked().item)
      newFavorite.parent = None
      self.favorites.append(newFavorite)
      self.refresh()
      
      
   def getClicked(self):
      for i in self.allItems:
         if i.mouseOver:
            return i
            
   def clearMouseOver(self):
      for i in self.allItems:
         i.mouseOver = False
         
   def clearListMouseOver(self):
      self.leftList.mouseOver = False
      self.rightList.mouseOver = False
      
      
   def refresh(self):
      self.leftList.clear()
      self.rightList.clear()
      self.allItems = []
      sortedLeft = []
      sortedRight = []
      if self.currentItem != None:
         currParent = self.currentItem.parent
         for i in self.menuItems:
            if i.parent == currParent and not i.deleted:
               sortedLeft.append(i)
      else:
         for i in self.favorites:
            sortedLeft.append(i)
      
      for i in self.menuItems:
         if i.parent == self.currentItem and not i.deleted:
            sortedRight.append(i)
            
      sortedLeft.sort(key = lambda x: x.name)
      sortedLeft.sort(key = lambda x: not x.folder)
      sortedRight.sort(key = lambda x: x.name)
      sortedRight.sort(key = lambda x: not x.folder)
      for i in sortedLeft:
         self.leftList.add(self.createItem(i))
      for i in sortedRight:
         self.rightList.add(self.createItem(i))
      
      # Save the current menu status
      with open(self.menuFile, 'w') as f:
         pickle.dump(self.menuItems, f)
      with open(self.favoritesFile, 'w') as f:
         pickle.dump(self.favorites, f)
         
   def createItem(self, item):
      newItem = ListItem(item, self.clearMouseOver)
      newItem.clicked.connect(self.itemClicked)
      self.allItems.append(newItem)
      return newItem
            
      
   def itemClicked(self):
      sender = self.sender()
      if sender.item.folder:
         self.setCurrentItem(sender.item)
         self.refresh()
      else:
         flags = ['f', 'F', 'u', 'U', 'd', 'D', 'n', 'N', 'i', 'c', 'k', 'v', 'm']
         command = sender.item.command
         for i in flags:
            command = command.replace('%' + i, '')
         os.system(command + '&')
         self.hideOrClose()
         
         
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
         
         
   def settingsClicked(self):
      form = SettingsForm(self)
      form.quitCheck.setChecked(self.settings['quit'])
      
      self.holdOpen = True
      form.exec_()
      self.holdOpen = False
      
      if form.accepted:
         self.settings['quit'] = form.quitCheck.isChecked()
      
      
   def firstRun(self):
      QMessageBox.information(self, 'First Time?', 'Your menu is currently empty.  It is recommended that you import an existing menu file.')
      self.settingsClicked()
      
      
   def connectToRunning(self):
      socket = QLocalSocket()
      socket.connectToServer('nemuSocket')
      
      if socket.state() == QLocalSocket.ConnectedState:
         self.connected = True
         objString = ''
         while socket.state() == QLocalSocket.ConnectedState and not objString.endswith('@EOF@'):
            while socket.bytesAvailable() < 1:
               socket.waitForReadyRead()
            data = socket.read(32768)
            objString += data
         
         print 'Read', len(objString)
         recObject = pickle.loads(objString[:-5])
         self.menuItems = recObject['menuItems']
         self.favorites = recObject['favorites']
         self.settings = recObject['settings']
         IconCache.icons = recObject['iconCache']
      else:
         print 'No server running'
      
      
   def handleConnection(self):
      while self.server.hasPendingConnections():
         socket = self.server.nextPendingConnection()
         print 'Got connection'
         
         sendObject = dict()
         sendObject['menuItems'] = self.menuItems
         sendObject['favorites'] = self.favorites
         sendObject['settings'] = self.settings
         sendObject['iconCache'] = IconCache.icons
         print 'Sent', socket.write(pickle.dumps(sendObject))
         socket.flush()
         print 'Sent', socket.write('@EOF@')
         socket.flush()
         
         del socket
      sys.exit()
      
      