from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QSizeGrip, QSplitter,QAction, QMessageBox)
from PyQt5.QtGui import QIcon, QCursor
import cPickle
import os
import copy
import sys
import time
from subprocess import Popen
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
      
      # If a Nemu instance is already running, this is as far as we go
      self.connectToRunning()
      
      self.holdOpen = False
      self.menuItems = []
      self.allItems = []
      self.favorites = []
      self.currentItem = None
      self.menuFile = os.path.expanduser('~/.nemu/menu')
      self.favoritesFile = os.path.expanduser('~/.nemu/favorites')
      self.settingsFile = os.path.expanduser('~/.nemu/settings')
      self.initSettings()

      self.server = QLocalServer()
      self.server.newConnection.connect(self.handleConnection)
      QLocalServer.removeServer('nemuSocket')
      self.server.listen('nemuSocket')
      
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
      # Look for broken icon paths
      needSave = False
      for i in self.menuItems + self.favorites:
          if not os.path.exists(i.icon):
              i.findIcon()
              needSave = True
      if needSave:
         self.saveMenu()


      for i in self.menuItems:
         if not hasattr(i, 'imported'):
            i.imported = False
      
      self.setupUI()
      
      self.setContextMenuPolicy(Qt.ActionsContextMenu)
      self.createMenu(self)
      
      self.refresh(False)
      
      if len(self.menuItems) == 0:
         self.firstRun()
      
      self.show()
      
      self.keepaliveTimer = QTimer(self)
      self.keepaliveTimer.timeout.connect(self.keepalive)
      self.keepaliveTimer.start(60000)
      
      
   def initSettings(self):
      self.settings = dict()
      self.settings['width'] = 400
      self.settings['height'] = 400
      self.settings['quit'] = False
      self.settings['imported'] = []
      self.settings['iconTheme'] = None
      
      
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename, 'rb') as f:
            data = f.read().replace('PyQt4', 'PyQt5')
            return cPickle.loads(data)
      else:
         return default
      
      
   def setupUI(self):
      self.resize(self.settings['width'], self.settings['height'])
      self.setWindowFlags(Qt.FramelessWindowHint | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
      #self.setWindowFlags(Qt.X11BypassWindowManagerHint)
      self.setWindowTitle('Nemu')
      self.setMouseTracking(True)
      
      iconPath = os.path.join(os.path.dirname(__file__), 'images')
      iconPath = os.path.join(iconPath, 'nemu.png')
      self.setWindowIcon(IconCache()[iconPath])
      
      self.place()
      
      self.buttonListLayout = QVBoxLayout(self)
      self.setMargins(self.buttonListLayout)
      
      self.buttonLayout = QHBoxLayout()
      self.setMargins(self.buttonLayout)
      
      # Settings and Filter box
      self.filterLayout = QHBoxLayout()
      self.settingsButton = QPushButton()
      self.settingsButton.setIcon(QIcon(iconPath))
      self.settingsButton.setMinimumHeight(35)
      self.settingsButton.clicked.connect(self.settingsClicked)
      self.filterLayout.addWidget(self.settingsButton, 0)
      
      self.filterLabel = QLabel("Filter")
      self.filterLayout.addWidget(self.filterLabel)
      
      self.filterBox = QLineEdit()
      self.filterBox.textChanged.connect(self.refresh)
      self.filterLayout.addWidget(self.filterBox)
      
      self.sizeGrip = QSizeGrip(self)
      self.sizeGrip.setMinimumSize(QSize(25, 25))
      self.filterLayout.addWidget(self.sizeGrip, 0, Qt.AlignRight | Qt.AlignTop)
      
      self.buttonListLayout.addLayout(self.filterLayout)
      
      # Top buttons and labels
      self.backButton = QPushButton('Favorites')
      self.backButton.setMinimumHeight(35)
      self.backButton.clicked.connect(self.backClicked)
      self.buttonLayout.addWidget(self.backButton, 1)
      
      self.currentLabel = QLabel()
      self.currentLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.buttonLayout.addWidget(self.currentLabel, 1)
      
      self.buttonListLayout.addLayout(self.buttonLayout, 0)
      
      # Menu item display
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
      
      
   def hideOrClose(self):
      if self.settings['quit']:
         self.close()
      else:
         self.hide()
         
   def closeEvent(self, event):
      self.saveSettings()
      
   def hideEvent(self, event):
      self.releaseMouse()
      self.saveSettings()
      
   def mouseMoveEvent(self, event):
      if self.hasMouse():
         self.releaseMouse()
      
   def leaveEvent(self, event):
      # If we set holdOpen, it means that we've opened a dialog, so we shouldn't grab
      if not self.hasMouse():
         self.grabMouse()
      
   def mousePressEvent(self, event):
      if not self.hasMouse():
         self.hideOrClose()
         
   def hasMouse(self):
      return self.geometry().contains(QCursor.pos())
         

   def saveSettings(self):
      self.settings['splitterState'] = self.listSplitter.saveState()
      self.settings['width'] = self.width()
      self.settings['height'] = self.height()
      with open(self.settingsFile, 'wb') as f:
         cPickle.dump(self.settings, f)
         
   def place(self):
      desktop = qApp.desktop()
      screenSize = desktop.availableGeometry(QCursor.pos())
      self.move(screenSize.x(), screenSize.y() + screenSize.height() - self.height())
         
         
   def newClicked(self):
      form = AddForm()
      
      self.holdOpen = True
      form.exec_()
      self.checkMouse()
      self.holdOpen = False
      
      if form.accepted:
         item = MenuItem()
         item.name = form.name
         item.command = form.command
         item.working = form.working
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
      form.working = item.working
      form.folder = item.folder
      form.icon = item.icon
      form.populateFields()
      
      self.holdOpen = True
      form.exec_()
      self.checkMouse()
      self.holdOpen = False
      
      if form.accepted:
         item.name = form.name
         item.command = form.command
         item.working = form.working
         item.folder = form.folder
         item.icon = form.icon
         item.imported = False
         item.findIcon()
         self.refresh()
         
         
   def checkMouse(self):
      if not self.hasMouse():
         self.grabMouse()
      
      
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
         item.imported = False
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
      
      
   def refresh(self, save = True):
      self.leftList.clear()
      self.rightList.clear()
      self.allItems = []
      sortedLeft = []
      sortedRight = []
      self.updateFilter()
      
      if self.currentItem != None:
         currParent = self.currentItem.parent
         for i in self.menuItems:
            if i.parent == currParent and not i.deleted and i.matchedFilter:
               sortedLeft.append(i)
      else:
         for i in self.favorites:
            sortedLeft.append(i)
      
      for i in self.menuItems:
         if i.parent == self.currentItem and not i.deleted and i.matchedFilter:
            sortedRight.append(i)
            
      sortedLeft.sort(key = lambda x: x.name)
      sortedLeft.sort(key = lambda x: not x.folder)
      sortedRight.sort(key = lambda x: x.name)
      sortedRight.sort(key = lambda x: not x.folder)
      for i in sortedLeft:
         self.leftList.add(self.createItem(i))
      for i in sortedRight:
         self.rightList.add(self.createItem(i))
         
      if save:
         self.saveMenu()

   def saveMenu(self):
      # Save the current menu status
      with open(self.menuFile, 'wb') as f:
         cPickle.dump(self.menuItems, f)
      with open(self.favoritesFile, 'wb') as f:
         cPickle.dump(self.favorites, f)

   def createItem(self, item):
      newItem = ListItem(item, self.clearMouseOver)
      newItem.clicked.connect(self.itemClicked)
      self.allItems.append(newItem)
      return newItem
      
   def updateFilter(self):
      filterValue = str(self.filterBox.text())
      
      for i in self.menuItems:
         i.checkFilter(filterValue)
            
      
   def itemClicked(self):
      sender = self.sender()
      if sender.item.folder:
         self.setCurrentItem(sender.item)
         self.refresh(False)
      else:
         flags = ['f', 'F', 'u', 'U', 'd', 'D', 'n', 'N', 'i', 'k', 'v', 'm']
         command = sender.item.command
         for i in flags:
            command = command.replace('%' + i, '')
         # %c needs a proper value in some cases
         command = command.replace('%c', '"%s"' % sender.item.name)
         working = sender.item.working
         if not os.path.isdir(working):
            working = None
            
         # Need to redirect stdout and stderr so if the process writes something it won't fail
         with open(os.path.devnull, 'w') as devnull:
            Popen(command + '&', stdout=devnull, stderr=devnull, shell=True, cwd=working)
         self.hideOrClose()
         
         
   def backClicked(self):
      if self.currentItem:
         self.setCurrentItem(self.currentItem.parent)
         self.refresh(False)
         
         
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
      theme = self.settings.get('iconTheme')
      if theme:
         form.themeCombo.setCurrentIndex(form.themeCombo.findText(theme))
      
      self.holdOpen = True
      form.exec_()
      self.checkMouse()
      self.holdOpen = False
      
      if form.accepted:
         self.settings['quit'] = form.quitCheck.isChecked()
      
      
   def firstRun(self):
      QMessageBox.information(self, 'First Time?', 'Your menu is currently empty.  It is recommended that you import an existing menu file.')
      self.settingsClicked()
      
      
   def connectToRunning(self):
      self.socket = QLocalSocket()
      self.socket.connectToServer('nemuSocket')
      self.socket.waitForConnected(1000)
      
      if self.socket.state() == QLocalSocket.ConnectedState:
         print 'Server found'
         if self.socket.waitForReadyRead(3000):
            line = self.socket.readLine()
            print line
         else:
            print self.socket.errorString()
         sys.exit()
      else:
         print 'No server running'
      
      
   def handleConnection(self):
      import datetime
      print "Got connection", datetime.datetime.now()
      
      connection = self.server.nextPendingConnection()
      connection.write('connected')
      del connection
      
      self.setCurrentItem(None)
      self.filterBox.setText('')
      self.refresh(False)
      self.show()
      print "Showed", datetime.datetime.now()
      return
      
      
   # Call periodically to keep data resident in memory (hopefully)
   def keepalive(self):
      if self.isHidden():
         self.refresh(False)
