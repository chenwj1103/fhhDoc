#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import json
import subprocess
import socket
from datetime import datetime
import smtplib

mongodbHost = "10.90.9.28"
mongodbPort = "27017"
mongodbDBName = "fhh_test"
mongodbUser = "fhh_test_rw"
mongodbPass = "fhh_test_rw"
esIndexName = "zmt_test"
emailReivers = ["renxf@ifeng.com", "shansk@ifeng.com", "qinfj@ifeng.com"]
esPath = ""

def runCommand(args):
    print '=> Run command:', args
    startTime = datetime.now()
    i = subprocess.call(args, shell=True)
    if i != 0:
        print '=> Failed to runCommand:', args
    
    print '=> time:', (datetime.now() - startTime).seconds, 'seconds for:', args
    return i

def getIp():
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith('127'):
            return ip
    return socket.gethostbyname(socket.gethostname())


def sendMail(isOk=False, msg=None):
    receivers = emailReivers

    ip = getIp()
    if isOk:
        subject = "恢复数据库成功(%s)" % (ip)
        description = "成功"
    else:
        subject = "恢复数据库失败(%s)" % (ip)
        description = "失败"
    if msg is not None:
        description += ': ' + msg

    content = """
恢复数据库主机ip: %s
恢复数据库时间: %s

%s
    """ % (ip, time.strftime('%Y%m%d_%H%M'), description)

    data = {
        "to": (',').join(receivers),
        "title": subject,
        "content": toHtml(content),
        "contentType":"text"
    }
    command = """curl -H "Content-Type: application/json" -X POST -d '%s' http://10.90.13.148/api/send_mail""" % (json.dumps(data))
    runCommand(command)

def toHtml(s):
    lines = s.split("\n")
    newlines = ['<p>' + line + '</p>' for line in lines]
    return "\n".join(newlines)

def validateUncompressedPath(p):
    pattern = re.compile('\d{8}_\d{4}')
    return pattern.match(p)

def dumpFileComp(x, y):
    xTime = datetime.strptime(x[:13], '%Y%m%d_%H%M')
    yTime = datetime.strptime(y[:13], '%Y%m%d_%H%M')
    if xTime > yTime:
        return -1
    if xTime < yTime:
        return 1
    return 0

def findDumpFile():
    outPath = '/data/backup/mongodb'
    uncompressed = [f for f in os.listdir(outPath) if os.path.isdir(os.path.join(outPath, f)) and validateUncompressedPath(f) ]
    print uncompressed
    uncompressed.sort(dumpFileComp)
    if len(uncompressed) > 0:
        return uncompressed[0]
    return None

def shardDB():
    command = 'mongo %s:%s/admin  -u fhh_shard_admin -p fhh_shard_admin < ' % (mongodbHost, mongodbPort)
    command += os.path.join(os.path.dirname(__file__), 'shard.js')
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def syncES():
    command = "java -server -Xms1G -Xmx2G -XX:+UseG1GC "
    command += """ -Dmongodb.driver='mongodb://%s:%s@%s:%s/?authSource=%s' """ % (mongodbUser, mongodbPass, mongodbHost, mongodbPort, mongodbDBName)
    command += """ -Dmongodb.db=%s -Des.index=%s -jar %s/es.jar """ % (mongodbDBName, esIndexName, esPath)
    command += """ %s | grep -v 'console_log - index %s' """
    allOk = True
    for action in ["recreate", "article", "video", "account"]:
        print "\n\n\n"
        ret = runCommand(command % (action, action))
        if ret != 0:
            allOk = False
    runCommand("rm -f /root/logs/sync*.log")
    return allOk

def start(dbName):
    # 
    dumpFile = findDumpFile()
    if dumpFile is None:
        sendMail(False, '没有找到可以用于数据库恢复的dump文件')
        return

    command = 'mongorestore --host %s --port %s --username fhh_test_restore --password fhh_test_restore --authenticationDatabase admin --drop --db %s /data/backup/mongodb/%s/fhh' % (mongodbHost, mongodbPort, dbName, dumpFile)
    print command
    ret = runCommand(command)
    if ret != 0:
        sendMail(False, '恢复数据库失败\n' + command)
        return

    if not syncES():
        sendMail(False, '恢复数据库失败:%s\n%s\n' % ('ES同步失败', command))
        return
    sendMail(True, '恢复数据库成功\n%s\n' % (command) )

def usage():
    print '%s fhh_test|fhh_test1 /path/of/es.jar' % (os.path.basename(__file__))
    exit()

if __name__ == '__main__':
    if len(sys.argv) <= 2 or sys.argv[1] not in ['fhh_test', 'fhh_test1']:
        usage()

    # 默认必须有个 es.jar
    dbName = sys.argv[1]
    esPath = sys.argv[2]

    if not os.path.isfile(os.path.join(esPath, "es.jar")):
        print 'Found no es.jar in', esPath
        usage()

    start(dbName)