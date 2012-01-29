import os
from xml.dom.minidom import parse

class MenuReader:
   def __init__(self):
      self.xdgConfigDirs = self.getenv('XDG_CONFIG_DIRS').split(':')
      
      menuPrefix = self.getenv('XDG_MENU_PREFIX')
      if menuPrefix == '':
         menuPrefix = 'kde4-'
      menuPath = os.path.join('menus', menuPrefix + 'applications.menu')
      xdgMenu = self.findFile(menuPath)
      self.doc = parse(xdgMenu)
      
      
   def getenv(self, key):
      try:
         return os.environ[key]
      except:
         return ''
      
      
   def findFile(self, path):
      for base in self.xdgConfigDirs:
         current = os.path.join(base, path)
         if os.path.exists(current):
            return current