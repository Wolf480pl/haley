import re

#_escape_regex = re.compile("\\\\(.)")
_escape_regex = "\\\\(?P<chr>.)"
_var_regex = "(?P<pre>^|[^\\\\](?:[\\\\]{2})*)\\$(?P<var>[a-zA-Z0-9_]+)(?:\\{(?P<args>[^}]*)\\})?"
_var_or_escape_regex = re.compile("(?:%s)|(?:%s)" % (_escape_regex, _var_regex))

#def unescape(sth):
#    return re.sub(_escape_regex, "\\1", sth)

class Environ:
    def __init__(self, context, parent=None):
        self.parent = parent
        self.env = {}
        self.context = context

    def put(self, name, value):
        self.env[name] = value

    def expose(self, name):
        def wrap_expose(func):
            self.put(name, func)
            return func
        return wrap_expose

    def lookup(self, name):
        if name in self.env:
            return self.env[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def evaluate(self, expr):
        def ev(match):
            if match.group("chr"):
                return match.group("chr")
            name = match.group("var")
            value = self.lookup(name)
            if callable(value):
                value = value(self.context, match.group("args"))
            out = str(value)
            if match.group("pre"):
                out = match.group("pre") + out
            return out
        return re.sub(_var_or_escape_regex, ev, expr)

class MatchEnviron(Environ):
    def __init__(self, context, match, parent=None):
        Environ.__init__(self, context, parent)
        self.match = match

    def lookup(self, name):
        match = self.match
        if match:
            try:
                return match.group(name)
            except IndexError:
                pass
        return Environ.lookup(self, name)

class RuleMaker:
    def __init__(self, haley, env):
        self.haley = haley
        self.env = env

    def make_rule(self, regex, expr, prio=1, flags=''):
        stop = not 'p' in flags
        regex = re.compile(regex)
        def filt(haley, message, friend):
            match = regex.match(message)
            if not match:
                return False
            env = MatchEnviron(haley, match, self.env)
            env.put("user", friend)
            env.put("msg", message)
            haley.say(env.evaluate(expr))
            return stop
        self.haley.add_filter(filt, prio)
