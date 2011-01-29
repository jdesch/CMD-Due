#!/usr/bin/env python
# encoding: utf-8
"""
handler.py

Created by Justin Deschenes on 2011-01-27.
Copyright (c) 2011 . All rights reserved.
"""

import sys
import os
import gzip
import plistlib
import time

from dateutil import tz
from datetime import *
from subprocess import call
from Foundation import NSMutableDictionary

help_message = '''
The help message goes here.
'''

FNAME = "Sync.dueappgz"
NAME = "Sync"
CNAME = "$classname"
CLASS = "$class"
CF = "CF$UID"

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
    path = argv[-1]
    lookahead = 3
    if len(argv) > 1:
        lookahead = int(argv[0])
    
    if os.path.isdir(path):
        if os.path.basename(path):
            path += "/"
    
    f = gzip.open(path + FNAME, 'rb')
    content = f.read()
    f.close()
    del(f)
    f = open(path + NAME, 'w')
    f.writelines(content)
    f.close()
    del(f)
    os.system("plutil -convert xml1 '%s'" % path+NAME )
    f= os.popen("echo `date +%z`")
    utc = f.readline()
    f.close()
    del(f)
    u = format_utc(utc)
    p = plistlib.Plist.fromFile(path+NAME)
    l = getClasses("Reminder", p["$objects"])
    l = filter_list(l, u, lookahead)
    l.sort()
    for o in l:
        print "[%s] %s - %s" % (o[1], o[2], o[3])

def filter_list(l, utc, args):
    ret = []
    for o in l:
        if o.status == 1:
            dt = get_date(o.dateDue, utc)
            if comp_now(dt, args, utc):
                ret.append(format(o.name, dt))
    return ret

def format(name, date):
    day = date.strftime("%a") + ". " + date.strftime("%b") + " " + date.strftime("%d")
    time = date.strftime("%I") + ":" + date.strftime("%M") + date.strftime("%p")
    sortval = int(date.strftime("%y") + date.strftime("%j") + date.strftime("%H") + date.strftime("%H"))
    return(sortval, day, name, time)
           
def comp_now(date, ahead, utc):
    now = datetime.now()
    now = now + timedelta(days= ahead, seconds= utc*3600)
    #print "comp- %s, now- %s" %(date, now)
    return bool(date < now)
    
def get_date(seconds, utc):
    start = datetime(2001, 1, 1, 0, 0, 0)
    u = utc * 3600
    ret = start + timedelta(seconds= abs(seconds) + u)
    return ret
    
def format_utc(utc):
    ret = float(utc[0:3])
    if utc[4] == 3:
        if utc[0] == '-':
            ret -= 0.5
        else:
            ret += 0.5
    return ret
        
def getClasses(classname, arr):
    cmatch = -1
    classlist = []
    for i in range(0, len(arr)):
        if isinstance(arr[i], dict):
            if CNAME in arr[i]:
                if arr[i][CNAME] == classname:
                    cmatch = i
            if CLASS in arr[i]:
                itm = items()
                if CLASS in arr[i] and arr[i][CLASS][CF] == cmatch:
                    for k in arr[i]:
                        v = arr[i][k]
                        pname = k
                        pval = None
                        if not isinstance(v, dict):
                            pval = v
                        else:
                            if isinstance(arr[v[CF]], dict):
                                for k1 in arr[v[CF]]:
                                    if not isinstance(arr[v[CF]][k1], dict) and not isinstance(arr[v[CF]][k1], list):
                                        pval = arr[v[CF]][k1]
                            else:
                                pval = arr[v[CF]]
                        if '$' in pname:
                            pname = pname.replace('$', '')
                        itm._create_property(pname, pval)
                    classlist.append(itm)
    return classlist
                    
                            
                                         
class items(object):
    def __init__(self):
        pass
    
    def _create_property(self, name, value):
        setattr(self, name, value)
        

if __name__ == "__main__":
	main(sys.argv[1:])
