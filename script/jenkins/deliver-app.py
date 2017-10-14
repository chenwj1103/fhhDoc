#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import re
import os
import sys
import time
import subprocess
import shutil
from datetime import datetime


def runCommand(args):
    print '=> Run command:', args
    i = subprocess.call(args, shell=True)
    if i != 0:
        print '=> Failed to runCommand:', args
    return i

def mustRunCommand(args):
    print '=> Run command:', args
    i = subprocess.call(args, shell=True)
    if i != 0:
        raise Exception('Failed to runcommand', args)

def runCommandAndGet(args):
    print '=> Run command:', args
    return subprocess.check_output(args, shell=True)

def cleanFolders(rootpath, keepNum = 20):
    def compare(x, y):
        if int(x) > int(y):
            return -1
        if int(x) < int(y):
            return 1
        return 0

    print 'keepNum is', keepNum
    i = 0
    all = [f for f in os.listdir(rootpath) if f != 'running']
    all.sort(compare)
    for dayfolder in all:
        print 'Search folder', dayfolder
        if i == keepNum:
            print 'Delete folder', dayfolder
            shutil.rmtree(os.path.join(rootpath, dayfolder))
            continue
        subfolders = [n for n in os.listdir(os.path.join(rootpath, dayfolder))]
        subfolders.sort(compare)
        for folder in subfolders:
            if i < keepNum:
                i += 1
                print 'Keep folder: %s/%s' % (dayfolder, folder)
                continue
            print 'Delete folder:%s/%s' % (dayfolder, folder)
            shutil.rmtree(os.path.join(rootpath, dayfolder, folder))
            


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("tarball", help="your tarball")
    parser.add_argument("appname", help="your appname")
    parser.add_argument("--max", help="max num to keep, default 10", default=10, action="store", type=int)

    args = parser.parse_args()

    print '-'*50
    print 'tarball:       ', args.tarball
    print 'appname:       ', args.appname
    print 'maxkeep:       ', args.max
    print '-'*50

    return args

# 脚本执行过程
# 脚本在当前目录下会创建　app/$appname/libs/201706/1030 的目录,并讲制定tarball解压到此目录.
# 同时，会将软连接指向新的目录 app/$appname/libs/running -> app/$appname/libs/201706/1030
# 而且脚本会自动清理旧的目录.规则为保留最新的20个
if __name__ == '__main__':
    args = parseArgs()

    rootpath = os.path.abspath(os.path.join("./app", args.appname, "libs"))
    packagepath = os.path.join(rootpath, time.strftime('%Y%m%d'), time.strftime('%H%M%S'))
    runningpath = os.path.join(rootpath, "running")
    os.makedirs(packagepath)
    # extract
    mustRunCommand("tar xf %s -C %s" % (args.tarball, packagepath))
    # linking
    if os.path.islink(runningpath):
        print 'Delete old link'
        os.remove(runningpath)

    mustRunCommand("ln -s %s %s" % (packagepath, runningpath))

    # clean expired folders
    cleanFolders(rootpath, args.max)

    # remove tar
    os.remove(args.tarball)