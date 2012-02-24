from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSvg import *

class IconCache():
   icons = dict()
   
   @staticmethod
   def __getitem__(key):
      if key not in IconCache.icons:
         if not key.endswith('.svg') and not key.endswith('.svgz'):
            image = QImage(key).scaled(24, 24)
         else:
            svg = QSvgRenderer(key)
            image = QImage(24, 24, QImage.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            svg.render(painter)
            painter.end()
         bytes = QByteArray()
         buff = QBuffer(bytes)
         buff.open(QIODevice.WriteOnly)
         image.save(buff, 'png')
         IconCache.icons[key] = bytes
      return QIcon(QPixmap.fromImage(QImage.fromData(IconCache.icons[key])))