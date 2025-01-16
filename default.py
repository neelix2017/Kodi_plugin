#   Title: Domoticz Control
#   Author: Peter Verčkovnik
#   Date: 1-4-2021
#   Info: Control for Domoticz
#   Version : 0.0.1
#

import os
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import re, traceback, datetime
import urllib, urlparse, urllib2, base64, json
import time
import threading


__addon__       = xbmcaddon.Addon()
__addon_id__    = "plugin.program.domoticz2"
__author__      = "Peter Verčkovnik"
__version__     = "0.0.1"


__language__    = xbmcaddon.Addon(__addon_id__).getLocalizedString
CWD             = xbmcaddon.Addon(__addon_id__).getAddonInfo('path')
__addonname__   = __addon__.getAddonInfo('id')
__dataroot__    = xbmc.translatePath('special://profile/addon_data/%s' % __addonname__ ).decode('utf-8')
RESOURCE_PATH   = os.path.join(CWD, "resources" )

DomoticzIP      = xbmcaddon.Addon(__addon_id__).getSetting('ip')
DomoticzPort    = xbmcaddon.Addon(__addon_id__).getSetting('port')
DomoticzUser    = xbmcaddon.Addon(__addon_id__).getSetting('user')
DomtoiczPwd     = xbmcaddon.Addon(__addon_id__).getSetting('pwd')
ListType        = int(xbmcaddon.Addon(__addon_id__).getSetting('listtype'))
CustomIdxs      = xbmcaddon.Addon(__addon_id__).getSetting('customidxs')
NameRoomplan    = xbmcaddon.Addon(__addon_id__).getSetting('nameroomplan')
ShowItems       = 16

ACTION_PREVIOUS_MENU = 10
ACTION_BACK = 92
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ITEM_HEIGHT = 40

__IDX__     = 0
__NAME__    = 1
__TYPE__    = 2
__IMAGE__   = 3
__STATUS__  = 4



class MainGUI(xbmcgui.WindowXMLDialog):
    def __init__(self,*args,**kwargs):
        pass

    def onInit(self):
        self.CurrentListType = 0
        self.domoticz = clsDomoticz()
        self.Loadlist(ListType)
        self.nowplaying = ""

    def Loadlist(self, ListNumber):
        self.getControl( 112 ).reset()
        xbmc.log ("laad nieuw lijst" + str(ListNumber))
        double=2

        self.CurrentListType = ListNumber
        xbmc.log ("CurrentListType Loadlist: " + str(self.CurrentListType))
        if ListNumber == 0 :
            self.devices = self.domoticz.list_switches(0, 0)
            self.getControl( 113 ).setLabel (__language__(30201).title())
        if ListNumber == 1 :
            self.devices = self.domoticz.list_switches(1, 0)
            self.getControl( 113 ).setLabel (__language__(30202).title())
        if ListNumber == 2 :
            self.devices = self.domoticz.list_switches(0, self.domoticz.get_roomid(NameRoomplan))
            self.getControl( 113 ).setLabel (NameRoomplan.title())
        if ListNumber == 3 : 
            self.devices = self.domoticz.list_scenes()
            self.getControl( 113 ).setLabel (__language__(30204).title())
        if ListNumber == 4 :
            self.devices = self.domoticz.list_sensors()
            self.getControl( 113 ).setLabel ("Senzorji")

        if len(self.devices) < int(ShowItems):
            self.getControl( 111 ).setHeight ( 130 + (len(self.devices) * ITEM_HEIGHT) * double ) 
            self.getControl( 112 ).setHeight ( len(self.devices) * ITEM_HEIGHT * double )    
        else:
            self.getControl( 111 ).setHeight ( 130 + (ShowItems * ITEM_HEIGHT) * double )
            self.getControl( 112 ).setHeight ( (ShowItems * ITEM_HEIGHT) * double )
        self.getControl( 112 ).setItemHeight( ITEM_HEIGHT * double )  

        for item in self.devices:
            listitem = xbmcgui.ListItem( label = item[__NAME__] )
            
            listitem.setIconImage( item[__IMAGE__] )
            listitem.setProperty( "idx", item[__IDX__] )

            self.getControl( 112 ).addItem( listitem )
	    
	if ListNumber == 0 :
	    listitem = xbmcgui.ListItem( label = "Padavine" )            
            listitem.setIconImage( "http://"+ DomoticzIP + ":" + DomoticzPort +"/images/dimmer48-on.png" )
            listitem.setProperty( "idx", "9999" )
	    self.getControl( 112 ).addItem( listitem )
	 
        self.getControl( 112 ).setItemHeight( ITEM_HEIGHT * double )
        self.setFocus(self.getControl(112))
        
        listitem = xbmcgui.ListItem( label = "izhod" )            
        listitem.setProperty( "idx", "9009" )
        self.getControl( 112 ).addItem( listitem )

    def onAction(self, action):
        #if action == ACTION_MOVE_UP or action == ACTION_MOVE_DOWN:
           #self.getControl( 150 ).setImage(RESOURCE_PATH+'\skins\Default\media\domoticz_logo.png')
        #if self.domoticz.Timer:
           #self.domoticz.Timer.cancel()
            #self.domoticz.Timer.join()
        if action == ACTION_PREVIOUS_MENU or action == ACTION_BACK:
          #  if self.domoticz.Timer:
          #     self.domoticz.Timer.cancel()
            xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
            self.close()
        if action == ACTION_MOVE_LEFT:
            xbmc.log ("CurrentListType Action: " + str(self.CurrentListType))
            currentList = self.CurrentListType

            if currentList == 0 and CustomIdxs != "":
                currentList = 4
            elif currentList == 0 and CustomIdxs == "":
                 currentList = 4
            elif currentList == 4 and NameRoomplan == "":
                 currentList = 1
            else:
                currentList = int(currentList) - 1
            self.Loadlist(currentList)

        if action == ACTION_MOVE_RIGHT:
            xbmc.log ("CurrentListType Action: " + str(self.CurrentListType))
            currentList = self.CurrentListType
            if currentList == 4:
                 currentList = 0
            elif currentList == 4 and CustomIdxs == "":
                 currentList = 0
            elif currentList == 1 and NameRoomplan == "":
                 currentList = 4
            else:
                currentList = int(currentList) + 1
            self.Loadlist(currentList)

    def onClick(self, controlID):
        if controlID == 112:
            idx = str(self.getControl(112).getSelectedItem().getProperty("idx"))
            xbmc.log ("selected : " + idx)
            if (idx=="9009"):
                xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
                self.close()
                return
            if (idx=="9999"):
                self.domoticz.setradar(self)
                return
            if (idx=="9989"):
                self.domoticz.setradar(self)
                return
            if (idx=="48"):
                self.domoticz.setcam(self, 1)
                return
            if (idx=="49"):
                self.domoticz.setcam(self, 2)
                return
            if (idx=="92"):
                self.domoticz.setcam(self, 4)
                return
            if (idx=="93"):
                self.domoticz.setcam(self, 3)
                return
            for item in self.devices:
                if item[__IDX__] == idx and (item[__STATUS__] == 0 or item[__STATUS__] == 2):
                    if ListType == 3:
                        self.domoticz.set_scenestatus(idx, 1)
                    else:
                        self.domoticz.set_switchstatus(idx, 1)
                elif item[__IDX__] == idx and item[__STATUS__] == 1:
                    if ListType == 3:
                        self.domoticz.set_scenestatus(idx, 0)
                    else:
                        self.domoticz.set_switchstatus(idx, 0)
            #self.close()
            self.onInit()

    def onFocus(self, controlID):
        pass

class clsDomoticz:
    def __init__(self):
        self.base64string = base64.encodestring('%s:%s' % (DomoticzUser, DomtoiczPwd)).replace('\n', '')
        self.Timer = None
       
    def load_json(self, url):
        request = urllib2.Request(url)
        request.add_header("Authorization", "Basic %s" % self.base64string)
        return urllib2.urlopen(request).read()

    # takes 2 arguments. first if only favorites should be listed (0 or 1) and the second is the plan id. if no plan is selected it should be 0
    def list_switches(self, IsFavorite, plan):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=devices&filter=all&used=true&order=Name'
        if int(plan) > 0:
            self.url += "&plan=" + str(plan)

        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
                if ((IsFavorite == 1 and json_object["result"][i]["Favorite"] == 1) or IsFavorite == 0) and "Light/Switch" in json_object["result"][i]["Type"] :
                    item.append (json_object["result"][i]["idx"])
                    item.append (json_object["result"][i]["Name"]+ "   :\r\n"+json_object["result"][i]["LastUpdate"])
                    item.append (json_object["result"][i]["Type"])
                    
                    # Image
                    if json_object["result"][i]["SwitchType"] == "Contact":
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/contact48_Open.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/contact48.png")
                    elif json_object["result"][i]["SwitchType"] == "Door Lock":
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/door48open.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/door48.png")
                    elif json_object["result"][i]["SwitchType"] == "Dimmer":
                        if json_object["result"][i]["Status"] == "On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/dimmer48-on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/dimmer48-off.png")
                    elif "Blinds" in json_object["result"][i]["SwitchType"]:
                        if json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/blindsopen48sel.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/blinds48.png")
                    elif json_object["result"][i]["SwitchType"] == "Doorbell":
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/doorbell48.png")
                    elif json_object["result"][i]["SwitchType"] == "Smoke Detector":
                        if json_object["result"][i]["Status"] == "On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/smoke48on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/smoke48off.png")
                    elif json_object["result"][i]["SwitchType"] == "X10 Siren":
                        if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "All On":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/siren-on.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/siren-off.png")
                    else:
                        if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "Open":
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_On.png")
                        else:
                            item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_Off.png")

                    # Status
                    if json_object["result"][i]["Status"] == "On" or json_object["result"][i]["Status"] == "Open" or json_object["result"][i]["Status"] == "All On": 
                        item.append (1)
                    if json_object["result"][i]["Status"] == "Off" or json_object["result"][i]["Status"] == "Locked" or json_object["result"][i]["Status"] == "Closed" or json_object["result"][i]["Status"] == "All Off": 
                        item.append (0)
                    if json_object["result"][i]["Status"] == "Mixed": 
                        item.append (2)
                    
                if len(item) > 0:
                    array_id.append (item)
            return array_id

    def list_scenes(self):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=scenes'
        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
            
                item.append (json_object["result"][i]["idx"])
                item.append (json_object["result"][i]["Name"])
                item.append (json_object["result"][i]["Type"])
                
                # Image
                if json_object["result"][i]["Type"] == "Scene":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/push48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "On":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/push48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "Off":
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/pushoff48.png")
                elif json_object["result"][i]["Type"] == "Group" and json_object["result"][i]["Status"] == "Mixed":
                    item.append ("pushmixed48.png")
                else:
                    item.append ("")
                
                # Status
                if json_object["result"][i]["Status"] == "On": 
                    item.append (1)
                if json_object["result"][i]["Status"] == "Off": 
                    item.append (0)
                if json_object["result"][i]["Status"] == "Mixed": 
                    item.append (2)
                
                if len(item) > 0:
                    array_id.append (item)
            return array_id
			
    def list_sensors(self):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=devices&filter=temp&used=true&order=Name'
        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
                if (1==1) :
                    date_time_obj = datetime.datetime.strptime(json_object["result"][i]["LastUpdate"], '%Y-%m-%d %H:%M:%S')
                    if ((datetime.datetime.now()-date_time_obj).seconds/60 > 60):continue
                    item.append (json_object["result"][i]["idx"])
                    item.append (json_object["result"][i]["Name"]+ "   :\r\n"+json_object["result"][i]["Data"])
                    item.append (json_object["result"][i]["Type"])
                    
                    # Image
                    item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/temperature.png")
                    
                    # Status
                    item.append (2)
                    
                if len(item) > 0:
                    array_id.append (item)
            return array_id

    def list_customswitches(self, idxs):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=devices&filter=all&used=true&order=Name'
        array_idx = idxs.split(",")
        array_id = []
        json_object = json.loads(self.load_json(self.url))

        status = -2
        if json_object["status"] == "OK":
            status = -1
            for i, v in enumerate(json_object["result"]):
                item = []
                if json_object["result"][i]["idx"] in array_idx and "Lighting" in json_object["result"][i]["Type"] :
                    item.append (json_object["result"][i]["idx"])
                    item.append (json_object["result"][i]["Name"])
                    item.append (json_object["result"][i]["Type"])
                    
                    # Image
                    if json_object["result"][i]["Status"] == "On":
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_On.png")
                    else:
                        item.append ("http://"+ DomoticzIP + ":" + DomoticzPort +"/images/" + json_object["result"][i]["Image"] + "48_Off.png")

                    # Status
                    if json_object["result"][i]["Status"] == "On": 
                        item.append (1)
                    if json_object["result"][i]["Status"] == "Off": 
                        item.append (0)
                    if json_object["result"][i]["Status"] == "Mixed": 
                        item.append (2)
                    
                if len(item) > 0:
                    array_id.append (item)
            return array_id

    def get_roomid(self, roomname):
        self.url = 'http://'+ DomoticzIP + ":" + DomoticzPort +'/json.htm?type=plans'
        json_object = json.loads(self.load_json(self.url))
        roomid = 0
        if json_object["status"] == "OK":
            for i, v in enumerate(json_object["result"]):
                if json_object["result"][i]["Name"].lower() == str(roomname).lower() :
                    roomid = json_object["result"][i]["idx"]
        return roomid

    def set_switchstatus (self, switchid, status):
        update_domoticz = 0
        #xbmcgui.Dialog().ok('switch id', str(switchid)) 
        if status == 1:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchlight&idx=" + str(switchid) + "&switchcmd=On&level=0"
            update_domoticz = 1
        if status == 0:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchlight&idx=" + str(switchid) + "&switchcmd=Off&level=0"
            update_domoticz = 1

        if update_domoticz:
            request = urllib2.Request(self.url)
            request.add_header("Authorization", "Basic %s" % self.base64string)
            self.response = urllib2.urlopen(request).read()

    def setcam (self, kodi, idx):
        #kodi.getControl( 150 ).setImage('http://127.0.0.1:8080/camsnapshot.jpg?idx='+str(idx)+'?t='+str(time.time())+'000',False)
        file = ""
        renew = 8
        title =""
        if idx == 1:
            file = 'http://admin:admin@192.168.0.106/tmpfs/auto.jpg'
            video = "rtsp://admin:admin@192.168.0.106:554/11"
            renew = 1
            title = "Otroska soba"
        elif idx == 2:
            file = 'http://127.0.0.1:8082/pic.jpg'
            video = "http://127.0.0.1:8082/video.mpeg"
            renew = 2
            title = "Dnevna soba"
        elif idx == 3:
            file = 'http://192.168.0.200/control?cmd=esp32cam'#'http://192.168.0.200/control?cmd=esp32cam,picture'
            video = "http://192.168.0.200/control?cmd=esp32cam,stream"
            renew = 3
            title = "Garaza"
        elif idx == 4:
            file = 'http://192.168.0.149/control?cmd=esp32cam'#'http://192.168.0.149/control?cmd=esp32cam,picture'
            video = "http://192.168.0.149/control?cmd=esp32cam,stream"
            renew = 3
            title = "Vhodna vrata"
        window = DialogWindow(file,title,renew,video)
        window.doModal()
        #xbmc.executebuiltin("RunScript(script.hello.world,link=%s)"%(self.file))
        #xbmc.executebuiltin("RunScript(script.hello.world,image=%s&line1=%s&rate=%s)"%(file,title,renew))
        #xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
        #self.close()
        #kodi.getControl( 150 ).setImage(file,False)
        #self.Timer = threading.Timer(  renew,  self.setcam,(kodi,idx))
        #self.Timer.start()
    
    def setradar (self, kodi):
        kodi.getControl( 150 ).setImage('http://meteo.arso.gov.si/uploads/probase/www/observ/radar/si0-rm.gif',False)
        if xbmc.Player().isPlaying(): ui.nowplaying = xbmc.Player().getPlayingFile()
        xbmc.Player().play("http://meteo.arso.gov.si/uploads/probase/www/fproduct/media/sl/fcast_si_audio_hbr.mp3", windowed=False)

    def set_scenestatus (self, switchid, status):
        update_domoticz = 0
        if status == 1:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchscene&idx=" + str(switchid) + "&switchcmd=On"
            update_domoticz = 1
        if status == 0:
            self.url = "http://" + DomoticzIP + ":" + DomoticzPort + "/json.htm?type=command&param=switchscene&idx=" + str(switchid) + "&switchcmd=Off"
            update_domoticz = 1

        if update_domoticz:
            request = urllib2.Request(self.url)
            request.add_header("Authorization", "Basic %s" % self.base64string)
            self.response = urllib2.urlopen(request).read()

#open(os.path.join( __dataroot__, "text.txt" ), 'a').close()
class DialogWindow(xbmcgui.WindowDialog):
    def __init__(self,image, line1, rate,video):
        self.image = image
        self.line1 = line1
        self.rate = rate
        self.video = video
        self.addControl(xbmcgui.ControlImage (x=500, y=300, width=420, height=220, filename=RESOURCE_PATH+'\skins\Default\media\Dialog.png'))
        self.btnPic = xbmcgui.ControlButton(x=510, y=310, width=400, height=100,  label='pic', font='font14', textOffsetY=30, alignment=10 )
        self.btnVideo = xbmcgui.ControlButton(x=510, y=410, width=400, height=100,  label='video', font='font14',textOffsetY=30, alignment=10 )
        self.addControl(self.btnPic)
        self.addControl(self.btnVideo)
        self.setFocus(self.btnPic)

    def exiting(self):
        self.Timer.cancel()
        #xbmc.executeJSONRPC({ "jsonrpc": "2.0", "method": "GUI.ShowNotification", "id":1, "params":{"title":"Obvestilo","message":"Pregled zakljucen"}})
        #ui.getControl(9999).setVisible(False)
        if ui.nowplaying != "":xbmc.Player().play(ui.nowplaying, windowed=False)
        

    def onControl(self, controlID):
        if controlID.getId() == 3002:
            xbmc.executebuiltin("RunScript(script.hello.world,image=%s&line1=%s&rate=%s&box=%s&ask=%s)"%(self.image,self.line1,self.rate,"400 10 860 600","0"))
            xbmc.executebuiltin("Action(Back,%s)" % xbmcgui.getCurrentWindowId())
            self.close()
        if controlID.getId() == 3003:
            if xbmc.Player().isPlaying(): ui.nowplaying = xbmc.Player().getPlayingFile()
            #ui.getControl(9999).setVisible(True)
            xbmc.Player().play(self.video, windowed=True)
            self.Timer = threading.Timer(  15,  self.exiting)
            self.Timer.start()
            self.close()
 
    def onAction(self, action):
        if action == 10 or action == 92:
            self.close()
        if action == 3:
            self.setFocus(self.btnPic)
        if action == 4:
            self.setFocus(self.btnVideo)

ui = MainGUI("main_gui.xml",CWD,"Default")
ui.doModal()
