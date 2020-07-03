# -*- python -*-

import os
import string
import re
import subprocess
import json

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

def guess_client_version():
    'Guess iRODS icommands version number'
    lines = DirectOutputIrodsCommand('ienv')([])

    for l in lines:
        if l.startswith('NOTICE: '):
            m = re.match('^NOTICE: Release Version = rods(?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+), API Version = .*$', l)
            if m is not None:
                return [int(d) for d in m.groups()]
        else:
            m = re.match('^irods_version - (?P<major>\d+)\.(?P<minor>\d+)\.(?P<micro>\d+)\w*$', l)
            if m is not None:
                return [int(d) for d in m.groups()]

    return None

def env_file3(pid=None):
    repo = os.path.expanduser(os.path.join("~", ".irods"))
    if pid is None:
        return os.path.join(repo, ".irodsEnv")

    return os.path.join(repo, ".irodsEnv.%d" % pid)

def parse_env3(path=None):
    "parse iRODS iCommands environment files"

    if path is None:
        path = env_file3(os.getpid())
        if not os.path.isfile(path):
            path = env_file3(os.getppid())

    envre = re.compile("^\s*(?P<name>\w+)\s*(=(?P<value1>.*)|\s+[\'\"](?P<value2>.*)[\'\"]|(?P<value3>[^\'\"].*))\s*$")

    ret = {}

    #print "opening", path
    with open(path, 'r') as f:
        for l in f.readlines():
            #print "parsing", l
            m = envre.match(l)
            if m:
                ret[m.group("name")] = m.group("value1") or m.group("value2") or m.group("value3")

    return ret

def env_file4(pid=None):
    repo = os.path.expanduser(os.path.join("~", ".irods"))
    if pid is None:
        return os.path.join(repo, "irods_environment.json")

    return os.path.join(repo, "irods_environment.json.%d" % pid)

def parse_env4(path=None):
    if path is None:
        path = env_file4(os.getpid())
        if not os.path.isfile(path):
            path = env_file4(os.getppid())

    return json.load(open(path, 'r'))

def load_env(pid=None):
    if guess_client_version()[0] >= 4:
        return parse_env4(env_file4(pid))

    return parse_env3(env_file3(pid))

def guess_icwd():
    "guess iCommand working directory"

    icwd = None
    try:
        #try iRODS v3 environment
        icwd = parse_env3()["irodsCwd"]
    except Exception as e:
        try:
            # try iRODS v4 environment
            icwd = parse_env4()['irods_cwd']
        except Exception as e:
            # fallback to icommand
            ipwd = IrodsCommand("ipwd", output_filter = string.strip)
            _retcode, icwd = ipwd()

    return icwd

def guess_user(env = None):
    "guess iCommands iRODS user name" 

    if env is None:
        env = load_env()

    try:
        user = env["irods_user_name"]
    except KeyError:
        user = env["irodsUserName"]

    return user

def guess_zone(env = None):
    "guess iCommands iRODS zone" 

    if env is None:
        env = load_env()

    try:
        zone = env["irods_zone_name"]
    except KeyError:
        zone = env["irodsZone"]

    return zone

def guess_home(env = None):
    "guess iCommands iRODS user home collection" 

    if env is None:
        env = load_env()

    try:
        try:
            home = env["irods_home"]
        except KeyError:
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
        env = load_env()
        if var_name in env:
            var = env[var_name]

    return var
