#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import subprocess
import socket
from datetime import datetime

def runCommand(args):
    print '=> Run command:', args
    startTime = datetime.now()
    i = subprocess.call(args, shell=True)
    if i != 0:
        print '=> Failed to runCommand:', args
    
    print '=> time:', (datetime.now() - startTime).seconds, 'seconds for:', args
    return i

def get_collections():
    command = "echo 'show collections' | mongo 10.90.13.157/fhh"
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def exclude_collections(collections):
    array = collections.split("\n")
    excludes = []
    for i in array:
        if len(i) == 0 or i.find(" ") != -1 or i.lower() == 'bye':
            continue
        if i in ['article', 'video', 'category', 'wemedia_account']:
            continue
        excludes.append(i)
    return excludes

def generateCommand(excludes):
    if len(excludes) == 0:
        print 'No excludes was found!!!'
        exit(-1)
    command = 'mongodump --host 10.90.13.157 --port 27017 --db fhh --out backup'
    for i in excludes:
        command += ' --excludeCollection ' + i
    return command

if __name__ == '__main__':

    collections = get_collections()
    excludes = exclude_collections(collections)
    command = generateCommand(excludes)
    print command
    runCommand(command)