#!/usr/bin/env python2

import socket, argparse, logging, threading, sys, time, re

LOGLEVEL_RECV = 18
LOGLEVEL_SENT = 17

logging.addLevelName(LOGLEVEL_RECV, "RECV")
logging.addLevelName(LOGLEVEL_SENT, "SENT")
logging.basicConfig(level=15, filename="haley.log", format='%(asctime)s %(levelname)s %(message)s')

class Magus(object):
    def __init__(self, haley, func, delta):
        self.haley = haley
        self.func = func
        self.delta = delta
        self.last = time.time()
    def update(self):
        if time.time() - self.last >= self.delta:
            self.last = time.time()
            try:
                self.func(self.haley)
            except:
                self.haley.say(self.haley.channel, str(sys.exc_info()[0]))

privmsg_regex = re.compile(":(?P<origin>[^ ]+) PRIVMSG (?P<target>) :?(?P<msg>.*)")

# I would call it Responder, but hey, we gotta keep the theme :P
class Receiver(threading.Thread):
    def __init__(self, haley, msg):
        threading.Thread.__init__(self)
        self.haley = haley
        self.msg = msg

    def run(self):
        haley = self.haley
        match = privmsg_regex.match(self.msg)
        if not match:
            return
        origin = match.group("origin")
        friend = origin.split('!')[0]
        target = match.group("target")
        message = match.group("msg")
        if friend != haley.nickname:
            if target == haley.nickname or target in haley.channels:
                haley.run_filters(None, friend, message)

class Haley(threading.Thread):
    def __init__(self, host, port, channels, nickname):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        def fixChan(channel):
            if "#" not in channel:
                return "#%s" % channel
            else:
                return channel
        self.channels = map(fixChan, channels)
        self.nickname = nickname
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chrono = []
        self.filters = []
    def add_filter(self, func, priority=1):
        self.filters.append((priority,func))
        self.filters.sort()
    def register_filter(self, priority=1):
        def func_wrapper(func):
            self.add_filter(func, priority)
            return func
        return func_wrapper
    def add_chrono(self, func, delta):
        self.chrono.append(Magus(self, func, delta))
    def register_chrono(self, delta):
        def func_wrapper(func):
            self.add_chrono(func, delta)
            return func
        return func_wrapper
    def run_filters(self, channel, friend, message):
        for fill in self.filters:
            try:
                if fill[1](self, message, friend):
                    break
            except:
                self.say(friend, str(sys.exc_info()[0]))
    def send(self, message):
        for line in message.split("\n"):
            logging.log(LOGLEVEL_SENT, "%s", line)
            self.socket.sendall("%s\r\n" % line)
    def say(self, channel, message):
        for line in message.split("\n"):
            self.send("PRIVMSG %s :%s" % (channel, line))
    def refresh(self):
        self.filters = []
        self.chrono = []
        execfile("filters.py", {"haley": self})
    def run(self):
        self.socket.connect((self.host, self.port))
        buff = ""
        while True:
            rc = self.socket.recv(512).replace("\r", "")
            buff += rc
            while "\n" in buff:
                message = buff.split("\n", 1)[0]
                buff = buff.split("\n",1)[1]
                logging.log(LOGLEVEL_RECV, message)
                if "checking ident" in message.lower():
                    self.send("USER %s %s s: %s" % (self.nickname, self.nickname, self.nickname))
                    self.send("NICK %s" % self.nickname)
                elif "nickname is already in use" in message.lower():
                    self.nickname += "_"
                    self.send("NICK %s" % self.nickname)
                elif message.upper().startswith("PING"):
                    self.send("PONG%s" % message[4:])
                elif message.startswith(":") and ("001 %s :" % self.nickname) in message and "PRIVMSG" not in message.upper():
                    for channel in self.channels:
                        self.send("JOIN %s" % channel)
                    self.refresh()
                elif " PRIVMSG " in message:
                    Receiver(self, message).start()
            for cron in self.chrono: cron.update()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple IRC bot")
    parser.add_argument("hostname", help="IRC server's IP or hostname")
    parser.add_argument("channels", help="Channels to mess with, leading '#' not required")
    parser.add_argument("-p", "--port", default=6667, metavar="port", help="IRC server's port")
    parser.add_argument("-n", "--name", default="hal3y", metavar="name", help="Nickname for the bot to use")
    args = parser.parse_args()
    overlord = Haley(args.hostname, args.port, args.channels.split(','), args.name)
    overlord.start()
    try:
        overlord.join()
    except KeyboardInterrupt: sys.exit()
