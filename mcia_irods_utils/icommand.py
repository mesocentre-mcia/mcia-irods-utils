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

class DirectOutputIrodsCommand( IrodsCommand ):
    "iRODS command wrapper that directly returns output lines from stdout"
    def __call__( self, cmdline = [] ):
        cmdlist = [self.cmd] + self.opts + cmdline

        if self.verbose:
            print "IrodsCommand:", " ".join( [self.cmd] + self.opts + [repr( e ) for e in cmdline] )

        stdout = os.tmpfile()
        p = subprocess.Popen( cmdlist, stdout = stdout, stderr = subprocess.STDOUT )

        p.wait()

        if p.returncode != 0: raise subprocess.CalledProcessError( " ".join( cmdlist ), p.returncode, stdout )

        stdout.seek( 0 )

        for l in stdout:
            yield self.output_filter( l )

def parse_env(path):
    "parse iRODS iCommands environment files"

    envre = re.compile("^\s*(?P<name>\w+)\s*(=(?P<value1>.*)|\s+[\'\"](?P<value2>.*)[\'\"])\s*$")

    ret = {}

    #print "opening", path
    with open(path, 'r') as f:
        for l in f.readlines():
            #print "parsing", l
            m = envre.match(l)
            if m:
                ret[m.group("name")] = m.group("value1") or m.group("value2")
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
        _retcode, icwd = ipwd()

    return icwd

def guess_user(env = None):
    "guess iCommands iRODS user name" 

    if env is None:
        envfile = os.path.expanduser(os.path.join("~", ".irods", ".irodsEnv"))
        env = parse_env(envfile)

    try:
        user = env["irodsUserName"]
    except:
        user = os.getlogin()
    return user

def guess_zone(env = None):
    "guess iCommands iRODS zone" 

    if env is None:
        envfile = os.path.expanduser(os.path.join("~", ".irods", ".irodsEnv"))
        env = parse_env(envfile)

    try:
        zone = env["irodsZone"]
    except:
        zone = "tempZone"
    return zone

def guess_home(env = None):
    "guess iCommands iRODS user home collection" 

    if env is None:
        envfile = os.path.expanduser(os.path.join("~", ".irods", ".irodsEnv"))
        env = parse_env(envfile)

    try:
        home = env["irodsHome"]
    except:
        home = "/".join(["", guess_zone(env), "home", guess_user(env)])
    return home

def expanduser(path):
    if not path.startswith("~"): return path

    path = path[1:]
    if path.startswith("/") or not path: return guess_home() + path

    return "/".join([guess_home(), path])

def isrel(path):
    "check if path is relative"
    return not path.startswith('/')

def getenv( var_name ):
    var = None
    if var_name in os.environ:
        var = os.environ[var_name]
    else:
        envfile = os.path.expanduser( os.path.join( "~", ".irods", ".irodsEnv" ) )
        env = parse_env( envfile )
        if var_name in env:
            var = env[var_name]

    return var
