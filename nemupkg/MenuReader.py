import os
from xml.dom.minidom import parse
from MenuItem import *

class MenuReader:
   def __init__(self, xdgMenu = None):
      self.xdgConfigDirs = self.getenv('XDG_CONFIG_DIRS')
      if self.xdgConfigDirs == '':
         self.xdgConfigDirs = '/etc/xdg'
      self.xdgDataDirs = self.getenv('XDG_DATA_DIRS')
      self.xdgDataDirs += ':' + os.path.expanduser('~/.local/share')
      self.desktopEntries = dict()
      self.menus = []
      self.menuItems = []
      
      self.loadDesktopEntries()
      
      if xdgMenu == None:
         menuPrefix = self.getenv('XDG_MENU_PREFIX')
         if menuPrefix == '':
            menuPrefix = 'kde-4-'
            menuPrefix = 'kde4-'
         menuPath = os.path.join('menus', menuPrefix + 'applications.menu')
         xdgMenu = self.findFile(self.xdgConfigDirs, menuPath)
         
      if xdgMenu == None or not os.path.exists(xdgMenu):
         print 'Failed to find menu file'
         return

      self.doc = parse(xdgMenu)
      
      self.loadMenu(self.doc.documentElement)
      
      self.buildMenu()
      
      self.checkSingleRoot()
      
      
   def getenv(self, key):
      if key in os.environ:
         return os.environ[key]
      else:
         return ''
         
         
   def splitDirs(self, dirs):
      if ':' in dirs:
         return dirs.split(':')
      else:
         return [dirs]
      
      
   def findFile(self, baseDirs, path):
      for base in self.splitDirs(baseDirs):
         current = os.path.join(base, path)
         if os.path.exists(current):
            return current
            
            
   def loadDesktopEntries(self):
      for base in self.splitDirs(self.xdgDataDirs):
         currPath = os.path.join(base, 'applications')
         if os.path.isdir(currPath):
            self.loadEntryDirectory(currPath)
            
            
   def loadEntryDirectory(self, path, prefix = ''):
      for i in os.listdir(path):
         currPath = os.path.join(path, i)
         if os.path.isdir(currPath):
            self.loadEntryDirectory(currPath, prefix + i + '-')
         else:
            self.desktopEntries[prefix + i] = DesktopEntry(currPath)
            
            
   def loadMenu(self, element, parent = None):
      current = Menu()
      current.parent = parent
      self.menus.append(current)
      for i in element.childNodes:
         if i.nodeName == 'Name':
            current.name = i.firstChild.nodeValue
         elif i.nodeName == 'Menu':
            self.loadMenu(i, current)
         elif i.nodeName == 'OnlyUnallocated':
            del self.menus[-1]
            return
         elif i.nodeName == 'Include':
            self.readLogic(i, current.logic['Or'])
                  
                  
   def readLogic(self, element, logic):
      for i in element.childNodes:
         if i.nodeName == 'And' or i.nodeName == 'Or' or i.nodeName == 'Not':
            logic[i.nodeName] = dict()
            self.readLogic(i, logic[i.nodeName])
         elif i.nodeName == 'Category' or i.nodeName == 'Filename':
            name = i.firstChild.nodeValue
            logic[name] = Menu.categoryFilenameID
            
            
   def buildMenu(self):
      for i in self.menus:
         currMenu = MenuItem()
         currMenu.name = i.name
         currMenu.folder = True
         if i.parent != None:
            currMenu.parent = i.parent.menuItem
         i.menuItem = currMenu
         self.menuItems.append(currMenu)
         for key, value in self.desktopEntries.items():
            if i.include(key, value.categories, 'Or', i.logic['Or']) and not value.noDisplay:
               newItem = MenuItem()
               newItem.parent = currMenu
               newItem.name = value.name
               newItem.command = value.command
               newItem.icon = value.icon
               self.menuItems.append(newItem)
               
   # The menu file likely has a single root menu - we throw that out since
   # we are the root menu and don't need that extra layer of indirection
   def checkSingleRoot(self):
      root = None
      for i in self.menuItems:
         if i.parent == None:
            if root == None:
               root = i
            else:
               return
      for i in self.menuItems:
         if i.parent == root:
            i.parent = None
      self.menuItems.remove(root)
         
            
class DesktopEntry():
   def __init__(self, path):
      self.path = path
      self.categories = ''
      self.name = ''
      self.command = ''
      self.icon = ''
      self.noDisplay = False
      with open(path) as f:
         for line in f:
            if line[:10] == 'Categories':
               self.categories = self.getValue(line)
               self.categories = self.categories.split(';')
            if line[:5] == 'Name=':
               self.name = self.getValue(line)
            if line[:4] == 'Exec':
               self.command = self.getValue(line)
            if line[:4] == 'Icon':
               self.icon = self.getValue(line)
            if line[:9] == 'NoDisplay':
               if self.getValue(line).lower() == 'true':
                  self.noDisplay = True
               
   def getValue(self, line):
      s = line[:-1] # Remove \n
      s = s.split('=')
      return s[1]
               
               
class Menu():
   categoryFilenameID = 1
   def __init__(self):
      self.logic = {'Or': dict()}
      self.parent = None
      self.name = 'The unnamed menu'
      self.menuItem = None
      
      
   # key and value should be an appropriate pair from self.logic
   def include(self, filename, categories, key, value):
      if key == 'And':
         for k, v in value.items():
            if v == self.categoryFilenameID:
               retval = self.checkFile(k, filename, categories)
            else:
               retval = self.include(filename, categories, k, v)
            if not retval:
               return False
         return True
      elif key == 'Or':
         for k, v in value.items():
            if v == self.categoryFilenameID:
               retval = self.checkFile(k, filename, categories)
            else:
               retval = self.include(filename, categories, k, v)
            if retval:
               return True
         return False
      elif key == 'Not':
         for k, v in value.items():
            retval = False
            if v == self.categoryFilenameID:
               retval = self.checkFile(k, filename, categories)
            else:
               retval = self.include(filename, categories, k, v)
            if retval:
               return False
         return True
      else:
         print 'Got unrecognized logic type', key
         return False
      
   def checkFile(self, name, filename, categories):
      return name in categories or name == filename
         
      