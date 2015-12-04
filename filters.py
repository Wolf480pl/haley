# encoding: utf-8
#from pymarkovchain import MarkovChain
import os.path, logging, re, random
from time import time
import regices

haley = haley
haley.bffs = ["Wolf480pl"]
haley.mode = False
haley.song = None
haley.send("AWAY :")
#with open(os.path.expanduser("~/.haleyay.txt")) as f:
#    haley.markov_text = f.read()
#haley.markov_db = MarkovChain(os.path.expanduser("~/.haleyay.db"))

ruleenv = regices.Environ(None)
rulemaker = regices.RuleMaker(haley, ruleenv)

@haley.register_filter(-100)
def nofidgot(self, message, friend, channel):
    if friend == "fidgot" or message.startswith("fidgot"): return True
    return False

#@haley.register_filter()
def modeswitch(self, message, friend, channel):
    if ("ACTION taps %s's head" % self.nickname) in message:
        if self.mode:
            self.say(channel or friend, "Leaving Sister Centipede mode.")
            self.send("AWAY :Airi")
        else:
            self.say(channel or friend, "Entering Sister Centipede mode.")
            self.send("AWAY :Sister Centipede")
        self.mode = not self.mode
        return True
    return False

#@haley.register_filter()
def marsay(self, message, friend, channel):
    if not self.mode and self.nickname in message and "say" in message and "something" in message:
        times = re.search("(?P<tim>\d+) times", message)
        if times:
            times = int(times.group("tim"))
        else:
            times = 1
        for t in range(times): self.say(channel or friend, self.markov_db.generateString())
        return True
    return False

@haley.register_filter()
def goodbye(self, message, friend, channel):
    if self.nickname in message and "quit" in message.lower() and (self.mode or "please" in message.lower()):
        if friend in self.bffs:
            if self.mode:
                self.say(channel or friend, "Commencing logout.")
            else:
                self.say(channel or friend, "Okay, %s, see you later!" % friend)
            self.send("QUIT :Bye!")
            self.stopping = True
        else:
            if self.mode:
                self.say(channel or friend, "Insufficent privileges.")
            else:
                self.say(channel or friend, "%s, it's not like you're %s, right? :D" % (friend, self.bff))
        return True
    return False

@haley.register_filter(1)
def tell(self, message, friend, channel):
    if message.startswith(self.nickname):
        if message.split(" ",1)[1].startswith("tell "):
            if friend in self.bffs:
                spl = message.split(" ",3)
                self.say(channel or friend, "%s: %s" % (spl[2], spl[3]))
            else:
                if self.mode:
                    self.say(channel or friend, "Insufficent privileges.")
                else:
                    self.say(channel or friend, "%s, I can't be easily convinced by someone I barely know ;)" % friend)
            return True
    return False

@haley.register_filter(2)
def thanks(self, message, friend, channel):
    if not self.mode and self.nickname in message and ("thanks" in message.lower() or "thank you" in message.lower()):
        self.say(channel or friend, "You're welcome, %s!" % friend)
        return True
    return False

@haley.register_filter()
def how_are_you(self, message, friend, channel):
    if not self.mode and self.nickname in message and ("how are you" in message.lower() or "what's up" in message.lower()):
        self.say(channel or friend, "The business's fine, %s! And you?" % friend)
        return True
    return False

@haley.register_filter()
def hello(self, message, friend, channel):
    if not self.mode and message.lower() == "hi" or (self.nickname in message and "hi" in message.lower().split()):
        self.say(channel or friend, random.choice(["%s! Tutturuuu!","Hello, %s, so it was you making the noise up there!"]) % friend)
        return True
    return False

#@haley.register_filter()
def nanon(self, message, friend, channel):
    if "nano" in message.lower() or "hakase" in message.lower():
        if "nano" in message.lower():
            self.say(channel or friend, "HAKASE"*len(re.findall("nano", message.lower())))
        if "hakase" in message.lower():
            self.say(channel or friend, "NANO"*len(re.findall("hakase", message.lower())))
        return True
    return False

@haley.register_filter(99)
def not_understand(self, message, friend, channel):
    if self.nickname in message:
        if self.mode:
            self.say(channel or friend, "Command not understood.")
        else:
            self.say(channel or friend, random.choice(["Yes, it's me. The Organization's feeding me phony data through %s. El Psy Kongroo.","Hey, %s, I didn't quite get what you mean?"]) % friend)
        return True
    return False

@ruleenv.expose("time")
def ev_time(self, msg):
    return time()

rulemaker.make_rule("faris (.* )?time( .*)?\\?", "$time")
