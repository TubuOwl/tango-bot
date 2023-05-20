################################################################
# Original By : Lumirayz/Lumz lumirayz@gmail.com
# Edited By : Agunq
# Use python3 because python2 is discontinued :(
# Require websocket-client module 
#	pip install websocket-client
################################################################

import websocket
import random
import re
import time
import urllib.request
import urllib.parse
import select
import threading

VERSION = "maddnes :s v2"
BigMessage_Multiple = 0
BigMessage_Cut      = 1

class Struct:
  def __init__(self, **entries):
    self.__dict__.update(entries)

MessageFlags = {
    "PREMIUM" : 1 << 2 ,
    "BG_ON" : 1 << 3 ,
    "MEDIA_ON" : 1 << 4 ,
    "CENSORED" : 1 << 5 ,
    "SHOW_MOD_ICON" : 1 << 6 ,
    "SHOW_STAFF_ICON" : 1 << 7 ,
    "CHANNEL_RED" : 1 << 8 ,
    "CHANNEL_ORANGE" : 1 << 9 ,
    "CHANNEL_GREEN" : 1 << 10 ,
    "CHANNEL_CYAN" : 1 << 11 ,
    "CHANNEL_BLUE" : 1 << 12 ,
    "CHANNEL_PURPLE" : 1 << 13 ,
    "CHANNEL_PINK" : 1 << 14 ,
    "CHANNEL_MOD" : 1 << 15 
    }

RoomFlags = {
    "LIST_TAXONOMY" : 1 << 0 ,
    "NO_ANONS" : 1 << 2 ,
    "NO_FLAGGING" : 1 << 3 ,
    "NO_COUNTER" : 1 << 4 ,
    "NO_IMAGES" : 1 << 5 ,
    "NO_LINKS" : 1 << 6 ,
    "NO_VIDEOS" : 1 << 7 ,
    "NO_STYLED_TEXT" : 1 << 8 ,
    "NO_LINKS_CHATANGO" : 1 << 9 ,
    "NO_BROADCAST_MSG_WITH_BW" : 1 << 10 ,
    "RATE_LIMIT_REGIMEON" : 1 << 11 ,
    "CHANNELS_DISABLED" : 1 << 13 ,
    "NLP_SINGLEMSG" : 1 << 14 ,
    "NLP_MSGQUEUE" : 1 << 15 ,
    "BROADCAST_MODE" : 1 << 16 ,
    "CLOSED_IF_NO_MODS" : 1 << 17 ,
    "IS_CLOSED" : 1 << 18 ,
    "SHOW_MOD_ICONS" : 1 << 19 ,
    "MODS_CHOOSE_VISIBILITY" : 1 << 20 ,
    "NLP_NGRAM" : 1 << 21 ,
    "NO_PROXIES" : 1 << 22 ,
    "HAS_XML" : 1 << 28 ,
    "UNSAFE" : 1 << 29 
    }

ModeratorFlags = {
    "DELETED" : 1 << 0 ,
    "EDIT_MODS" :  1 << 1 ,
    "EDIT_MOD_VISIBILITY" : 1 << 2 ,
    "EDIT_BW" : 1 << 3 ,
    "EDIT_RESTRICTIONS" : 1 << 4 ,
    "EDIT_GROUP" : 1 << 5 ,
    "SEE_COUNTER" : 1 << 6 ,
    "SEE_MOD_CHANNEL" : 1 << 7 ,
    "SEE_MOD_ACTIONS" : 1 << 8 ,
    "EDIT_NLP" : 1 << 9 ,
    "EDIT_GP_ANNC" : 1 << 10 ,
    "EDIT_ADMINS" : 1 << 11 ,
    "EDIT_SUPERMODS" : 1 << 12 ,
    "NO_SENDING_LIMITATIONS" : 1 << 13 ,
    "SEE_IPS" : 1 << 14 ,
    "CLOSE_GROUP" : 1 << 15 ,
    "CAN_BROADCAST" : 1 << 16 ,
    "MOD_ICON_VISIBLE" : 1 << 17 ,
    "IS_STAFF" : 1 << 18 ,
    "STAFF_ICON_VISIBLE" : 1 << 19 ,
    "UNBAN_ALL" : 1 << 20
    }


def getFlag(n, FlagSet):
    if n <= 0: return {}
    newflag = FlagSet
    f = FlagSet.values()
    c = 0
    bit = n
    newset = {}
    while bit != 0:
        bit >>= 1
        c += 1
        tv = 1 << c
        if tv not in f:
            newflag[str(tv)] = tv
    
    for flag, number in newflag.items():
        if n & number :
            newset[flag] = number
         
    return newset

specials = {'tango-hyoo': 60,
            'monosekai': 76,
            'nico-nico': 29
            }

tsweights = [['5', 75], ['6', 75], ['7', 75], ['8', 75], ['16', 75], ['17', 75], ['18', 75], ['9', 95], ['11', 95], ['12', 95], ['13', 95], ['14', 95], ['15', 95], ['19', 110], ['23', 110], ['24', 110], ['25', 110], ['26', 110], ['28', 104], ['29', 104], ['30', 104], ['31', 104], ['32', 104], ['33', 104], ['35', 101], ['36', 101], ['37', 101], ['38', 101], ['39', 101], ['40', 101], ['41', 101], ['42', 101], ['43', 101], ['44', 101], ['45', 101], ['46', 101], ['47', 101], ['48', 101], ['49', 101], ['50', 101], ['52', 110], ['53', 110], ['55', 110], ['57', 110], ['58', 110], ['59', 110], ['60', 110], ['61', 110], ['62', 110], ['63', 110], ['64', 110], ['65', 110], ['66', 110], ['68', 95], ['71', 116], ['72', 116], ['73', 116], ['74', 116], ['75', 116], ['76', 116], ['77', 116], ['78', 116], ['79', 116], ['80', 116], ['81', 116], ['82', 116], ['83', 116], ['84', 116]]

def getServer(group):
  try:
    sn = specials[group]
  except KeyError:
    group = group.replace("_", "q")
    group = group.replace("-", "q")
    fnv = float(int(group[0:min(5, len(group))], 36))
    lnv = group[6: (6 + min(3, len(group) - 5))]
    if(lnv):
      lnv = float(int(lnv, 36))
      lnv = max(lnv,1000)
    else:
      lnv = 1000
    num = (fnv % lnv) / lnv
    maxnum = sum(map(lambda x: x[1], tsweights))
    cumfreq = 0
    sn = 0
    for wgt in tsweights:
      cumfreq += float(wgt[1]) / maxnum
      if(num <= cumfreq):
        sn = int(wgt[0])
        break
  return "s" + str(sn) + ".chatango.com"

def genUid():
  return str(random.randrange(10 ** 15, 10 ** 16))

def clean_message(msg):
  n = re.search("<n(.*?)/>", msg)
  if n: n = n.group(1)
  f = re.search("<f(.*?)>", msg)
  if f: f = f.group(1)
  msg = re.sub("<n.*?/>", "", msg)
  msg = re.sub("<f.*?>", "", msg)
  msg = strip_html(msg)
  msg = msg.replace("&lt;", "<")
  msg = msg.replace("&gt;", ">")
  msg = msg.replace("&quot;", "\"")
  msg = msg.replace("&apos;", "'")
  msg = msg.replace("&amp;", "&")
  return msg, n, f

def strip_html(msg):
    msg = re.sub("<\/?[^>]*>", "", msg)
    return msg

def parseNameColor(n):
  return n

def parseFont(f):
  try:
    sizecolor, fontface = f.split("=", 1)
    sizecolor = sizecolor.strip()
    size = int(sizecolor[1:3])
    col = sizecolor[3:6]
    if col == "": col = None
    face = f.split("\"", 2)[1]
    return col, face, size
  except:
    return None, None, None

def getAnonId(n, ssid):
  if n == None: n = "5504"
  try:
    return "".join(list(
      map(lambda x: str(x[0] + x[1])[-1], list(zip(
        list(map(lambda x: int(x), n)),
        list(map(lambda x: int(x), ssid[4:]))
      )))
    ))
  except ValueError:
    return "NNNN"

class PM:
  def __init__(self, mgr):
    self._auth_re = re.compile(r"auth\.chatango\.com ?= ?([^;]*)", re.IGNORECASE)
    self._connected = False
    self._reconnecting = False
  
    self._mgr = mgr
    self._auid = None
    self._premium = False
    self._blocklist = set()
    self._contacts = set()
    self._status = dict()
    self._wlock = False
    self._firstCommand = True
    self._wbuf = ""
    self._wlockbuf = ""
    self._pingTask = None

    if self._mgr:
      self._connect()

  def _getAuth(self, name, password):
    data = urllib.parse.urlencode({
      "user_id": name,
      "password": password,
      "storecookie": "on",
      "checkerrors": "yes"
    }).encode()
    try:
      resp = urllib.request.urlopen("https://chatango.com/login", data)
      headers = resp.headers
    except Exception:
      return None
    for header, value in headers.items():
      if header.lower() == "set-cookie":
        m = self._auth_re.search(value)
        if m:
          auth = m.group(1)
          if auth == "":
            return None
          return auth
    return None

  def _auth(self):
    self._auid = self._getAuth(self._mgr.name, self._mgr.password)
    if self._auid == None:
      self._websock.close()
      self._callEvent("onLoginFail")
      return False
    self._sendCommand("tlogin", self._auid, "2")
    self._setWriteLock(True)
    return True

  def connect(self):
    self._connect()

  def _connect(self):
    self._websock = websocket.WebSocket()
    self._websock.connect('wss://%s:%s/' % (self._mgr._PMHost, self._mgr._PMPort), origin='https://st.chatango.com', header = { "Pragma" : "no-cache", "Cache-Control" : "no-cache" })
    if not self._auth(): return
    self._pingTask = self.mgr.setInterval(self.mgr._pingDelay, self.ping)
    
  def attemptReconnect(self):
    try:
      print("try reconect PM attempt %s" %  (self._attempt))
      self._reconnect()
    except:
      time.sleep(10)
      self._attempt -= 1
      if self._attempt > 0:
        self.attemptReconnect()
      else:
        print("failed to reconnect PM")
        self.disconnect()
    
      
  def reconnect(self):
    self._attempt = 3
    self.attemptReconnect()
  
  def _reconnect(self):
    self._reconnecting = True
    if self._connected:
      self._disconnect()
    self._connect()   
    self._reconnecting = False
    self._callEvent("onPMReconnect")
    
  def disconnect(self):
    self._disconnect()
    self._callEvent("onPMDisconnect")

  def _disconnect(self):
    self._connected = False
    self._pingTask.cancel()
    self._websock.close()

  def _feed(self, data):
    data = data.split(b"\x00")
    for food in data:
      self._process(food.decode(errors="replace").rstrip("\r\n").replace("&#39;", "'"))

  def _process(self, data):
    self._callEvent("onRaw", data)
    data = data.split(":")
    cmd, args = data[0], data[1:]
    #print(cmd, args)
    func = "rcmd_" + cmd
    if hasattr(self, func):
      getattr(self, func)(args)

  def getManager(self): return self._mgr
  def getContacts(self): return self._contacts
  def getBlocklist(self): return self._blocklist

  mgr = property(getManager)
  contacts = property(getContacts)
  blocklist = property(getBlocklist)

  def rcmd_OK(self, args):
    self._connected = True
    self._setWriteLock(False)
    self._sendCommand("wl")
    self._sendCommand("getblock")
    self._sendCommand("getpremium", "1")
    self._callEvent("onPMConnect")

  def rcmd_wl(self, args):
    self._contacts = set()
    for i in range(len(args) // 4):
      name, last_on, is_on, idle = args[i * 4: i * 4 + 4]
      user = User(name)
      if last_on=="None":pass
      elif is_on == "off": self._status[user] = [int(last_on), "offline", 0]
      elif is_on == "app": self._status[user] = [int(last_on), "app", 0]
      elif idle == '0' and is_on == "on": self._status[user] = [int(last_on), "online", 0]
      else: self._status[user] = [int(last_on), "online", time.time() - int(idle) * 60]
      self._contacts.add(user)
    self._callEvent("onPMContactlistReceive")

  def rcmd_wladd(self, args):
    name, is_on, last_on = args
    user = User(name)
    if is_on == "on":
      if last_on == '0':
        idle = 0
      else:
        idle = time.time() - int(last_on) * 60
      last_on = 0
      is_on = "online"
    elif is_on == "app":
      if last_on == '0':
        idle = 0
      else:
        idle = time.time() - int(last_on) * 60
      last_on = 0
      is_on = "app"
    else:
      idle = 0
      if last_on == "None":
        last_on = 0
      else:
        last_on = int(last_on)
      is_on = "offline"
    self._status[user] = [last_on, is_on, idle]
    if user not in self._contacts:
      self._contacts.add(user)
    self._callEvent("onPMContactAdd", user)

  def rcmd_wldelete(self, args):
    user = User(args[0])
    if user in self._contacts:
      self._contacts.remove(user)
    self._callEvent("onPMContactRemove", user)

  def rcmd_block_list(self, args):
    self._blocklist = set()
    for name in args:
      if name == "": continue
      self._blocklist.add(User(name))

  def rcmd_idleupdate(self, args):
    user = User(args[0])
    if user in self._status:
      last_on, is_on, idle = self._status[user]  
    if args[1] == '1':
      self._status[user] = [last_on, is_on, 0]
    else:
      self._status[user] = [last_on, is_on, time.time()]

  def rcmd_track(self, args):
    user = User(args[0])
    is_on = args[2]
    if is_on == "online":
      if args[1] == '0':
        idle = 0
      else:
        idle = time.time() - float(args[1]) * 60
      last_on = idle
    else:
      last_on = float(args[1])
      idle = 0
    self._status[user] = [last_on, is_on, idle]

  def rcmd_status(self, args): 
    user = User(args[0])
    is_on = args[2]
    if is_on == "online":
      if args[1] == '0':
        idle = 0
      else:
        idle = time.time() - float(args[1]) * 60
      last_on = idle
    else:
      last_on = float(args[1])
      idle = 0
    self._status[user] = [last_on, is_on, idle]

  def rcmd_connect(self, args): 
    user = User(args[0])
    is_on = args[2]
    if is_on == "online":
      if args[1] == '0':
        idle = 0
      else:
        idle = time.time() - float(args[1]) * 60
      last_on = idle
    else:
      last_on = float(args[1])
      idle = 0
    self._status[user] = [last_on, is_on, idle]

  def rcmd_DENIED(self, args):
    self._disconnect()
    self._callEvent("onLoginFail")

  def rcmd_msg(self, args):
    user = User(args[0])
    body = strip_html(":".join(args[5:]))
    self._callEvent("onPMMessage", user, body)

  def rcmd_msgoff(self, args):
    user = User(args[0])
    body = strip_html(":".join(args[5:]))
    self._callEvent("onPMOfflineMessage", user, body)

  def rcmd_wlonline(self, args):
    user = User(args[0])
    last_on = float(args[1])
    self._status[user] = [last_on,"online",last_on]
    self._callEvent("onPMContactOnline", user)

  def rcmd_wlapp(self, args):
    user = User(args[0])
    last_on = float(args[1])
    self._status[user] = [last_on,"app",last_on]
    self._callEvent("onPMContactApp", user)

  def rcmd_wloffline(self, args):
    user = User(args[0])
    last_on = float(args[1])
    self._status[user] = [last_on,"offline",0]
    self._callEvent("onPMContactOffline", user)

  def rcmd_premium(self, args):
    if float(args[1]) > time.time():
      self._premium = True
      self.setBgMode(1)
      self.setRecordingMode(1)
    else:
      self._premium = False

  def rcmd_kickingoff(self, args):
    self.disconnect()

  def rcmd_toofast(self, args):
    self.disconnect()

  def rcmd_unblocked(self, user):
    if user in self._blocklist:
      self._blocklist.remove(user)
      self._callEvent("onPMUnblock", user)

  def ping(self):
    self._sendCommand("")
    self._callEvent("onPMPing")

  def message(self, user, msg):
    if msg!=None:
      msg = "<n%s/><m v=\"1\"><g x%ss%s=\"%s\">%s</g></m>" % (self._mgr.user.nameColor.lower(), self._mgr.user.fontSize, self._mgr.user.fontColor.lower(), self._mgr.user.fontFace, msg)
      self._sendCommand("msg", user.name, msg)

  def addContact(self, user):
    if user not in self._contacts:
      self._sendCommand("wladd", user.name)

  def removeContact(self, user):
    if user in self._contacts:
      self._sendCommand("wldelete", user.name)

  def block(self, user):
    if user not in self._blocklist:
      self._sendCommand("block", user.name, user.name, "S")
      self._blocklist.add(user)
      self._callEvent("onPMBlock", user)

  def unblock(self, user):
    if user in self._blocklist:
      self._sendCommand("unblock", user.name)

  def setBgMode(self, mode):
    self._sendCommand("msgbg", str(mode))

  def setRecordingMode(self, mode):
    self._sendCommand("msgmedia", str(mode))

  def setIdle(self):
    self._sendCommand("idle:0")

  def setActive(self):
    self._sendCommand("idle:1")

  def rawTrack(self, user):
    cmd = self._sendCommand("track" , user.name)
    self._websock.send(cmd)
    op, data = self._websock.recv_data()
    if(len(data) > 0):
      self._feed(data)
  
  def track(self, user):
    self.rawTrack(user)
    return self._status[user]

  def checkOnline(self, user):
    if user in self._status:
      return self._status[user][1]
    else:
      return None

  def getIdle(self, user):
    if not user in self._status: return None
    if not self._status[user][1]: return 0
    if not self._status[user][2]: return time.time()
    else: return self._status[user][2]

  def _callEvent(self, evt, *args, **kw):
    getattr(self.mgr, evt)(self, *args, **kw)
    self.mgr.onEventCalled(self, evt, *args, **kw)

  def _write(self, data):
    if self._wlock:
      self._wlockbuf += data
    else:
      self._wbuf += data

  def _setWriteLock(self, lock):
    self._wlock = lock
    if self._wlock == False:
      self._write(self._wlockbuf)
      self._wlockbuf = ""
      
  def _sendCommand(self, *args):
    if self._firstCommand:
      terminator = "\x00"
      self._firstCommand = False
    else:
      terminator = "\r\n\x00"
    cmd = ":".join(args) + terminator
    self._write(cmd)
    return cmd
  
class Room:
  def __init__(self, room, uid = None, server = None, port = None, mgr = None):
    self._name = room
    self._server = server or getServer(room)
    self._port = port or 8081 #1800/8080
    self._mgr = mgr
    self._wlock = False
    self._firstCommand = True
    self._wbuf = ""
    self._wlockbuf = ""
    self._connected = False
    self._reconnecting = False
    self._uid = uid or genUid()
    self._channel = "0"
    self._owner = None
    self._mods = dict()
    self._mqueue = dict()
    self._history = list()
    self._status = dict()
    self._connectAmmount = 0
    self._premium = False
    self._userCount = 0
    self._pingTask = None
    self._users = dict()
    self._msgs = dict()
    self._silent = False
    self._banlist = dict()
    self._unbanlist = dict()
    self._bannedwords = list()
    
    if self._mgr:
      self._mgr._rooms[self.name] = self
      self._connect()

  def getMessage(self, mid):
    return self._msgs.get(mid)
  
  def createMessage(self, msgid, **kw):
    if msgid not in self._msgs:
      msg = Message(msgid = msgid, **kw)
      self._msgs[msgid] = msg
    else:
      msg = self._msgs[msgid]
    return msg

  def connect(self):
    self.connect()

  def _connect(self):
    self._websock = websocket.WebSocket()
    self._websock.connect('wss://%s:%s/' % (self._server, self._port), origin='https://st.chatango.com', header = { "Pragma" : "no-cache", "Cache-Control" : "no-cache" })
    self._auth()
    self._pingTask = self.mgr.setInterval(self.mgr._pingDelay, self.ping)


  def attemptReconnect(self):
    try:
      print("try reconect %s attempt %s" %  (self.name, self._attempt))
      self._reconnect()
    except:
      time.sleep(10)
      self._attempt -= 1
      if self._attempt > 0:
        self.attemptReconnect()
      else:
        print("failed to reconnect %s" % self.name)
        self.disconnect()
      
  def reconnect(self):
    self._attempt = 3
    self.attemptReconnect()
  
  def _reconnect(self):
    self._reconnecting = True
    if self._connected:
      self._disconnect()
    self._connect()
    self._reconnecting = False
  
  def disconnect(self):
    self._disconnect()
    self._callEvent("onDisconnect")
  
  def _disconnect(self):
    self._connected = False
    self._pingTask.cancel()
    self._websock.close()
    if not self._reconnecting:
      if self.name in self.mgr._rooms:
        del self.mgr._rooms[self.name]
    
  def _auth(self):
    if self._mgr._name and self._mgr._password:
      self._sendCommand("bauth", self._name, self._uid, self._mgr._name, self._mgr._password)
    else:
      self._sendCommand("bauth", self._name, self._uid)
    self._setWriteLock(True)
      
  def login(self, name, password=None):
    if password != None:
      self._sendCommand("blogin", name, password)
    else:
      self._sendCommand("blogin", name)

  def logout(self):
    self._sendCommand("blogout")

  def getName(self): return self._name
  def getManager(self): return self._mgr
  def getUserlist(self):
    ul = []
    for data in self._status.values():
      user = data[0]
      if user not in ul:
          ul.append(user)
    return ul

  def _getUserlist(self):
    ul = []
    for data in self._status.values():
      user = data[0]
      if user.name[0] not in ["!", "#"]:
        ul.append(user)
    return ul
    
  def getUserNames(self):
    ul = self.getUserlist()
    return list(map(lambda x: x.name, ul))

  def getOwner(self): return self._owner
  def getOwnerName(self): return self._owner.name
  def getMods(self):
    newset = set()
    for mod in self._mods.keys():
      newset.add(mod)
    return newset
  def getModNames(self):
    mods = self._mods.keys()
    newset = list()
    for x in mods:
      newset.append(x.name)
    return newset
  def getUserCount(self):
    if self._userCount == 0:
      return len(self.getUserlist())
    else:
      return self._userCount
  def getSilent(self): return self._silent
  def setSilent(self, val): self._silent = val
  def getBanlist(self): return list(self._banlist.keys())
  def getUnBanlist(self): return [(record["target"], record["src"]) for record in self._unbanlist.values()]
  def getBannedWords(self): return self._bannedwords
  def getFlags(self): return self._flags
    
  name = property(getName)
  mgr = property(getManager)
  userlist = property(getUserlist)
  _userlist = property(_getUserlist)
  usernames = property(getUserNames)
  owner = property(getOwner)
  ownername = property(getOwnerName)
  mods = property(getMods)
  modnames = property(getModNames)
  usercount = property(getUserCount)
  silent = property(getSilent, setSilent)
  banlist = property(getBanlist)
  unbanlist = property(getUnBanlist)
  bannedwords = property(getBannedWords)
  flags = property(getFlags)
 
  def _feed(self, data):
    data = data.split(b"\x00")
    for food in data:
      self._process(food.decode(errors="replace").rstrip("\r\n").replace("&#39;", "'"))
      
  def _process(self, data):
    self._callEvent("onRaw", data)
    data = data.split(":")
    cmd, args = data[0], data[1:]
    #print(cmd, args)
    func = "rcmd_" + cmd
    if hasattr(self, func):
      getattr(self, func)(args)

  def rcmd_ok(self, args):
    self._connected = True
    self._attempt = 0
    if args[2] == "C" and self._mgr._password == None and self._mgr._name == None:
      n = args[4].rsplit('.', 1)[0]
      n = n[-4:]
      pid = args[1][0:8]
      name = "!anon" + getAnonId(n, pid)
      self._mgr.user._nameColor = n
    elif args[2] == "C" and self._mgr._password == None:
      self.login(self._mgr._name)
    elif args[2] != "M": 
      self._callEvent("onLoginFail")
      self.disconnect()
    self._owner = User(args[0])
    self._uid = args[1]
    self._aid = args[1][4:8]
    if len(args[6]) > 0:
      self._mods = dict((x,y) for x, y in list(map(lambda x: (User(x.split(",")[0]), getFlag(int(x.split(",")[1]), ModeratorFlags)), args[6].split(";"))))
    self._flags = getFlag(int(args[7]), RoomFlags)
    self._i_log = list()

  def rcmd_groupflagsupdate(self, args):
    old_flags = set(self._flags.items())
    self._flags = getFlag(int(args[0]), RoomFlags)
    new_flags = set(self._flags.items())
    add_flags = new_flags - old_flags
    if len(add_flags) > 0:
      self._callEvent("onGroupFlagsAdded", dict(add_flags))
      
    remove_flags = old_flags - new_flags
    if len(remove_flags) > 0:
      self._callEvent("onGroupFlagsRemoved", dict(remove_flags))
      
    self._callEvent("onGroupFlagsUpdate")
  
  def rcmd_denied(self, args):
    self._disconnect()
    self._callEvent("onConnectFail")
  
  def rcmd_inited(self, args):
    self._sendCommand("g_participants", "start")
    self._sendCommand("getpremium", "1")
    self._sendCommand("getbannedwords")
    self._sendCommand("getratelimit")
    self.requestBanlist()
    self.requestUnBanlist()
    if self._connectAmmount == 0:
      self._callEvent("onConnect")
      for msg in reversed(self._i_log):
        user = msg.user
        self._callEvent("onHistoryMessage", user, msg)
        self._addHistory(msg)
      del self._i_log
    else:
      self._callEvent("onReconnect")
    self._connectAmmount += 1
    self._setWriteLock(False)

  def rcmd_getratelimit(self, args):
    pass

  def rcmd_bw(self, args):
    for word in args:
      words = urllib.parse.unquote(word).split(",") 
      for word in words:
        if word not in self._bannedwords and len(word) > 0:  
            self._bannedwords.append(word)
    bannedwords = self._bannedwords
    self._callEvent("onBannedWordsUpdated", bannedwords)
  
  def rcmd_premium(self, args):
    if float(args[1]) > time.time():
      self._premium = True
      if self._mgr.user._mbg: self.setBgMode(1)
      if self._mgr.user._mrec: self.setRecordingMode(1)
    else:
      self._premium = False
  
  def rcmd_mods(self, args):
    modnames = args
    mods = dict((x, y) for x, y in list(map(lambda x: (User(x.split(",")[0]), getFlag(int(x.split(",")[1]), ModeratorFlags)), modnames)))
    curmods = mods.keys()
    premods = self._mods.keys()
    for user in curmods - premods: #modded
      self._callEvent("onModAdd", user)
    for user in premods - curmods: #demodded
      self._callEvent("onModRemove", user)
    self._callEvent("onModChange")
    self._mods = mods
  
  def rcmd_b(self, args):
    mtime = float(args[0])
    channel = args[7]
    puid = args[3]
    ip = args[6]
    name = args[1]
    rawmsg = ":".join(args[8:])
    msg, n, f = clean_message(rawmsg)
    if name == "":
      nameColor = None
      name = "#" + args[2]
      if name == "#":
        name = "!anon" + getAnonId(n, puid)
    else:
      if n: nameColor = parseNameColor(n)
      else: nameColor = None
    i = args[5]
    unid = args[4]
    user = User(name)
    if puid:
      user.updatePuid(puid)
    if f: fontColor, fontFace, fontSize = parseFont(f)
    else: fontColor, fontFace, fontSize = None, None, None
    msg = Message(
      time = mtime,
      channel = channel,
      user = user,
      body = msg[1:],
      raw = rawmsg[1:],
      uid = puid,
      ip = ip,
      nameColor = nameColor,
      fontColor = fontColor,
      fontFace = fontFace,
      fontSize = fontSize,
      unid = unid,
      room = self
    )
    self._mqueue[i] = msg
  
  def rcmd_u(self, args):
    temp = Struct(**self._mqueue)
    if hasattr(temp, args[0]):
      msg = getattr(temp, args[0])
      if msg.user != self.mgr.user:
        msg.user._fontColor = msg.fontColor
        msg.user._fontFace = msg.fontFace
        msg.user._fontSize = msg.fontSize
        msg.user._nameColor = msg.nameColor
      del self._mqueue[args[0]]
      msg.attach(self, args[1])
      self._addHistory(msg)
      self._channel = msg.channel
      self._callEvent("onMessage", msg.user, msg)
  
  def rcmd_i(self, args):
    mtime = float(args[0])
    channel = args[7]
    puid = args[3]
    ip = args[6]
    if ip == "": ip = None
    name = args[1]
    rawmsg = ":".join(args[8:])
    msg, n, f = clean_message(rawmsg)
    msgid = args[5]
    if name == "":
      nameColor = None
      name = "#" + args[2]
      if name == "#":
        name = "!anon" + getAnonId(n, puid)
    else:
      if n: nameColor = parseNameColor(n)
      else: nameColor = None
    if f: fontColor, fontFace, fontSize = parseFont(f)
    else: fontColor, fontFace, fontSize = None, None, None
    user = User(name)
    if puid:
      user.updatePuid(puid)
    msg = self.createMessage(
      msgid = msgid,
      time = mtime,
      channel = channel,
      user = user,
      body = msg,
      raw = rawmsg,
      ip = args[6],
      unid = args[4],
      nameColor = nameColor,
      fontColor = fontColor,
      fontFace = fontFace,
      fontSize = fontSize,
      room = self
    )
    self._i_log.append(msg)
  
  def rcmd_g_participants(self, args):
    args = ":".join(args)
    args = args.split(";")
    for data in args:
      data = data.split(":")
      sid = data[0]
      usertime = float(data[1])
      name = data[3]
      puid = data[2]
      if name.lower() == "none":
          n = str(int(usertime))[-4:]
          if data[4].lower() == "none":
            name = "!anon" + getAnonId(n, puid)
          else:
            name = "#" + data[4] 
      user = User(name)
      if puid:
        user.updatePuid(puid)
      user.addSessionId(self, sid)
  
      if sid not in self._status:
        self._status[sid] = [user, usertime, data[2], data[3], data[4]]
  
  def rcmd_participant(self, args):
    name = args[3]
    sid = args[1]
    usertime = float(args[6])
    puid = args[2]
    if name.lower() == "none":
      n = str(int(usertime))[-4:]
      if args[4].lower() == "none":
        name = "!anon" + getAnonId(n, puid)
      else:
        name = "#" + args[4] 
    user = User(name)
    if puid:
      user.updatePuid(puid)
    if args[0] == "0": #leave
      user.removeSessionId(self, sid)
      if sid in self._status:
        del self._status[sid]
        self._callEvent("onLeave", user, puid)
        
    if args[0] == "1" or args[0] == "2": #join
      user.addSessionId(self, sid)
      self._status[sid] = [user, usertime, args[2], args[3], args[4]]
      self._callEvent("onJoin", user, puid)

        
  def rcmd_show_fw(self, args):
    self._callEvent("onFloodWarning")
  
  def rcmd_show_tb(self, args):
    self._callEvent("onFloodBan")
  
  def rcmd_tb(self, args):
    self._callEvent("onFloodBanRepeat")
  
  def rcmd_delete(self, args):
    msg = self.getMessage(args[0])
    if msg:
      if msg in self._history:
        self._history.remove(msg)
        self._callEvent("onMessageDelete", msg.user, msg)
        msg.detach()
  
  def rcmd_deleteall(self, args):
    for msgid in args:
      self.rcmd_delete([msgid])
  
  def rcmd_n(self, args):
    self._userCount = int(args[0], 16)
    self._callEvent("onUserCountChange")
  
  def rcmd_blocklist(self, args):
    self._banlist = dict()
    sections = ":".join(args).split(";")
    for section in sections:
      params = section.split(":")
      if len(params) != 5: continue
      if params[2] == "": continue
      user = User(params[2])
      self._banlist[user] = {
        "unid":params[0],
        "ip":params[1],
        "target":user,
        "time":float(params[3]),
        "src":User(params[4])
      }
    self._callEvent("onBanlistUpdate")

  def rcmd_unblocklist(self, args):
    self._unbanlist = dict()
    sections = ":".join(args).split(";")
    for section in sections:
      params = section.split(":")
      if len(params) != 5: continue
      if params[2] == "": continue
      user = User(params[2])
      self._unbanlist[user] = {
        "unid":params[0],
        "ip":params[1],
        "target":user,
        "time":float(params[3]),
        "src":User(params[4])
      }
    self._callEvent("onUnBanlistUpdate")
  
  def rcmd_blocked(self, args):
    if args[2] == "": return
    target = User(args[2])
    user = User(args[3])
    self._banlist[target] = {"unid":args[0], "ip":args[1], "target":target, "time":float(args[4]), "src":user}
    self._callEvent("onBan", user, target)
    self.requestBanlist()
  
  def rcmd_unblocked(self, args):
    if args[2] == "": return
    target = User(args[2])
    user = User(args[3])
    try:
       del self._banlist[target]
    except:
      return
    self._unbanlist[user] = {"unid":args[0], "ip":args[1], "target":target, "time":float(args[4]), "src":user}
    self._callEvent("onUnban", user, target)
    self.requestUnBanlist()

  def ping(self):
    self._sendCommand("")
    self._callEvent("onPing")
  
  def rawMessage(self, channel, msg):
    msg = "<n" + self._mgr.user.nameColor + "/>" + msg
    msg = "<f x%0.2i%s=\"%s\">" %(self._mgr.user.fontSize, self._mgr.user.fontColor, self._mgr.user.fontFace) + msg
    if not self._silent:
      self._sendCommand("bm", "tl2r", channel, msg)

  def message(self, msg, html = False, channel = None):
    if msg == None:
      return
    if not html:
      msg = msg.replace("<", "&lt;").replace(">", "&gt;")
    if len(msg) > self.mgr._maxLength:
      if self.mgr._tooBigMessage == BigMessage_Cut:
        self.message(msg[:self.mgr._maxLength], html = html)
      elif self.mgr._tooBigMessage == BigMessage_Multiple:
        while len(msg) > 0:
          sect = msg[:self.mgr._maxLength]
          msg = msg[self.mgr._maxLength:]
          self.message(sect, html = html)
      return
    if channel == None:
        channel = self._channel
    self.rawMessage(channel, msg)
  
  def setBgMode(self, mode):
    self._sendCommand("msgbg", str(mode))
  
  def setRecordingMode(self, mode):
    self._sendCommand("msgmedia", str(mode))

  def addBadWord(self, word):
    if self.getLevel(self._mgr.user) == 2:
      self._bannedwords.append(word)
      self._sendCommand("setbannedwords", "403", ", ".join(self._bannedwords))
       
  def removeBadWord(self, word):
    if self.getLevel(self._mgr.user) == 2:
      self._bannedwords.remove(word)
      self._sendCommand("setbannedwords", "403", ", ".join(self._bannedwords))

  def addMod(self, user):
    if self.getLevel(self._mgr.user) == 2:
      self._sendCommand("addmod", user.name)
    
  def removeMod(self, user):
    if self.getLevel(self._mgr.user) == 2:
      self._sendCommand("removemod", user.name)
  
  def flag(self, message):
    self._sendCommand("g_flag", message.msgid)
  
  def flagUser(self, user):
    msg = self.getLastMessage(user)
    if msg:
      self.flag(msg)
      return True
    return False
  
  def delete(self, message):
    if self.getLevel(self._mgr.user) > 0:
      self._sendCommand("delmsg", message.msgid)
  
  def rawClearUser(self, unid, ip, user):
    self._sendCommand("delallmsg", unid, ip, user)
  
  def clearUser(self, user):
    if self.getLevel(self._mgr.user) > 0:
      msg = self.getLastMessage(user)
      if msg:
        if user.name[0] in ["!","#"]:
          username = ""
        else:
          username = user.name
        self.rawClearUser(msg.unid, msg.ip, username)
      return True
    return False
  
  def clearall(self):
    self._sendCommand("clearall")
    if self.getLevel(self._mgr.user) == 1:
      for msg in self._history:
        self.clearUser(msg.user)
    self._callEvent("onClearAll")
    
  
  def rawBan(self, name, ip, unid):
    self._sendCommand("block", unid, ip, name)
  
  def ban(self, msg):
    if self.getLevel(self._mgr.user) > 0:
      if msg.user.name[0] in ["!","#"]:
        username = ""
      else:
        username = msg.user.name
      self.rawBan(username, msg.ip, msg.unid)
  
  def banUser(self, user):
    msg = self.getLastMessage(user)
    if msg:
      self.ban(msg)
      return True
    return False
  
  def requestBanlist(self):
    self._sendCommand("blocklist", "block", "", "next", "500")
    
  def requestUnBanlist(self):
    self._sendCommand("blocklist", "unblock", "", "next", "500")
  
  def rawUnban(self, name, ip, unid):
    self._sendCommand("removeblock", unid, ip, name)
  
  def unban(self, user):
    rec = self._getBanRecord(user)
    if rec:
      self.rawUnban(rec["target"].name, rec["ip"], rec["unid"])
      return True
    else:
      return False

  def _getBanRecord(self, user):
    if user in self._banlist:
      return self._banlist[user]
    return None
  
  def _callEvent(self, evt, *args, **kw):
    getattr(self.mgr, evt)(self, *args, **kw)
    self.mgr.onEventCalled(self, evt, *args, **kw)

  def _write(self, data):
    if self._wlock:
      self._wlockbuf += data
    else:
      self._wbuf += data

  def _setWriteLock(self, lock):
    self._wlock = lock
    if self._wlock == False:
      self._write(self._wlockbuf)
      self._wlockbuf = ""
      
  def _sendCommand(self, *args):
    if self._firstCommand:
      terminator = "\x00"
      self._firstCommand = False
    else:
      terminator = "\r\n\x00"
    self._write(":".join(args) + terminator)
    
  def getLevel(self, user):
    if user == self._owner: return 2
    if user in self._mods: return 1
    return 0

  def getBadge(self, msg):
    channel = int(msg.channel)
    badge = getFlag(channel, MessageFlags)
    if "SHOW_MOD_ICON" in badge.keys() or "SHOW_STAFF_ICON" in badge.keys():
      return 1
    else:
      return 0
  
  def getLastMessage(self, user = None):
    if user:
      try:
        i = 1
        while True:
          msg = self._history[-i]
          if msg.user == user:
            return msg
          i += 1
      except IndexError:
        return None
    else:
      try:
        return self._history[-1]
      except IndexError:
        return None
    return None
  
  def findUser(self, name):
    name = name.lower()
    ul = self.getUserlist()
    udi = dict(zip([u.name for u in ul], ul))
    cname = None
    for n in udi.keys():
      if n.find(name) != -1:
        if cname: return None 
        cname = n
    if cname: return udi[cname]
    else: return None

  def _addHistory(self, msg):
    self._history.append(msg)
    if self.getBadge(msg) > 0:
      if msg.user not in self._mods.keys() and msg.user != self._owner:
        self._mods[msg.user] = {}
    if len(self._history) > self.mgr._maxHistoryLength:
      rest, self._history = self._history[:-self.mgr._maxHistoryLength], self._history[-self.mgr._maxHistoryLength:]
      for msg in rest:
        msg.detach()
  
class RoomManager:
  _Room = Room
  _PM = PM
  _PMHost = "c1.chatango.com"
  _PMPort = 8081 #1800/8080
  _pingDelay = 20
  _tooBigMessage = BigMessage_Multiple
  _maxLength = 2800
  _maxHistoryLength = 150

  def __init__(self, name = None, password = None, pm = True):
    self._name = name
    self._password = password
    self._tasks = set()
    self._rooms = dict()
    self._running = False
    if pm:
      conn = self._PM(mgr = self)
      self._pm = conn
    else:
      self._pm = None

  def joinThread(self, room):
    self._Room(room, mgr = self)
    
  def joinRoom(self, room):
    room = room.lower()
    if room not in self._rooms:
      self.joinThread(room)

  def leaveRoom(self, room):
    room = room.lower()
    if room in self._rooms:
      con = self._rooms[room]
      con.disconnect()

  def getRoom(self, room):
    room = room.lower()
    if room in self._rooms:
      return self._rooms[room]
    else:
      return None
  
  def getUser(self): return User(self._name)
  def getName(self): return self._name
  def getPassword(self): return self._password
  def getRooms(self): return set(self._rooms.values())
  def getRoomNames(self): return set(self._rooms.keys())
  def getPM(self): return self._pm
  
  user = property(getUser)
  name = property(getName)
  password = property(getPassword)
  rooms = property(getRooms)
  roomnames = property(getRoomNames)
  pm = property(getPM)
  
  def onInit(self):
    pass
  
  def onConnect(self, room):
    pass
  
  def onReconnect(self, room):
    pass
  
  def onConnectFail(self, room):
    pass
  
  def onDisconnect(self, room):
    pass
  
  def onLoginFail(self, room):
    pass

  def onGroupFlagsUpdate(self, room):
    pass

  def onGroupFlagsAdded(self, room, flags):
    pass

  def onGroupFlagsRemoved(self, room, flags):
    pass
  
  def onFloodBan(self, room):
    pass
  
  def onFloodBanRepeat(self, room):
    pass
  
  def onFloodWarning(self, room):
    pass
  
  def onMessageDelete(self, room, user, message):
    pass
  
  def onModChange(self, room):
    pass
  
  def onModAdd(self, room, user):
    pass
	
  def onClearAll(self, room):
    pass
  
  def onModRemove(self, room, user):
    pass
  
  def onMessage(self, room, user, message):
    pass

  def onBannedWordsUpdated(self, room, words):
    pass
  
  def onHistoryMessage(self, room, user, message):
    pass
  
  def onJoin(self, room, user, puid):
    pass
  
  def onLeave(self, room, user, puid):
    pass
  
  def onRaw(self, room, raw):
    pass
  
  def onPing(self, room):
    pass
  
  def onUserCountChange(self, room):
    pass
  
  def onBan(self, room, user, target):
    pass
  
  def onUnban(self, room, user, target):
    pass
  
  def onBanlistUpdate(self, room):
    pass

  def onUnBanlistUpdate(self, room):
    pass
  
  def onPMConnect(self, pm):
    pass
  
  def onPMReconnect(self, pm):
    pass
  
  def onPMDisconnect(self, pm):
    pass
  
  def onPMPing(self, pm):
    pass
  
  def onPMMessage(self, pm, user, body):
    pass
  
  def onPMOfflineMessage(self, pm, user, body):
    pass
  
  def onPMContactlistReceive(self, pm):
    pass
  
  def onPMBlocklistReceive(self, pm):
    pass
  
  def onPMContactAdd(self, pm, user):
    pass
  
  def onPMContactRemove(self, pm, user):
    pass
  
  def onPMBlock(self, pm, user):
    pass
  
  def onPMUnblock(self, pm, user):
    pass
  
  def onPMContactOnline(self, pm, user):
    pass

  def onPMContactApp(self, pm, user):
    pass
  
  def onPMContactOffline(self, pm, user):
    pass
  
  def onEventCalled(self, room, evt, *args, **kw):
    pass
   
  class _Task:
    def cancel(self):
      self.mgr.removeTask(self)
  
  def _tick(self):
    now = time.time()
    for task in set(self._tasks):
      if task.target <= now:
        task.func(*task.args, **task.kw)
        if task.isInterval:
          task.target = now + task.timeout
        else:
          self._tasks.remove(task)
  
  def setTimeout(self, timeout, func, *args, **kw):
    task = self._Task()
    task.mgr = self
    task.target = time.time() + timeout
    task.timeout = timeout
    task.func = func
    task.isInterval = False
    task.args = args
    task.kw = kw
    self._tasks.add(task)
    return task
  
  def setInterval(self, timeout, func, *args, **kw):
    task = self._Task()
    task.mgr = self
    task.target = time.time() + timeout
    task.timeout = timeout
    task.func = func
    task.isInterval = True
    task.args = args
    task.kw = kw
    self._tasks.add(task)
    return task
  
  def removeTask(self, task):
    self._tasks.remove(task)

  @classmethod
  def run(cl, rooms = None, name = None, password = None, pm = True):
    try:
      if not rooms: rooms = str(input("Room names separated by semicolons: ")).split(";")
      if len(rooms) == 1 and rooms[0] == "": rooms = []
      if name == None: name = str(input("User name: "))
      if name == "" or " " in name: name = None
      if password == None: password = str(input("User password: "))
      if password == "": password = None
      if name == None or password == None: pm = False
      self = cl(name, password, pm = pm)
      self.rooms_copy = rooms
      if len(self.rooms_copy)>0:
        for room in self.rooms_copy:
          self.joinRoom(room)
      self.main()
    except Exception as e:
      print(str(e))
      
  def main(self):
    self.onInit()
    self._running = True
    while self._running:
      conns = list(self._rooms.values())
      if self.pm:
        conns.append(self.pm)
      socks = [x._websock.sock for x in conns if x._websock.sock != None ]
      wsocks = [x._websock.sock for x in conns if x._wbuf != "" and x._websock.sock != None]
      rd, wr, sp = select.select(socks, wsocks, [], 0.1)
      for sock in rd:
        con = [c for c in conns if c._websock.sock == sock][0]
        try:
          op, data = con._websock.recv_data()
          if(len(data) > 0):
            #print(data)
            con._feed(data)
       
        except Exception as e:
          print(str(e))
          #pass
          con.reconnect()
          
      for sock in wr:
        con = [c for c in conns if c._websock.sock == sock][0]
        try:
          size = con._websock.send(con._wbuf)
          con._wbuf = con._wbuf[size:]
        except Exception as e:
          print(str(e))
          #pass
          con.reconnect()
        
        
      self._tick()
      
  def stop(self):
    self._running = False
    conns = list(self._rooms.values())
    if self.pm:
      conns.append(self.pm)
    for conn in conns:
      conn.disconnect()

  def enableBg(self):
    self.user._mbg = True
    for room in self.rooms:
      room.setBgMode(1)
  
  def disableBg(self):
    self.user._mbg = False
    for room in self.rooms:
      room.setBgMode(0)
  
  def enableRecording(self):
    self.user._mrec = True
    for room in self.rooms:
      room.setRecordingMode(1)
  
  def disableRecording(self):
    self.user._mrec = False
    for room in self.rooms:
      room.setRecordingMode(0)
  
  def setNameColor(self, color3x):
    self.user._nameColor = color3x
  
  def setFontColor(self, color3x):
    self.user._fontColor = color3x
  
  def setFontFace(self, face):
    self.user._fontFace = face
  
  def setFontSize(self, size):
    if size < 9: size = 9
    if size > 22: size = 22
    self.user._fontSize = size


_users = dict()
def User(name):
  if name == None: name = ""
  user = _users.get(name.lower())
  if not user:
    user = _User(name)
    _users[name.lower()] = user
  return user
  
class _User:
  def __init__(self, name):
    self._name = name.lower()
    self._raw = name
    self._puid = ""
    self._sids = dict()
    self._msgs = list()
    self._nameColor = "000"
    self._fontSize = 12
    self._fontFace = "0"
    self._fontColor = "000"
    self._mbg = False
    self._mrec = False
  
  def getName(self): return self._name
  def getRaw(self): return self._raw
  def getPuid(self): return self._puid
  def getSessionIds(self, room = None):
    if room:
      return self._sids.get(room, set())
    else:
      return set.union(*self._sids.values())
  def getRooms(self): return self._sids.keys()
  def getRoomNames(self): return [room.name for room in self.getRooms()]
  def getFontColor(self): return self._fontColor
  def getFontFace(self): return self._fontFace
  def getFontSize(self): return self._fontSize
  def getNameColor(self): return self._nameColor
  
  name = property(getName)
  raw = property(getRaw)
  puid = property(getPuid)
  sids = property(getSessionIds)
  rooms = property(getRooms)
  roomnames = property(getRoomNames)
  fontColor = property(getFontColor)
  fontFace = property(getFontFace)
  fontSize = property(getFontSize)
  nameColor = property(getNameColor)
  
  def addSessionId(self, room, sid):
    if room not in self._sids:
      self._sids[room] = set()
    self._sids[room].add(sid)
  
  def removeSessionId(self, room, sid):
    try:
      self._sids[room].remove(sid)
      if len(self._sids[room]) == 0:
        del self._sids[room]
    except KeyError:
      pass
  
  def clearSessionIds(self, room):
    try:
      del self._sids[room]
    except KeyError:
      pass
  
  def hasSessionId(self, room, sid):
    try:
      if sid in self._sids[room]:
        return True
      else:
        return False
    except KeyError:
      return False

  def updatePuid(self, puid):
    self._puid = puid
  
  def __repr__(self):
    return "<User: %s>" %(self.name)

class Message:
  def attach(self, room, msgid):
    if self._msgid == None:
      self._room = room
      self._msgid = msgid
      self._room._msgs[msgid] = self
  
  def detach(self):
    if self._msgid != None and self._msgid in self._room._msgs:
      del self._room._msgs[self._msgid]
      self._msgid = None
  
  def __init__(self, **kw):
    self._msgid = None
    self._time = None
    self._channel = None
    self._user = None
    self._body = None
    self._room = None
    self._raw = ""
    self._ip = None
    self._unid = ""
    self._nameColor = "000"
    self._fontSize = 12
    self._fontFace = "0"
    self._fontColor = "000"
    for attr, val in kw.items():
      if val == None: continue
      setattr(self, "_" + attr, val)
  
  def getId(self): return self._msgid
  def getTime(self): return self._time
  def getChannel(self): return self._channel
  def getUser(self): return self._user
  def getBody(self): return self._body
  def getUid(self): return self._uid
  def getIP(self): return self._ip
  def getFontColor(self): return self._fontColor
  def getFontFace(self): return self._fontFace
  def getFontSize(self): return self._fontSize
  def getNameColor(self): return self._nameColor
  def getRoom(self): return self._room
  def getRaw(self): return self._raw
  def getUnid(self): return self._unid
  
  msgid = property(getId)
  time = property(getTime)
  channel = property(getChannel)
  user = property(getUser)
  body = property(getBody)
  uid = property(getUid)
  room = property(getRoom)
  ip = property(getIP)
  fontColor = property(getFontColor)
  fontFace = property(getFontFace)
  fontSize = property(getFontSize)
  raw = property(getRaw)
  nameColor = property(getNameColor)
  unid = property(getUnid)
