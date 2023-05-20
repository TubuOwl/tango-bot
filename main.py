import cerach as ch
import sys, time, datetime, re, html
import requests


class config:
  rooms = ["log-me", "nico-nico"]

  botname = ""

  password = ""

  owner = ["tidakterdaftar"]

  def get_prefix(user):
    prefix = ['?']
    me = ['-']
    if user.name in config.owner:
        return me
    else: return prefix

class bot(ch.RoomManager):

  def onInit(self):
    self.setNameColor("000000")
    self.setFontColor("000000")
    self.setFontFace("Consolas")
    self.setFontSize(11)
    self.enableBg()
    self.enableRecording()
    self.active = time.time()
 
  def onConnect(self, room): print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [INFO]Connected to {room.name}")
 
  def onReconnect(self, room): print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [INFO]Reconnected to {room.name}")
 
  def onDisconnect(self, room): print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [INFO]Disconnected to {room.name}")
    
  def onMessage(self, room, user, message):
     try:
        msgdata = message.body.split(" ",1)
        if len(msgdata) > 1:
          cmd, args = msgdata[0], msgdata[1]
        else:
          cmd, args = msgdata[0],""
          cmd=cmd.lower()
        print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [{room.name}] {user.name.title()}: {message.body}")
        if user == self.user: return

        body = message.body
        var = body.split(maxsplit=1)

        if "@tidakterdaftar" in message.body.lower():
          if self.active <= time.time():
            self.active = time.time() + (60*5)
            room.message("Tubu currently afk.")

        if cmd and cmd[0] in config.get_prefix(user):
          used_prefix = True
          cmd = cmd[1:].lower()
        else:
          used_prefix = False

        if used_prefix and cmd in ["say"]:
           if args: room.message(f"{args}", True)

        elif used_prefix and cmd in ["p", "prof"]:
           try:
               args = args.lower() if args else user.name.lower()
               arrange = f"{args[0]}/{args[1]}/{args}" if len(args) != 1 else f"{args}/{args}/{args}"
               status = {'online': 'online', 'offline': 'offline', 'app': 'app'}.get(self.pm.track(ch.User(args))[1], '')
               response = requests.get(f"https://{args}.chatango.com").text
               age = (re.findall('<strong>Age:</strong></span></td><td><span class="profile_text">(.*?)<br /></span></td>', response, re.DOTALL) or ['None'])[0]
               gender = {'M': 'M (Male)', 'F': 'F (Female)'}.get((re.findall('<strong>Gender:</strong></span></td><td><span class="profile_text">(.*?) <br /></span></td>', response, re.DOTALL) or ['None'])[0], 'None')
               location = (re.findall('<strong>Location:</strong></span></td><td><span class="profile_text">(.*?) <br /></span>', response, re.DOTALL) or ['None'])[0]
               about = html.escape(re.sub("<\/?[^>]*>", "", re.sub("<(script|style)(.*?)</(script|style)>", "", re.search('<span class="profile_text"><!-- google_ad_section_start -->(.*?)<!-- google_ad_section_end --></span>', response, re.DOTALL).group(1).replace("\n", "\r"))))
               image = f"https://fp.chatango.com/profileimg/{arrange}/full.jpg - https://fp.chatango.com/profileimg/{arrange}/thumb.jpg"
               room.message(f"User Profile <b>{args}</b>:\r{image}\r<b>Age</b>: {age} | <b>Gender</b>: {gender} | <b>Location</b>: {location}\r<b>Status</b>: {status}\r<b>About</b>: {about}", True)
           except Exception as e:
               room.message(f"Profile Not Found! {e}", True)
            
        elif used_prefix and cmd in ["eval"]:
           if args: room.message(str(eval(args)))

     except Exception as e:
       try:
          et, ev, tb = sys.exc_info()
          if not tb:
              print(str(e))
          while tb:
              lineno = tb.tb_lineno
              fn = tb.tb_frame.f_code.co_filename
              tb = tb.tb_next
              room.message("[Expectation Failed] %s Line %i - %s"% (fn, lineno, str(e)))
       except: print("Error cannot be detected.")
      
  def onJoin(self, room, user, puid):
    if user.name[0] not in ["!", "#"]: print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [{user.name}] joined [{room.name}]")

  def onLeave(self, room, user, puid):
    if user.name[0] not in ["!", "#"]: print(f"[{datetime.datetime.now():%Y-%m-%d %I:%M:%S %p}] [{user.name}] left [{room.name}]")

try:
    bot = bot.run(
        config.rooms, config.botname, config.password
    )
except Exception as error:
    print("Error in easy_start:", error)
