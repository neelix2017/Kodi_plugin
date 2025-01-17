import xbmc
import xbmcaddon
import xbmcgui
import sys
import urllib.parse
import os

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
CWD             = xbmcaddon.Addon(addon.getAddonInfo('id')).getAddonInfo('path')
RESOURCE_PATH   = os.path.join(CWD, "resources" )

class PopupWindow(xbmcgui.WindowDialog):
    def __init__(self, image, line, time):
        self.addControl(xbmcgui.ControlImage(x=10, y=10, width=1240, height=70, filename=RESOURCE_PATH+'\skins\Default\media\Dialog.png'))
        self.addControl(xbmcgui.ControlImage(x=40, y=15, width=50, height=50, filename=image[0]))
        #self.addControl(xbmcgui.ControlLabel(x=190, y=25, width=1200, height=50, label=line[0]))
        self.fadelabel = xbmcgui.ControlFadeLabel(x=120, y=35, width=1100, height=50, font='font25', textColor='0xFFFFFFFF')
        self.addControl(self.fadelabel)
        self.fadelabel.addLabel(line[0])
        self.fadelabel.setScrolling(True)

if __name__ == '__main__':
    params = urllib.parse.parse_qs('&'.join(sys.argv[1:]))
    window = PopupWindow(**params)
    window.show()
    xx = sys.argv[1:][len(sys.argv[1:])-1].split('=')[1]
    if (str(xx).isnumeric()): xx= int(xx)
    else: xx= 60
    xbmc.sleep(xx*1000)
    window.close()
    del window
