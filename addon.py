# -*- coding: utf-8 -*-
import http.cookiejar
import datetime
import json
import os
import sys
import urllib.request, urllib.parse, urllib.error

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

#######################################

# global constants

url_base = 'http://api.rtvslo.si/ava/'
client_id = '82013fb3a531d5414f478747c1aca622'
delete_action = 'deleteall893745927368199189474t52910373h2i2u2j2788927628018736tghs8291282'
podcast_file = 'podcast_'

data_folder = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
try:
    os.makedirs(data_folder)
except:
    pass

search_history_file = os.path.join(data_folder, 'history.json')
mark_file = os.path.join(data_folder, 'mark.json')


# classes

#######################################
# functions
def drmcontent(showid):
        url_query = {}
        url_query['client_id'] = client_id
        url_query['session_id'] = api
        url_query['callback'] = 'jQuery1113023734881856870338_1462389077542'
        url_query['_'] = '1462389077543'

        url = build_url(url_base + 'getRecordingDrm/' + showid, url_query)

        # download response from rtvslo api
        rtvsloHtml = urllib.request.urlopen(url)
        rtvsloData = rtvsloHtml.read().decode("utf8")
        rtvsloHtml.close()

        # extract json from response
        x = rtvsloData.find('({')
        y = rtvsloData.rfind('});')
        if x < 0 or y < 0:
            xbmcgui.Dialog().ok('RTV Slovenija', 'Strežnik ni posredoval podatkov o podcastu.')
            return
        rtvsloData = rtvsloData[x + 1:y + 1]
        complete_item = json.loads(rtvsloData)
        jwt = complete_item['response']['jwt']
        
        url_query = {}
        url_query['client_id'] = client_id
        url_query['jwt'] = jwt
        url_query['session_id'] = api
        url_query['callback'] = 'jQuery1113023734881856870338_1462389077542'
        url_query['_'] = '1462389077543'

        url = build_url("https://api.rtvslo.si/ava/getMedia/" + showid, url_query)
        rtvsloHtml = urllib.request.urlopen(url)
        rtvsloData = rtvsloHtml.read().decode("utf8")
        rtvsloHtml.close()
        x = rtvsloData.find('({')
        y = rtvsloData.rfind('});')
        if x < 0 or y < 0:
            xbmcgui.Dialog().ok('RTV Slovenija', 'Strežnik ni posredoval podatkov o podcastu.')
            return
        rtvsloData = rtvsloData[x + 1:y + 1]
        complete_item2 = json.loads(rtvsloData)
        complete_item['response'].update ( complete_item2['response'] )

        try:
            just_response = complete_item['response']
        except KeyError as e:
            return
            
        return just_response

def nodrmcontent(showid):
        # url parameters
        url_query = {}
        url_query['client_id'] = client_id
        url_query['session_id'] = api
        url_query['callback'] = 'jQuery1113023734881856870338_1462389077542'
        url_query['_'] = '1462389077543'

        url = build_url(url_base + 'getRecording/' + showid, url_query)

        # download response from rtvslo api
        rtvsloHtml = urllib.request.urlopen(url)
        rtvsloData = rtvsloHtml.read().decode("utf8")
        rtvsloHtml.close()

        # extract json from response
        x = rtvsloData.find('({')
        y = rtvsloData.rfind('});')
        if x < 0 or y < 0:
            # xbmcgui.Dialog().ok('RTV Slovenija', 'Strežnik ni posredoval podatkov o podcastu.')
            return
        rtvsloData = rtvsloData[x + 1:y + 1]
        complete_item = json.loads(rtvsloData)

        try:
            just_response = complete_item['response']
        except KeyError as e:
            return
            
        return just_response
        
def weekday(day):
    dnevi = ['ponedeljek','torek','sreda','četrtek','petek','sobota','nedelja']
    x = day.weekday()-1
    if x>6:x=x%6
    if x<0:x=x+7
    return dnevi[x]
    
def clear_items():
    cleanup_date = item_retrieve('cleanup_date')
    if cleanup_date[0]:
        if cleanup_date[1] == str(datetime.date.today()):
            return

    cache_size = int(xbmcplugin.getSetting(handle, 'cache_size'))

    for dirpath, dirnames, filenames in os.walk(data_folder):
        for file in filenames:
            if file[0:len(podcast_file)] == podcast_file:
                curpath = os.path.join(dirpath, file)
                file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
                if datetime.datetime.now() - file_modified > datetime.timedelta(days=cache_size):
                    os.remove(curpath)

    item_store('cleanup_date', str(datetime.date.today()))

def item_store(filename, jdata):
    storage_name = filename
    storage_name = storage_name.replace('/', '_')
    storage_name = storage_name.replace(':', '_')
    storage_name = storage_name.replace('.', '_')
    
    storage_name = os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile')),
                              storage_name + '.json')
    with open(storage_name, "w") as debug_file:
        json.dump(jdata, debug_file)


def item_retrieve(filename):
    storage_name = filename
    storage_name = storage_name.replace('/', '_')
    storage_name = storage_name.replace(':', '_')
    storage_name = storage_name.replace('.', '_')
    storage_name = os.path.join(xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile')),
                              storage_name + '.json')

    try:
        with open(storage_name, "r") as s_file:
            jdata = json.load(s_file)
        return True, jdata
    except:
        return False, {}


def do_ListMarkedItems():
    # seznam oddaj za pogledat
    showList = []

    try:
        with open(mark_file, "r") as s_file:
            j = json.load(s_file)
    except:
        return

    j = j['MarkHistory'][contentType]
    if len(j) == 0:
        return

    for showid in j:
        getSingleItem(showid, {'title_style': 'date', 'marked_item': 'True'})


def do_MarkItem():
    # označi oddajo za pogledat
    delete_marked_item(True)

def do_UnMarkItem():
    # odoznači oddajo za pogledat
    delete_marked_item(False)

def do_MainMenu():
    # login
    api = login()

    # ISKANJE
    if hide_search != 'true':
        li = xbmcgui.ListItem('Iskanje')
        url = build_url(base, {'content_type': contentType, 'menu': 'SearchHistory', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # ZAZNAMKI
    if hide_mark != 'true':
        li = xbmcgui.ListItem('Zaznamki')
        url = build_url(base, {'content_type': contentType, 'menu': 'ListMarkedItems', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # ARHIV ODDAJ
    if hide_shows != 'true':
        li = xbmcgui.ListItem('Arhiv oddaj')
        url = build_url(base, {'content_type': contentType, 'menu': 'ShowsArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # ARHIV PRISPEVKOV
    if hide_clips != 'true':
        li = xbmcgui.ListItem('Arhiv prispevkov')
        url = build_url(base, {'content_type': contentType, 'menu': 'ClipsArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # ARHIV PO ABECEDI
    if hide_letters != 'true':
        li = xbmcgui.ListItem('Arhiv po abecedi')
        url = build_url(base, {'content_type': contentType, 'menu': 'ListLetters', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    if contentType == 'audio':
        li = xbmcgui.ListItem('Zvrsti')
        url = build_url(base, {'content_type': contentType, 'menu': 'RadijskeArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    if contentType == 'video':
        li = xbmcgui.ListItem('Arhiv filmov')
        url = build_url(base, {'content_type': contentType, 'menu': 'MovieArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
        
        li = xbmcgui.ListItem('Arhiv dokumentarcev')
        url = build_url(base, {'content_type': contentType, 'menu': 'DokArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
        
        li = xbmcgui.ListItem('Arhiv risank')
        url = build_url(base, {'content_type': contentType, 'menu': 'RisankeArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
        
        li = xbmcgui.ListItem('Arhiv razvedrilnih oddaj')
        url = build_url(base, {'content_type': contentType, 'menu': 'RazvedriloArchive', 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

def RadijskeOddaje(_id,days):
    # maps for genres and sorting
    name = 'Oddaje'
    li = xbmcgui.ListItem('== '+name+' ==' +weekday(list_date+ datetime.timedelta(days=1)) + ' - ' +str(datetime.date.fromordinal((list_date+ datetime.timedelta(days=1)).toordinal() - 1)) + ' ==')
    url = build_url(base, {'content_type': contentType, 'menu': menu, 'ordinal_date': list_date, 'sort': sort,'showId': str(_id), 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['q'] = ''
    url_query['showId'] = str(_id)
    url_query['sort'] = str(sort)
    url_query['order'] = 'desc'
    url_query['pageSize'] = '999'
    url_query['source'] = ''
    url_query['hearingAid'] = '0'
    url_query['clip'] = 'show'
    url_query['from'] = str(list_date+ datetime.timedelta(days=-days))
    url_query['to'] = str(list_date)
    url_query['WPId'] = ''
    url_query['zkp'] = '0'
    url_query['callback'] = 'jQuery11130980077945755083_1462458118383'
    url_query['_'] = '1462458118384'
    url = build_url(url_base + 'getSearch', url_query)

    getItemList(url, {'listType': 'streamlist', 'days': days,'paging_style': 'date'})

def do_ArchiveID(name,_id,days):
    # maps for genres and sorting
    li = xbmcgui.ListItem('== '+name+' ==' +weekday(list_date+ datetime.timedelta(days=1)) + ' - ' +str(datetime.date.fromordinal((list_date+ datetime.timedelta(days=1)).toordinal() - 1)) + ' ==')
    url = build_url(base, {'content_type': contentType, 'menu': menu, 'ordinal_date': list_date, 'sort': sort,'showTypeId': str(_id), 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['q'] = ''
    url_query['showTypeId'] = str(_id)
    url_query['sort'] = str(sort)
    url_query['order'] = 'desc'
    url_query['pageSize'] = '999'
    url_query['source'] = ''
    url_query['hearingAid'] = '0'
    url_query['clip'] = 'show'
    url_query['from'] = str(list_date+ datetime.timedelta(days=-days))
    url_query['to'] = str(list_date)
    url_query['WPId'] = ''
    url_query['zkp'] = '0'
    url_query['callback'] = 'jQuery11130980077945755083_1462458118383'
    url_query['_'] = '1462458118384'
    url = build_url(url_base + 'getSearch', url_query)

    getItemList(url, {'listType': 'streamlist', 'days': days,'paging_style': 'date'})


def do_ShowsArchive():
    # maps for genres and sorting
    li = xbmcgui.ListItem('Zvrsti')
    url = build_url(base, {'content_type': contentType, 'menu': 'ListShowGenres', 'sort': sort, 'api': api})
    #xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Sortiranje')
    url = build_url(base,
                    {'content_type': contentType, 'menu': 'ListShowSortorders', 'showTypeId': showTypeId, 'api': api})
    #xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    
    li = xbmcgui.ListItem('== ' +weekday(list_date+ datetime.timedelta(days=1)) + ' - ' +str(datetime.date.fromordinal((list_date+ datetime.timedelta(days=1)).toordinal() - 1)) + ' ==')
    url = build_url(base, {'content_type': contentType, 'menu': menu, 'ordinal_date': list_date, 'sort': sort,'showTypeId': showTypeId, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['q'] = ''
    url_query['showTypeId'] = str(showTypeId)
    url_query['sort'] = str(sort)
    url_query['order'] = 'desc'
    url_query['pageSize'] = '999'
    url_query['source'] = ''
    url_query['hearingAid'] = '0'
    url_query['clip'] = 'show'
    url_query['from'] = str(list_date)
    url_query['to'] = str(list_date)
    url_query['WPId'] = ''
    url_query['zkp'] = '0'
    url_query['callback'] = 'jQuery11130980077945755083_1462458118383'
    url_query['_'] = '1462458118384'
    url = build_url(url_base + 'getSearch', url_query)

    getItemList(url, {'listType': 'streamlist', 'paging_style': 'date'})


def do_ClipsArchive():
    # maps for genres and sorting
    li = xbmcgui.ListItem('Zvrsti')
    url = build_url(base, {'content_type': contentType, 'menu': 'ListClipGenres', 'sort': sort, 'api': api})
    #xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Sortiranje')
    url = build_url(base,
                    {'content_type': contentType, 'menu': 'ListClipSortorders', 'showTypeId': showTypeId, 'api': api})
    #xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['q'] = ''
    url_query['showTypeId'] = str(showTypeId)
    url_query['sort'] = str(sort)
    url_query['order'] = 'desc'
    url_query['pageSize'] = '999'
    url_query['source'] = ''
    url_query['hearingAid'] = '0'
    url_query['clip'] = 'clip'
    url_query['from'] = str(list_date)
    url_query['to'] = str(list_date)
    url_query['WPId'] = ''
    url_query['zkp'] = '0'
    url_query['callback'] = 'jQuery111307342043845078507_1462458568679'
    url_query['_'] = '1462458568680'
    url = build_url(url_base + 'getSearch', url_query)

    # download response from rtvslo api
    getItemList(url, {'listType': 'streamlist', 'paging_style': 'date'})


def do_ListGenres(nextmenu):
    li = xbmcgui.ListItem('Informativni')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 34, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Športni')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 35, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Izobraževalni')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 33, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Kulturno Umetniški')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 30, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Razvedrilni')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 36, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Verski')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 32, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Otroški')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 31, 'sort': sort, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Mladinski')
    url = build_url(base, {'content_type': contentType, 'menu': nextmenu, 'showTypeId': 15890838, 'sort': sort,
                           'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)


def do_ListSortorders(nextmenu):
    li = xbmcgui.ListItem('Po Datumu')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'sort': 'date', 'showTypeId': showTypeId,
                     'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Po Naslovu')
    url = build_url(base,
                    {'content_type': contentType, 'menu': nextmenu, 'sort': 'title', 'showTypeId': showTypeId,
                     'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    li = xbmcgui.ListItem('Po Popularnosti')
    url = build_url(base, {'content_type': contentType, 'menu': nextmenu, 'sort': 'popularity',
                           'showTypeId': showTypeId, 'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)



def do_Search(search_string, search_type):
    if search_string == '':
        keyboard = xbmc.Keyboard('', 'Iskanje', False)
        keyboard.doModal()
        if not keyboard.isConfirmed() or not keyboard.getText():
            xbmcgui.Dialog().ok('RTV Slovenija', 'Iskanje je prekinjeno')
            return
        search_string = keyboard.getText()

    if search_type < 0:
        search_type = xbmcgui.Dialog().select('Izberi:', ['Iskanje Prispevkov', 'Iskanje Oddaj'])

    if search_type < 0:
        xbmcgui.Dialog().ok('RTV Slovenija', 'Iskanje je prekinjeno')
        return

    # all is set, let's do this
    delete_history_item(search_string, True)
    if type(search_string) == str:
        search_string = search_string.encode('utf-8')

    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['q'] = search_string
    url_query['showTypeId'] = str(showTypeId)
    url_query['sort'] = str(sort)
    url_query['order'] = 'desc'
    url_query['pageSize'] = '12'
    url_query['pageNumber'] = str(page)
    url_query['source'] = ''
    url_query['hearingAid'] = '0'
    if search_type == 0:
        url_query['clip'] = 'clip'
    else:
        url_query['clip'] = 'show'
    url_query['from'] = ''  # '2007-01-01'
    url_query['to'] = ''
    url_query['WPId'] = ''
    url_query['zkp'] = '0'
    url_query['callback'] = 'jQuery111307342043845078507_1462458568679'
    url_query['_'] = '1462458568680'
    url = build_url(url_base + 'getSearch', url_query)

    getItemList(url, {'listType': 'streamlist', 'paging_style': 'page', 'title_style': 'date',
                      'search_string': search_string, 'search_type': search_type})


def do_SearchHistory():
    li = xbmcgui.ListItem('Novo Iskanje')
    li.addContextMenuItems([('Izbriši zgodovino', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                                      'menu': 'DeleteHistory',
                                                                                      'search_string': delete_action,
                                                                                      'api': api})))])
    url = build_url(base, {'content_type': contentType, 'menu': 'Search', 'sort': 'date', 'showTypeId': showTypeId,
                           'api': api})
    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

    try:
        with open(search_history_file, "r") as s_file:
            s_file_data = json.load(s_file)
    except:
        return

    for search_entry in s_file_data.get('SearchHistory', []):
        search_string = search_entry
        search_string = search_string.encode('utf-8')
        li = xbmcgui.ListItem(search_entry)
        li.addContextMenuItems([('Izbriši iskanje', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                                        'menu': 'DeleteHistory',
                                                                                        'search_string': search_string,
                                                                                        'api': api}))),
                                ('Izbriši zgodovino', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                                        'menu': 'DeleteHistory',
                                                                                        'search_string': delete_action,
                                                                                        'api': api})))])
        url = build_url(base, {'content_type': contentType, 'menu': 'Search', 'sort': 'date', 'showTypeId': showTypeId,
                               'searsearch_string': search_string, 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)


def delete_history_item(search_string, also_insert):
    if not also_insert:
        if search_string == delete_action:
            open(search_history_file, 'w').close()
            return

    if type(search_string) != str:
        search_string = search_string.decode('utf-8')

    try:
        with open(search_history_file, "r") as s_file:
            s_file_data = json.load(s_file)
    except:
        s_file_data = {}

    search_list = s_file_data.get('SearchHistory', [])

    try:
        search_list.remove(search_string)
    except:
        pass

    if also_insert:
        search_list.insert(0, search_string)
        search_list = search_list[0:11]

    s_file_data['SearchHistory'] = search_list

    with open(search_history_file, "w") as s_file:
        json.dump(s_file_data, s_file)


def delete_marked_item(also_insert):
    if not also_insert:
        if show_id == delete_action:
            open(mark_file, 'w').close()
            return

    try:
        with open(mark_file, "r") as s_file:
            s_file_data = json.load(s_file)
    except:
        s_file_data = {'MarkHistory': {}}

    mark_list = s_file_data['MarkHistory'].get(contentType, [])

    try:
        mark_list.remove(show_id)
    except:
        pass

    if also_insert:
        mark_list.insert(0, show_id)
        mark_list = mark_list[0:29]

    s_file_data['MarkHistory'][contentType] = mark_list

    with open(mark_file, "w") as s_file:
        json.dump(s_file_data, s_file)


def do_ListShows():
    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['sort'] = 'title'
    url_query['order'] = 'asc'
    url_query['pageSize'] = '100'
    url_query['hidden'] = '0'
    url_query['start'] = letter
    url_query['callback'] = 'jQuery111306175395867148092_1462381908718'
    url_query['_'] = '1462381908719'
    url = build_url(url_base + 'getShowsSearch', url_query)

    # download response from rtvslo api
    getItemList(url, {'listType': 'showlist'})


def do_ListStreams():
    # url parameters
    url_query = {}
    url_query['client_id'] = client_id
    url_query['sort'] = 'date'
    url_query['order'] = 'desc'
    url_query['pageSize'] = '12'
    url_query['pageNumber'] = str(page)
    url_query['from'] = '1991-01-01'
    url_query['clip'] = 'show'
    url_query['showId'] = show_id
    url_query['callback'] = 'jQuery11130007442688502199202_1462387460339'
    url_query['_'] = '1462387460342'
    url = build_url(url_base + 'getSearch', url_query)

    # download response from rtvslo api
    getItemList(url, {'listType': 'streamlist', 'paging_style': 'page', 'title_style': 'date'})


def getSingleItem(showid, _args):
    item_cached = item_retrieve(podcast_file + showid)
    '''
    its_ok = item_cached[0]
    if its_ok:
        try:
            just_response = item_cached[1]
        except KeyError:
            its_ok = False
    '''
    its_ok = False
    if not its_ok:
        try:
            if (drmclip == 'true'):
                just_response = drmcontent(showid)
            else:
                just_response = nodrmcontent(showid)
                
        except Exception as e:
            xbmcgui.Dialog().ok('RTV Slovenija', 'Prišlo je do napake:\n' + e.message)
            pass
        

        #item_store(podcast_file + showid, just_response)

    # parse json to a list of streams
    parseStreamToListEntry(just_response, _args)

def do_getVideo(_id):
    if (drmclip != 'false') and (contentType == 'video'):
        j = drmcontent(args.get('id', [''])[0])
    else:
        j = nodrmcontent(args.get('id', [''])[0])
    try:
            stream_url = j['addaptiveMedia']['hls']
    except KeyError:
            # audio streams and some older video streams have this format
            try:
                if contentType == 'audio':
                    stream_url = j['mediaFiles'][0]['streamers']['http']
                    if stream_url.find('ava_archive02') > 0:
                        stream_url = stream_url.replace("ava_archive02", "podcast/ava_archive02")
                    stream_url = stream_url + '/' + j['mediaFiles'][0]['filename']
                else:
                    mediaArr=j['mediaFiles']
                    media = []
                    for bitrate in mediaArr:
                        media.append ([bitrate['bitrate'],bitrate['streams']['hls']])
                    
                    temp = 0;    
                    for i_ in range(0, len(media)):   
                       for j_ in range(i_+1, len(media)):    
                            if(media[i_][0] < media[j_][0]):    
                                temp = media[i_];    
                                media[i_] = media[j_];    
                                media[j_] = temp;     
                    
                    stream_url = media[0][1]
            except KeyError as e:
                pass
    if stream_url:
        list_item = xbmcgui.ListItem(j.get('title', ''), j['images'].get('orig', ''))
        list_item.setInfo('video', {'duration': j.get('duration','0'),
                                        'title':j.get('title', ''),
                                        'playcount': 0,
                                        'aired': j.get('date',''),
                                        'plot': j.get('description',''),
                                        'plotoutline': j.get('jDescription',''),
                                        'tvjtitle': j.get('title','')})
        list_item.setArt({'thumb': j['images'].get('orig', ''),
                          'poster': j['images'].get('orig', ''),
                          'banner': j['images'].get('orig', ''),
                          'fanart': j['images'].get('orig', ''),
                          'clearart': j['images'].get('fp1', ''),
                          'clearlogo': j['images'].get('fp2', ''),
                          'landscape': j['images'].get('wide1', ''),
                          'icon': j['images'].get('fp3', '')})
        try:
            list_item.setSubtitles([j['subtitles'][0].get('file', '')])
        except KeyError as e:
            pass
        from os import environ
        if 'ANDROID_BOOTLOGO' in environ:
            selection = xbmcgui.Dialog().select('Izberi predvajalnik', ['KODI', 'VLC'])
            if selection == 1:
                xbmc.executebuiltin('StartAndroidActivity("org.videolan.vlc","android.intent.action.VIEW","","'+stream_url+'")')
                exit()
            if selection == 0:
                xbmc.Player().play(stream_url, list_item, windowed=False)
                exit()
        else:
            xbmc.log ("stream : "+stream_url,xbmc.LOGERROR)
            selection = xbmcgui.Dialog().select('Izberi predvajalnik', ['KODI', 'VLC','DOWNLOAD'])
            if selection == 2:
                import subprocess
                proc = subprocess.Popen(["c:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe", "-i", stream_url, "-c", "copy", "-v", "-ac", "2", "-acodec", "aac"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                exit()
            if selection == 1:
                import subprocess
                proc = subprocess.Popen(["c:\\Program Files\\VideoLAN\\VLC\\vlc.exe", stream_url, "--video-on-top", "--play-and-exit" , "--no-qt-bgcone", "--no-qt-name-in-title", "--no-video-title-show", "--qt-minimal-view", "--fullscreen",  "--autoscale"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                exit()
            if selection == 0:
                xbmc.Player().play(stream_url, list_item, windowed=False)
                exit()
        
def getItemList(url, _args):
    rtvsloHtml = urllib.request.urlopen(url)
    rtvsloData = rtvsloHtml.read().decode("utf8")
    rtvsloHtml.close()
    
    # extract json from response
    x = rtvsloData.find('({')
    y = rtvsloData.rfind('});')
    if x < 0 or y < 0:
        xbmcgui.Dialog().ok('RTV Slovenija', 'Strežnik ni posredoval seznama.')
        return
    rtvsloData = rtvsloData[x + 1:y + 1]
    
    # parse json to a list of streams
    if _args.get('listType') == 'showlist':
        parseShowsToShowList(rtvsloData)
    elif _args.get('listType') == 'streamlist':
        parseShowToStreamList(rtvsloData, _args)


def build_url(base, query):
    return base + '?' + urllib.parse.urlencode(query)


def login():
    # get settings
    username = xbmcplugin.getSetting(handle, 'username')
    password = xbmcplugin.getSetting(handle, 'password')
    hide_nagger = xbmcplugin.getSetting(handle, 'hide_nagger')

    if username == '' or password == '':
        if hide_nagger != 'true':
            xbmcgui.Dialog().ok('RTV Slovenija',
                                'Nimate konfigurirane prijave! Nekatere vsebine brez prijave niso dosegljive. Uporabniško ime in geslo lahko brezplačno pridobite na https://moj.rtvslo.si/prijava. Vnos podatkov za prijavo je mogoč v nastavitvah.')
        return

    # no Requests library dependency required...
    url = 'https://4d.rtvslo.si/prijava'
    referurl = 'https://4d.rtvslo.si'
    params = urllib.parse.urlencode({'action': 'login', 'referer': referurl, 'user': username, 'pass': password})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(),
        urllib.request.HTTPCookieProcessor(cookies)
    ]
    opener = urllib.request.build_opener(*handlers)

    req = urllib.request.Request(url, params, headers)
    response = opener.open(req)

    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[str(cookie.name)] = cookie.value

    a = ''
    try:
        a = str(cookies_dict['APISESSION'])
    except KeyError:
        if hide_nagger != 'true':
            xbmcgui.Dialog().ok('RTV Slovenija',
                                'Prijava je neuspešna! Nekatere vsebine brez prijave niso dosegljive. Uporabniško ime in geslo lahko brezplačno pridobite na https://moj.rtvslo.si/prijava. Vnos podatkov za prijavo je mogoč v nastavitvah.')

    return a


def parseShowsToShowList(json_data):
    showList = []
    j = json.loads(json_data)
    j = j['response']['response']

    if len(j) == 0:
        return

    # list shows
    for show in j:
        if (contentType == 'audio' and show['mediaType'] == 'radio') or (
                contentType == 'video' and show['mediaType'] == 'tv'):
            li = xbmcgui.ListItem(show['title'], iconImage=show['thumbnail']['show'])
            url = build_url(base, {'content_type': contentType, 'menu': 'ListStreams', 'page': 0, 'id': show['id'],
                                   'api': api})
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)

def parseShowToStreamList(json_data, _args):
    j = json.loads(json_data)
    j = j['response']['recordings']
    
    #xbmcgui.Dialog().ok('RTV Slovenija', str(json_data))
    # find playlists and list streams
    for show in j:
        #xbmcgui.Dialog().ok('RTV Slovenija', str(show))
        if (contentType == 'audio' and show['mediaType'] == 'audio') or (
                contentType == 'video' and show['mediaType'] == 'video'):
            stream_genre = ''
            try:
                for g in show['broadcast']['genre']:
                    # stream_genre = stream_genre + ',' + g
                    stream_genre = g  # rabimo samo zadnjega
            # stream_genre = stream_genre[1:]
            except KeyError:
                pass
            if _args.get('days') != 0:
                list_title = show.get('date') + ' - ' + show.get('title', '')
            else:
                stream_aired = show.get('broadcastDate', '')
                if stream_aired != '':
                    stream_time = stream_aired[11:16]
                else:
                    stream_time = ''
                list_title = stream_time + ' - ' + show.get('title', '')
            if contentType == 'audio' and show['mediaType'] == 'audio':
                list_title = show['showName'] + "  "+ list_title
            
            list_item = xbmcgui.ListItem(list_title, show['images'].get('orig', ''))
            list_item.setInfo('video', {'duration': show.get('duration','0'),
                                        'genre': stream_genre,
                                        'title':show.get('title', ''),
                                        'playcount': 0,
                                        'aired': show.get('date',''),
                                        'plot': show.get('description',''),
                                        'plotoutline': show.get('showDescription',''),
                                        'tvshowtitle': show.get('title','')})
            list_item.setArt({'thumb': show['images'].get('orig', ''),
                          'poster': show['images'].get('orig', ''),
                          'banner': show['images'].get('orig', ''),
                          'fanart': show['images'].get('orig', ''),
                          'clearart': show['images'].get('fp1', ''),
                          'clearlogo': show['images'].get('fp2', ''),
                          'landscape': show['images'].get('wide1', ''),
                          'icon': show['images'].get('fp3', '')})
            url = build_url(base, {'content_type': contentType, 'menu': 'VideoPlay', 'page': 0, 'id': show['id'],'api': api })
            if _args.get('marked_item') == 'True':
                list_item.addContextMenuItems(
                    [('Izbriši zaznamek', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                        'menu': 'UnMarkItem',
                                                                        'id': show['id'],
                                                                        'api': api}))),
                     ('Izbriši vse zaznamke', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                           'menu': 'UnMarkItem',
                                                                           'id': delete_action,
                                                                           'api': api})))])
            else:
                list_item.addContextMenuItems(
                    [('Poglej kasneje', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                        'menu': 'MarkItem',
                                                                        'listType': 'streamlist',
                                                                        'id': show['id'],
                                                                        'api': api})))])
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=list_item, isFolder=False)
    
    if _args.get('paging_style', '') == 'date':
        #if _args.get('days') == None:
        # previous day
        ordinal_date = list_date.toordinal() - _args.get('days',1)
        li = xbmcgui.ListItem('> ' +weekday(list_date) + ' - ' +str(datetime.date.fromordinal(ordinal_date)) + ' >')
        url = build_url(base, {'content_type': contentType, 'menu': menu, 'ordinal_date': ordinal_date, 'sort': sort,

                               'showTypeId': showTypeId, 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

def parseShowToStreamList_old(json_data, _args):
    j = json.loads(json_data)
    j = j['response']['recordings']

    # find playlists and list streams
    for stream in j:
        if (contentType == 'audio' and stream['mediaType'] == 'audio') or (
                contentType == 'video' and stream['mediaType'] == 'video'):
            getSingleItem(str(stream['id']), {'title_style': _args.get('title_style', 'time')})

    if _args.get('paging_style', '') == 'date':
        # previous day
        ordinal_date = list_date.toordinal() - 1
        li = xbmcgui.ListItem('> ' +weekday(list_date) + ' - ' +str(datetime.date.fromordinal(ordinal_date)) + ' >')
        url = build_url(base, {'content_type': contentType, 'menu': menu, 'ordinal_date': ordinal_date, 'sort': sort,

                               'showTypeId': showTypeId, 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)
    else:
        if len(j) == 0:
           return

        # show next page marker
        page_no = int(page) + 1
        li = xbmcgui.ListItem('> ' + str(page_no) + ' >')
        url = build_url(base, {'content_type': contentType, 'menu': menu, 'page': page_no, 'sort': sort,
                               'search_string': _args.get('search_string', ''),
                               'search_type': _args.get('search_type', -1),

                               'showTypeId': showTypeId, 'api': api})
        xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)


def parseStreamToListEntry(j, _args):
    if len(j) == 0:
        return
    
    typeOK = True
    try:
        if contentType == 'audio' and j['mediaType'] == 'video':
            typeOK = False
        if contentType == 'video' and j['mediaType'] == 'audio':
            typeOK = False
    except Exception:
        pass
    """
    #PETER begin
    
    try:
            if drmclip == 'true':
                typeOK = False
                stream_url = drmcontent(str(j['id']))
                
                #select best quality
                mediaArr=stream_url['mediaFiles']
                media = []
                for bitrate in mediaArr:
                    media.append ([bitrate['bitrate'],bitrate['streams']['hls']])
                
                temp = 0;    
                for i_ in range(0, len(media)):   
                   for j_ in range(i_+1, len(media)):    
                        if(media[i_][0] < media[j_][0]):    
                            temp = media[i_];    
                            media[i_] = media[j_];    
                            media[j_] = temp;     
                
                stream_url = media[0][1]
            
            if (j["geoblocked"] == 1):
                typeOK = False
                stream_url = drmcontent(str(j['id']))
                
                #select best quality
                mediaArr=stream_url['mediaFiles']
                media = []
                for bitrate in mediaArr:
                    media.append ([bitrate['bitrate'],bitrate['streams']['hls']])
                
                temp = 0;    
                for i_ in range(0, len(media)):   
                   for j_ in range(i_+1, len(media)):    
                        if(media[i_][0] < media[j_][0]):    
                            temp = media[i_];    
                            media[i_] = media[j_];    
                            media[j_] = temp;     
                
                stream_url = media[0][1]
                
    except Exception :
            pass
    #PETER end
    """    
    stream_url = ""
    if typeOK:
        # newer video streams usually have this format
        try:
            stream_url = j['addaptiveMedia']['hls']
        except KeyError:
            # audio streams and some older video streams have this format
            try:
                '''
                stream_url = j['mediaFiles'][0]['streamers']['http']
                if stream_url.find('ava_archive02') > 0:
                    stream_url = stream_url.replace("ava_archive02", "podcast/ava_archive02")
                stream_url = stream_url + '/' + j['mediaFiles'][0]['filename']
                '''

                mediaArr=j['mediaFiles']
                media = []
                for bitrate in mediaArr:
                    media.append ([bitrate['bitrate'],bitrate['streams']['hls']])
                
                temp = 0;    
                for i_ in range(0, len(media)):   
                   for j_ in range(i_+1, len(media)):    
                        if(media[i_][0] < media[j_][0]):    
                            temp = media[i_];    
                            media[i_] = media[j_];    
                            media[j_] = temp;     
                
                stream_url = media[0][1]
            except KeyError as e:
                pass

    # list stream
    if stream_url:
        stream_aired = j.get('broadcastDate', '')
        if stream_aired != '':
            stream_time = stream_aired[11:16]
        else:
            stream_time = ''

        stream_genre = ''
        try:
            for g in j['broadcast']['genre']:
                # stream_genre = stream_genre + ',' + g
                stream_genre = g  # rabimo samo zadnjega
        # stream_genre = stream_genre[1:]
        except KeyError:
            pass

        if _args.get('title_style') == 'date':
            list_title = j.get('date') + ' - ' + j.get('title', '')
        else:
            list_title = stream_time + ' - ' + j.get('title', '')

        list_item = xbmcgui.ListItem(list_title, j.get('showName', ''))
        list_item.setArt({'thumb': j['images'].get('orig', ''),
                          'poster': j['images'].get('orig', ''),
                          'banner': j['images'].get('orig', ''),
                          'fanart': j['images'].get('orig', ''),
                          'clearart': j['images'].get('fp1', ''),
                          'clearlogo': j['images'].get('fp2', ''),
                          'landscape': j['images'].get('wide1', ''),
                          'icon': j['images'].get('fp3', '')})

        if contentType == 'audio':
            list_item.setInfo('music', {'duration': j.get('duration', '0'),
                                        'genre': stream_genre,
                                        'title': j.get('title', ''),
                                        'playcount': j.get('views', '')})
        elif contentType == 'video':
            list_item.setInfo('video', {'duration': j.get('duration', '0'),
                                        'genre': stream_genre,
                                        'title': j.get('title', ''),
                                        'playcount': j.get('views', ''),
                                        'aired': stream_aired,
                                        'plot': j.get('description', ''),
                                        'plotoutline': j.get('showDescription', ''),
                                        'tvshowtitle': j.get('showName', '')})

        if _args.get('marked_item') == 'True':
            list_item.addContextMenuItems(
                [('Izbriši zaznamek', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                        'menu': 'UnMarkItem',
                                                                        'id': j['id'],
                                                                        'api': api}))),
                 ('Izbriši vse zaznamke', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                           'menu': 'UnMarkItem',
                                                                           'id': delete_action,
                                                                           'api': api})))])
        else:
            list_item.addContextMenuItems(
                [('Poglej kasneje', 'RunPlugin(%s)' % (build_url(base, {'content_type': contentType,
                                                                        'menu': 'MarkItem',
                                                                        'listType': 'streamlist',
                                                                        'id': j['id'],
                                                                        'api': api})))])
        xbmcplugin.addDirectoryItem(handle=handle, url=stream_url, listitem=list_item)


#######################################
# main
if __name__ == "__main__":
    try:
        # arguments
        Argv = sys.argv
        
        # get add-on base url
        base = str(Argv[0])

        # get add-on handle
        handle = int(Argv[1])
        
        drmclip = xbmcplugin.getSetting(handle, 'drmclip')
        #xbmcgui.Dialog().ok('RTV Slovenija', drmclip)
        hide_search = xbmcplugin.getSetting(handle, 'hide_search')
        hide_mark = xbmcplugin.getSetting(handle, 'hide_mark')
        hide_shows = xbmcplugin.getSetting(handle, 'hide_shows')
        hide_clips = xbmcplugin.getSetting(handle, 'hide_clips')
        hide_letters = xbmcplugin.getSetting(handle, 'hide_letters')

        # CLEANUP
        clear_items()

        # in some cases kodi returns empty sys.argv[2]
        if Argv[2] == '':
            selection = xbmcgui.Dialog().select(
                'Kodi ni posredoval informacije o vrsti vsebine, izberi:', ['TV', 'Radio'])
            if selection == 0:
                Argv[2] = '?content_type=video'
            else:
                Argv[2] = '?content_type=audio'

        # get add-on args
        args = urllib.parse.parse_qs(Argv[2][1:])

        # get content type
        contentType = str(args.get('content_type')[0])
        if contentType == 'audio':
            xbmcplugin.setContent(handle, 'songs')
        elif contentType == 'video':
            xbmcplugin.setContent(handle, 'videos')

        # get menu and other parameters
        api = args.get('api', [''])[0]
        menu = args.get('menu', ['MainMenu'])[0]
        letter = args.get('letter', ['A'])[0]
        show_id = args.get('id', [''])[0]
        page = args.get('page', ['0'])[0]
        showTypeId = args.get('showTypeId', ['0'])[0]
        sort = args.get('sort', ['date'])[0]
        srch_string = args.get('search_string', [''])[0]
        srch_type = args.get('search_type', [-1])[0]

        dateArg = args.get('ordinal_date')
        if dateArg:
            list_date = datetime.date.fromordinal(int(dateArg[0]))
        else:
            list_date = datetime.date.today()
        
        # MENU SYSTEM
        if menu == 'MainMenu':
            do_MainMenu()
        
        elif menu == 'MovieArchive':
            do_ArchiveID('FILMI/SERIJE',"15890841,15890843",30)
        
        elif menu == 'DokArchive':
            do_ArchiveID('Dokumentarci',15890840,30)

        elif menu == 'RisankeArchive':
            do_ArchiveID('RISANKE',31,30)

        elif menu == 'RazvedriloArchive':
            do_ArchiveID('RAZVEDRILO',36,30)

        elif menu == 'ShowsArchive':
            do_ShowsArchive()

        elif menu == 'ListShowGenres':
            do_ListGenres('ShowsArchive')

        elif menu == 'ListShowSortorders':
            do_ListSortorders('ShowsArchive')

        elif menu == 'ClipsArchive':
            do_ClipsArchive()

        elif menu == 'ListClipGenres':
            do_ListGenres('ClipsArchive')

        elif menu == 'ListClipSortorders':
            do_ListSortorders('ClipsArchive')

        elif menu == 'Search':
            do_Search(srch_string, int(srch_type))

        elif menu == 'SearchHistory':
            do_SearchHistory()

        elif menu == 'DeleteHistory':
            delete_history_item(srch_string, False)
            xbmc.executebuiltin('Container.Refresh')

        elif menu == 'ListLetters':
            oddaje = ['A', 'B', 'C', 'Č', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                      'S', 'Š', 'T', 'U', 'V', 'W', 'Z', 'Ž', '0']
            for o in oddaje:
                li = xbmcgui.ListItem(o)
                url = build_url(base, {'content_type': contentType, 'menu': 'ListShows', 'letter': o, 'api': api})
                xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=True)

        elif menu == 'ListShows':
            do_ListShows()

        elif menu == 'ListStreams':
            do_ListStreams()

        elif menu == 'ListMarkedItems':
            do_ListMarkedItems()

        elif menu == 'MarkItem':
            do_MarkItem()

        elif menu == 'UnMarkItem':
            do_UnMarkItem()
            xbmc.executebuiltin('Container.Refresh')

        elif menu == 'VideoPlay':
            do_getVideo(args.get('id', [''])[0])

        elif menu == 'RadijskeArchive':
            RadijskeOddaje('185,155437317,173250989,31057643,182,97041869,173251238,173250817,173250842,173250838',30)
            
        else:
            xbmcgui.Dialog().ok('RTV Slovenija', 'Neznan meni: ' + menu)  # this never happens

        # write contents
        xbmcplugin.endOfDirectory(handle)

    except Exception as e:
        xbmcgui.Dialog().ok('RTV Slovenija', 'Prišlo je do napake:\n' + e.message)

