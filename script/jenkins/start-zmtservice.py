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

def detectRunningExec(jarname):
    result = []

    command = "ps -ef | grep -E '%s' |grep -Ev 'grep|start-zmtservice.py|python' " % (jarname)
    print runCommandAndGet(command)
    command += "| awk '{print $2}'"
    pids = runCommandAndGet(command)
    if pids.strip() == "":
        return result

    for pid in pids.strip().split('\n'):
        entry = {"pid": pid}
        ports = runCommandAndGet("""netstat -tunlp | grep %s | awk '{gsub(".*:","",$4);print $4}'""" % (pid)).strip().split("\n")
        if len(ports) == 0:
            print 'Can not get the port!!!!!!!!!!!!!!!!!!!!!!!!'
            os.exit(1)
        entry["ports"] = ports
        result.append(entry)
    return result


def startNewInstance(args, app, port):
    envstr = "env " + args.env if args.env != "" else ""
    adminport = port + 10
    logpath = "/data/logs/" + app
    runCommand("mkdir -p " + logpath)
    stdlog = logpath + "/nohup.out"
    opt = "--server.port=%d" % (port)
    jvmopt = "-server -Xms4G -Xmx8G -XX:+UseG1GC -Dcom.sun.management.jmxremote \
            -Dcom.sun.management.jmxremote.port=%d -Dcom.sun.management.jmxremote.ssl=false \
            -Dcom.sun.management.jmxremote.authenticate=false -Dvertx.options.jmxEnabled=true \
            -Dlog.log4j2.home=%s" % (adminport, logpath)
    command = "nohup %s java %s -jar %s.jar %s > %s 2>&1 & echo $!" % (envstr, jvmopt, app, opt, stdlog)
    pid = mustRunCommandAndGet(command).strip()
    print 'New pid is',pid
    time.sleep(7)
    # check new pid
    print '-'*55
    print 'Check new instance status:'
    status = runCommandAndGet("ps -ef | grep %s | grep %s | grep -v grep | wc -l" % (app, pid)).strip()
    if int(status) == 0:
        print '==> Failed to start new instance, found no pid', pid, '!!!!!!!'
        print '='*20 + "nohup.out" + "=" *20
        print runCommand("tail -n 20 " + stdlog)
        exit(1)

    print '-' * 50
    print runCommand("tail -n 20 " + stdlog)


def terminateOld(runnings):
    for running in runnings:
        pid = running["pid"]
        print 'Kill old instance', pid
        runCommand("kill " + pid)

def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("--env", help='enviroment variables passed to exec, i.e. -env="MODE=prod LOG=1"', default="", action="store")
    parser.add_argument("--nginxconf", help='nginx config path', default="/usr/local/nginx/conf/conf.d", action="store")
    args = parser.parse_args()

    def printHelpAndExit(msg):
        parser.print_help()
        print msg
        exit(1)

    print '-'*50
    print 'env:        ', args.env
    print 'nginxconf:  ', args.nginxconf
    print '-'*50
    return args

def updateNginxConfig(configpath, localPort, foreignPort, apiPort):
    fp = open(os.path.join(configpath, "default.conf"), "w")
    data="""
upstream zmt-service-foreign {
    server 127.0.0.1:%s;
    keepalive 15;
}

upstream zmt-service-local {
    server 127.0.0.1:%s;
    keepalive 15;
}

upstream zmt-service-api {
    server 127.0.0.1:%s;
    keepalive 15;
}

server {
    listen       80;
    server_name fhhapi.ifeng.com;
    location / {
        proxy_pass http://zmt-service-foreign;
        proxy_set_header Connection "Keep-Alive";
        proxy_set_header Proxy-Connection "Keep-Alive";
    }
}

server {
    listen       80;
    server_name local.fhhapi.ifeng.com;
    location / {
        proxy_pass http://zmt-service-local;
        proxy_set_header Connection "Keep-Alive";
        proxy_set_header Proxy-Connection "Keep-Alive";
    }
}

server {
    listen       80;
    server_name local.fhhapi-service.ifengidc.com;
    location / {
        proxy_pass http://zmt-service-api;
        proxy_set_header Connection "Keep-Alive";
        proxy_set_header Proxy-Connection "Keep-Alive";
    }
}

""" % (foreignPort, localPort, apiPort)

    fp.write(data)
    fp.close()

    # reload nginx
    mustRunCommandAndGet("service nginx reload")
    print 'sleep 2 seconds to wait reload ok'
    time.sleep(2)

def chooseNewPort(startport, ports):
    print 'choose a new port from:' + str(ports)
    for i in range(startport, startport + 699):
        if str(i) in ports or str(i+10) in ports:
            continue
        return i
    return None

if __name__ == '__main__':
    args = parseArgs()


    allRunning = []
    newPorts = {
        "zmt-service-local": 8002,
        "zmt-service-foreign": 8702,
        "zmt-service-api": 9402
    }
    for app in newPorts.keys():
        newport = newPorts[app]
        print '--[%s] Start to handle %s' % (app, app)
        # runningPids
        runningPids = detectRunningExec(app + '.jar')
        print '--[%s] Runing program is %s'% (app, runningPids)

        if len(runningPids) != 0:
            ports = []
            for running in runningPids:
                ports += running["ports"]
            newport = chooseNewPort(newport, ports)
        if newport is None:
            print 'Failed to choose a new port!!!!!!!!!!!'
            exit(1)
        print '--[%s] Choosing a new port %d' % (app, newport)

        # start new
        startNewInstance(args, app, newport)
        newPorts[app] = newport
        allRunning += runningPids
        print '-'*50 + '\n'

    # nginx
    localPort = newPorts["zmt-service-local"]
    foreignPort = newPorts["zmt-service-foreign"]
    apiPort = newPorts["zmt-service-api"]
    updateNginxConfig(args.nginxconf, localPort, foreignPort, apiPort)

    # kill
    terminateOld(allRunning)