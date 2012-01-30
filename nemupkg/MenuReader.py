import os
from xml.dom.minidom import parse

class MenuReader:
   def __init__(self):
      self.xdgConfigDirs = self.getenv('XDG_CONFIG_DIRS')
      
      menuPrefix = self.getenv('XDG_MENU_PREFIX')
      if menuPrefix == '':
         menuPrefix = 'kde-4-' #'kde4-'
      menuPath = os.path.join('menus', menuPrefix + 'applications.menu')
      xdgMenu = self.findFile(menuPath)
      self.doc = parse(xdgMenu)
      
      
   def getenv(self, key):
      if key in os.environ:
         return os.environ[key]
      else:
         return ''
      
      
   def findFile(self, path):
      if ':' in self.xdgConfigDirs:
         dirs = self.xdgConfigDirs.split(':')
      else:
         dirs = [self.xdgConfigDirs]
         
      for base in dirs:
         current = os.path.join(base, path)
         if os.path.exists(current):
            return current