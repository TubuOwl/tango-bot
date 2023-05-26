import traceback

from datetime import datetime

import cerach as ch

import time

import json

#from keep_alive import keep_alive


def getSTime(x):

    total_seconds = int(time.time()) - int(x)

    intervals = [

        ('year', 60 * 60 * 24 * 365),

        ('month', 60 * 60 * 24 * 30),

        ('day', 60 * 60 * 24),

        ('hour', 60 * 60),

        ('minute', 60),

        ('second', 1)

    ]

    for name, seconds in intervals:

        count = total_seconds // seconds

        if count != 0:

            return f"{count} {name}{'' if count == 1 else 's'} ago."

    return "Just now"

seen = {}

with open("seen.txt", "r") as f:

    for line in f:

        if line.strip():

            record = json.loads(line.strip())

            name = record["name"]

            timestamp = record["time"]

            room_name = record["room"]

            body = record["message"]

            seen[name] = (timestamp, room_name, body)

class Config:

    rooms = ["log-me", "nico-nico"]

    botname = "anggi"

    password = "123456"

    owner = ["gustixa", "tidakterdaftar", "ulnuh"]

    @staticmethod

    def get_prefix(user):

        return ['-'] if user.name in Config.owner else ['?']

class Bot(ch.RoomManager):

    def onInit(self):

        self.setNameColor("000000")

        self.setFontColor("000000")

        self.setFontFace("Consolas")

        self.setFontSize(11)

        self.enableBg()

        self.enableRecording()

        self.active = time.time()

    def log_info(self, message):

        timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

        print(f"[{timestamp}] [INFO] {message}")

    def onConnect(self, room):

        self.log_info(f"Connected to {room.name}")

    def onReconnect(self, room):

        self.log_info(f"Reconnected to {room.name}")

    def onDisconnect(self, room):

        self.log_info(f"Disconnected from {room.name}")

    def onMessage(self, room, user, message):

        try:

            msgdata = message.body.split(" ", 1)

            cmd, args = msgdata[0].lower(), msgdata[1] if len(msgdata) > 1 else ""

            name = user.name

            seen[name] = (room.getLastMessage(ch.User(name)).time, room.getLastMessage(ch.User(name)).room.name, room.getLastMessage(ch.User(name)).body)

            with open("seen.txt", "w") as f:

                for name, (timestamp, room_name, body) in seen.items():

                    record = {

                        "name": name,

                        "time": timestamp,

                        "room": room_name,

                        "message": body

                    }

                    f.write(json.dumps(record) + "\n")

            self.log_info(f"[{room.name}] {user.name.title()}: {message.body}")

            if user == self.user:

                return

            if "@tidakterdaftar" in message.body.lower():

                status = {'online': 'online', 'offline': 'offline', 'app': 'app'}.get(self.pm.track(ch.User("tidakterdaftar"))[1], 'None')

                if self.active <= time.time():

                    self.active = time.time() + (60 * 5)

                    if status == "offline":

                        room.message("Tubu currently offline.")

            if cmd and cmd[0] in Config.get_prefix(user):

                used_prefix = True

                cmd = cmd[1:]

            else:

                used_prefix = False

            if used_prefix and cmd == "say" and args:

                room.message(args, True)

            elif cmd.lower() in ["seen", "history"]:

                name = args.lower()

                if name in seen:

                    timestamp, room_name, body = seen[name]

                    time_ago = getSTime(timestamp)

                    room.message(f"{name.capitalize()} was last seen {time_ago} in {room_name} saying: {body}")

                else:

                    room.message(f"I haven't seen {name.capitalize()}.")

            elif used_prefix and cmd == "eval" and args:

                try:

                    result = eval(args)

                    room.message(str(result))

                except Exception as e:

                    room.message("Error occurred during evaluation: {}".format(str(e)))

            

            elif used_prefix and cmd == "eval" and not args:

                room.message("No expression provided for evaluation.")

        except Exception as e:

            print(traceback.format_exc())

    def onJoin(self, room, user, puid):

        if user.name[0] not in ["!", "#"]:

            self.log_info(f"[{user.name}] joined [{room.name}]")

    def onLeave(self, room, user, puid):

        if user.name[0] not in ["!", "#"]:

            self.log_info(f"[{user.name}] left [{room.name}]")

while True:

    try:

        #keep_alive()

        bot = Bot.run(Config.rooms, Config.botname, Config.password)

    except Exception as error:

        print("Error in easy_start:", error)

