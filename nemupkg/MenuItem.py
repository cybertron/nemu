import os

class MenuItem:
   iconTheme = 'oxygen'
   def __init__(self):
      self.name = ''
      self.command = ''
      self.icon = ''
      self.parent = None
      self.folder = False
      
      
   def findIcon(self):
      if os.path.exists(self.icon) or (self.icon == '' and not self.folder):
         return
         
      if self.folder:
         self.icon = 'folder'
         
      print 'Searching for', self.name, 'icon'
      for basePath in ['/usr/share/icons', '/usr/local/share/icons', '/usr/share/pixmaps']:
         iconPath = self.lookForIcon(self.icon, basePath)
         if iconPath != '':
            break
      self.icon = iconPath
            
   def lookForIcon(self, icon, path, recurse = False):
      if os.path.isdir(path):
         for i in os.listdir(path):
            currPath = os.path.join(path, i)
            if i.startswith(icon + '.') or i == icon:
               return currPath
            if i == self.iconTheme:
               retval = self.lookForIcon(icon, currPath, True)
               if retval != '':
                  return retval
            if os.path.isdir(currPath) and recurse:
               retval = self.lookForIcon(icon, currPath, recurse)
               if retval != '':
                  return retval
         if not recurse:
            return self.lookForIcon(icon, path, True)
      return ''