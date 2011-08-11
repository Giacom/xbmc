import urllib
import urllib2
import simplejson
import xbmcplugin
import xbmcgui
import shelve

API_PATH = 'http://api.giantbomb.com'
API_KEY = 'e5529a761ee3394ffbd237269966e9f53a4c7bf3'

def CATEGORIES():
    d = shelve.open('local')
    if d.has_key('api_key'):
        global API_KEY
        API_KEY = d['api_key']
    d.close()

    response = urllib2.urlopen(API_PATH + '/video_types/?api_key=' + API_KEY + '&format=json')
    category_data = simplejson.loads(response.read())['results']
    response.close()

    name = 'Latest'
    url = API_PATH + '/videos/?api_key=' + API_KEY + '&sort=-publish_date&format=json'
    iconimage = ''
    addDir(name, url, 2, '')

    for cat in category_data:
        name = cat['name']
        url = API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=' + str(cat['id']) + '&sort=-publish_date&format=json'
        iconimage = ''
        if str(cat['id']) == '5':
            addDir(name, '5', 1, '')
        else:
            addDir(name, url, 2, '')

    name = 'Search'
    iconimage = ''
    addDir(name, 'search', 1, '')

    name = 'Register'
    iconimage = ''
    addDir(name, 'register', 1, '')

def GET_API_KEY(access_code):
    if access_code and len(access_code) == 6:
        try:
            response = urllib2.urlopen(API_PATH + '/validate?api_key=' + API_KEY + '&format=json')
            data = simplejson.loads(response.read())
            api_key = data['api_key']
            d = shelve.open('local')
            d['api_key'] = api_key
            d.close()
        except:
            pass

    CATEGORIES()

def INDEX(url):
    if url == 'search':
        keyboard = xbmc.Keyboard("", 'Search', False)
        keyboard.doModal()
        if keyboard.isConfirmed():
            query = keyboard.getText().replace(' ', '%20')
            url = API_PATH + '/search/?api_key=' + API_KEY + '&resources=video&query=' + query + '&format=json'
            VIDEOLINKS(url, 'search')

    elif url == 'register':
        keyboard = xbmc.Keyboard("", 'Access Code', False)
        keyboard.doModal()
        if keyboard.isConfirmed():
            access_code = keyboard.getText().upper()
            GET_API_KEY(access_code)
    else:
        addDir('Deadly Premonition', url + '&DP', 2, '')
        addDir('Persona 4', url + '&P4', 2, '')
        addDir('The Matrix Online: Not Like This', url + '&MO', 2, '')

def VIDEOLINKS(url, name):
    if url.endswith('&DP'):
        response = urllib2.urlopen(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=161&format=json')
        video_data = simplejson.loads(response.read())['results']
        response.close()
    elif url.endswith('&P4'):
        response = urllib2.urlopen(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&format=json')
        video_data = simplejson.loads(response.read())['results']
        response.close()

        response = urllib2.urlopen(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=100&limit=61&format=json')
        video_data += simplejson.loads(response.read())['results']
        response.close()

        video_data = [video for video in video_data if not video['name'].startswith('The Matrix Online')]
    elif url.endswith('&MO'):
        response = urllib2.urlopen(API_PATH + '/videos/?api_key=' + API_KEY + '&video_type=5&offset=105&limit=21&format=json')
        video_data = simplejson.loads(response.read())['results']
        response.close()

        video_data = [video for video in video_data if video['name'].startswith('The Matrix Online')]
    else:
        response = urllib2.urlopen(url)
        video_data = simplejson.loads(response.read())['results']
        response.close()

    for vid in video_data:
        name = vid['name']
        if 'hd_url' in vid:
            url = vid['hd_url'] + '&api_key=' + API_KEY
        else:
            url = vid['high_url']
        thumbnail = vid['image']['super_url']
        addLink(name,url,thumbnail)

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]

    return param

def addLink(name, url, iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name, url, mode, iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
    print ""
    CATEGORIES()

elif mode==1:
    print ""+url
    INDEX(url)

elif mode==2:
    print ""+url
    VIDEOLINKS(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
