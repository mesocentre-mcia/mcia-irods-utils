# -*- python -*-

import os
import string
import re
import subprocess

class IrodsCommand:
    "An iRODS iCommand wrapper"
    def __init__(self, cmd, opts = [], output_filter = lambda e: e, verbose = False):
        self.cmd = cmd
        self.opts = opts
        self.verbose = verbose
        self.output_filter = output_filter

    def __call__(self, cmdline = []):
        cmdlist = [self.cmd] + self.opts + cmdline

        if self.verbose:
            print "IrodsCommand:", " ".join([self.cmd] + self.opts + [repr(e) for e in cmdline])

        p = subprocess.Popen( cmdlist, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
        output = p.communicate()[0]

        if p.returncode == 0: output = self.output_filter(output)

        return p.returncode, output

def parse_env(path):
    "parse iRODS iCommands environment files"

    envre = re.compile("^\s*(?P<name>\w+)\s*[=\s]\s*['\"]?(?P<value>[^'\"]*[^'\"\s])['\"]?\s*")

    ret = {}

    #print "opening", path
    with open(path, 'r') as f:
        for l in f.readlines():
            #print "parsing", l
            m = envre.match(l)
            if m:
                ret[m.group("name")] = m.group("value")
    return ret

def guess_icwd():
    "guess iCommand working directory"
    pid = os.getpid()
    ppid = os.getppid()

    repo = os.path.expanduser(os.path.join("~", ".irods"))

    icwd = None
    try:
        icwd = parse_env(os.path.join(repo, ".irodsEnv.%d" % pid))["irodsCwd"]
    except:
        try:
            icwd = parse_env(os.path.join(repo, ".irodsEnv.%d" % ppid))["irodsCwd"]
        except:
            pass

    if not icwd:
        ipwd = IrodsCommand("ipwd", output_filter = string.strip)
        retcode, icwd = ipwd()

    return icwd

def guess_user():
    "guess iCommands iRODS user name" 
    envfile = os.path.expanduser(os.path.join("~", ".irods", ".irodsEnv"))

    env = parse_env(envfile)

    try:
        user = env["irodsUserName"]
    except:
        user = os.getlogin()
    return user

def isrel(path):
    "check if path is relative"
    return not path.startswith('/')

