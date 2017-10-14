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

def detectRunningExec(execname):
    result = []

    command = "ps -ef | grep %s |grep -Ev 'grep|start-go.py|python' " % (execname)
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

def chooseNewPort(ports):
    for i in range(9000, 9999):
        if str(i) in ports:
            continue
        return i
    return None

def startNewInstance(args, port):
    envstr = "env " + args.env if args.env != "" else ""
    optstr = args.opt
    if args.porttype == "env":
        if envstr == "":
            envstr = "env %s=%d" % (args.portvalue, port)
        else:
            envstr += " %s=%d" % (args.portvalue, port)
    else:
        optstr += " %s%d" % (args.portvalue, port)

    command = "nohup %s ./%s %s > nohup.out 2>&1 & echo $!" % (envstr, args.execname, args.opt)
    pid = mustRunCommandAndGet(command).strip()
    print 'New pid is',pid
    for i in range(6):
        time.sleep(5)
        # check new pid
        print '-'*55
        print 'Check new instance status:',i, ' times'
        status = runCommandAndGet("ps -ef | grep %s | grep %s | grep -v grep | wc -l" % (args.execname, pid)).strip()
        if int(status) == 0:
            print '==> Failed to start new instance, found no pid', pid, '!!!!!!!'
            exit(1)
        appok = runCommandAndGet("grep 'APP STARTED AND READY' nohup.out | wc -l").strip()
        if int(appok) > 0:
            print 'App started OK'
            break
        # TODO check if program is ok by api???
    print '-' * 50
    print runCommand("cat nohup.out")


def updateNginxConfig(configpath, serverport, upstreamport, execname):
    fp = open(os.path.join(configpath, "default.conf"), "w")
    upstream = "%s-%d" % (execname, upstreamport)
    data="""
upstream %s {
    server 127.0.0.1:%s;
    keepalive 15;
}
server {
    listen       %s;
    location / {
      proxy_pass http://%s;
      proxy_set_header Connection "Keep-Alive";
      proxy_set_header Proxy-Connection "Keep-Alive";
    }
}
""" % (upstream, port, serverport, upstream)

    fp.write(data)
    fp.close()

    # reload nginx
    mustRunCommandAndGet("service nginx reload")
    print 'sleep 2 seconds to wait reload ok'
    time.sleep(2)

def terminateOld(runnings):
    for running in runnings:
        pid = running["pid"]
        print 'Kill old instance', pid
        runCommand("kill " + pid)

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("execname", help="exec program name")
    parser.add_argument("portswitch", help='must in the form of env=PORT or opt=--port', action="store")

    parser.add_argument("--env", help='enviroment variables passed to exec, i.e. -env="MODE=prod LOG=1"', default="", action="store")
    parser.add_argument("--opt", help='exec args options: --opt="-cpu=4 --verbose"', default="", action="store")
    parser.add_argument("--nginxconf", help='nginx config path', default="/usr/local/nginx/conf/conf.d", action="store")
    parser.add_argument("--nginxport", help='nginx listening port', default="80", action="store")
    args = parser.parse_args()

    def printHelpAndExit(msg):
        parser.print_help()
        print msg
        exit(1)
    # parse port switch and type
    msg = '\nError: bad format portswitch, should be env=XXX or opt=xxx'
    portswitch = args.portswitch
    if len(portswitch) == 0 or (not portswitch.startswith("env=") and not portswitch.startswith('opt=')):
        printHelpAndExit(msg)
    porttype = portswitch.split("=")[0]
    portvalue = portswitch.split("=")[1]
    if portvalue == "":
        printHelpAndExit(msg)

    args.porttype = porttype
    args.portvalue = portvalue

    # check nginx path
    if not os.path.exists(args.nginxconf):
        printHelpAndExit("nginx config path:%s doest exsit" % (args.nginxconf))

    print '-'*50
    print 'exec:       ', args.execname
    print 'porttype:   ', args.porttype
    print 'portvalue:  ', args.portvalue
    print 'env:        ', args.env
    print 'opt:        ', args.opt
    print 'nginxconf:  ', args.nginxconf
    print 'nginxport:  ', args.nginxport
    print '-'*50
    return args


# 脚本执行过程
# 脚本会在当前目录寻找执行程序并进行执行,端口号范围是在9000~9999,自动选择
# 支持自定义的环境变量和运行参数
if __name__ == '__main__':
    args = parseArgs()
    runningPids = detectRunningExec(args.execname)
    print 'Runing program is', runningPids

    port = 9000
    if len(runningPids) != 0:
        port = chooseNewPort([d["port"] for d in runningPids])
    if port is None:
        print 'Failed to choose a new port!!!!!!!!!!!'
        exit(1)
    print 'Choosing a new port', port
    startNewInstance(args, port)

    updateNginxConfig(args.nginxconf, args.nginxport, port, args.execname)
    # TODO check if reload ok by api ??? for example. /check-stat return new pid

    terminateOld(runningPids)