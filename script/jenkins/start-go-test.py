#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import re
import os
import sys
import time
import subprocess
import socket
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

def mustRunCommandAndGet(args):
    print '=> Run command:', args
    return subprocess.check_output(args, shell=True)

def runCommandAndGet(args):
    print '=> Run command:', args
    out = ""
    try:
        out = subprocess.check_output(args, shell=True)
    except subprocess.CalledProcessError as e:
        print '=> Run command Error:', e
    return out

def detectRunningExec(appname, execname):
    result = []

    command = "ps -ef | grep %s | grep %s |grep -Ev 'grep|start-go-test.py|python' " % (execname, appname)
    print runCommandAndGet(command)
    command += "| awk '{print $2}'"
    pids = runCommandAndGet(command)
    if pids.strip() == "":
        return result

    for pid in pids.strip().split('\n'):
        entry = {"pid": pid}
        port = runCommandAndGet("""netstat -tunlp | grep %s | awk '{gsub(".*:","",$4);print $4}'""" % (pid)).strip()
        if port == "":
            print 'Can not get the port!!!!!!!!!!!!!!!!!!!!!!!!'
            os.exit(1)
        entry["port"] = port
        result.append(entry)
    return result


def startNewInstance(args):
    envstr = "env " + args.env if args.env != "" else ""
    optstr = args.opt

    command = "nohup %s `pwd`/%s %s > nohup.out 2>&1 & echo $!" % (envstr, args.execname, optstr)
    pid = mustRunCommandAndGet(command).strip()
    print 'New pid is',pid
    time.sleep(7)
    # check new pid
    print '-'*55
    print 'Check new instance status:'
    status = runCommandAndGet("ps -ef | grep %s | grep %s | grep -v grep | wc -l" % (args.execname, pid)).strip()
    if int(status) == 0:
        print '==> Failed to start new instance, found no pid', pid, '!!!!!!!'
        print '='*20 + "nohup.out" + "=" *20
        print runCommand("cat nohup.out")
        exit(1)

    print '-' * 50
    print runCommand("cat nohup.out")


def terminateOld(runnings):
    for running in runnings:
        pid = running["pid"]
        print 'Kill old instance', pid
        runCommand("kill " + pid)

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("appname", help="app name")
    parser.add_argument("execname", help="exec program name")

    parser.add_argument("--env", help='enviroment variables passed to exec, i.e. -env="MODE=prod LOG=1"', default="", action="store")
    parser.add_argument("--opt", help='exec args options: --opt="-cpu=4 --verbose"', default="", action="store")

    args = parser.parse_args()

    def printHelpAndExit(msg):
        parser.print_help()
        print msg
        exit(1)

    print '-'*50
    print 'appname:    ', args.appname
    print 'exec:       ', args.execname
    print 'env:        ', args.env
    print 'opt:        ', args.opt
    print '-'*50
    return args


# 脚本执行过程
# 脚本会在当前目录寻找执行程序并进行执行,端口号范围是在9000~9999,自动选择
# 支持自定义的环境变量和运行参数
if __name__ == '__main__':
    args = parseArgs()
    runningPids = detectRunningExec(args.appname, args.execname)
    print 'Runing program is', runningPids

    # force kill
    for running in runningPids:
        pid = running["pid"]
        print 'Kill old instance', pid
        runCommand("kill " + pid)

    # start new
    startNewInstance(args)