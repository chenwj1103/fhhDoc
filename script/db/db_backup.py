#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import time
import json
import subprocess
import socket
from datetime import datetime

mongoHost = '10.90.13.162'
mongoPort = '27017'
mongoDB = 'fhh'
mongoUser = 'fhh_backup_p'
mongoPass = 'fhh_backup_p'
outPath = '/data/backup/mongodb'
syncPath = '/data/backup/sync_fhh'
backupTime = time.strftime('%Y%m%d_%H%M')
outFilePath = outPath + '/' + backupTime
emailReivers = ["renxf@ifeng.com", "shansk@ifeng.com", "qinfj@ifeng.com"]
emailSender = "renxf@localhost.localdomain"
maxCompressedFileNum = 5

def runCommand(args):
    print '=> Run command:', args
    startTime = datetime.now()
    i = subprocess.call(args, shell=True)
    if i != 0:
        print '=> Failed to runCommand:', args
    
    print '=> time:', (datetime.now() - startTime).seconds, 'seconds for:', args
    return i

def backup():
    print 'Start to backup...'
    command = 'mongodump'
    command += ' --host ' + mongoHost
    command += ' --port ' + mongoPort
    command += ' --db ' + mongoDB
    command += ' --out ' + outFilePath
    command += ' --excludeCollection operation_data_log'
    command += ' --excludeCollection operation_log'
    if mongoUser != "" and mongoPass != "":
        command += ' --username ' + mongoUser
        command += ' --password ' + mongoPass
        command += ' --authenticationDatabase admin'
    ret = runCommand(command)
    return ret == 0

def validateUncompressedPath(p):
    pattern = re.compile('\d{8}_\d{4}')
    return pattern.match(p)

def compress():
    uncompressed = [f for f in os.listdir(outPath) if os.path.isdir(os.path.join(outPath, f)) and validateUncompressedPath(f) ]
    for f in uncompressed:
        if f != backupTime:
            filePath = os.path.join(outPath, f)
            command = 'tar zcvf %s.tar.gz %s && rm -r %s' % (filePath, filePath, filePath)
            ret = runCommand(command)
            if ret != 0:
                return False
    return True

def syncFhh():
    fhhTar = 'fhh-%s.tar.gz' % (time.strftime('%Y%m%d'))
    collections = ''
    for c in ['article', 'video', 'category', 'wemedia_account', 'article_statistics', 'video_statistics']:
        collections += ' ./fhh/%s.bson ./fhh/%s.metadata.json' % (c, c)
    command = 'cd %s && tar zcvf %s %s && mv %s %s && find %s -mtime +7 -exec rm -f {} \;' % (outFilePath, fhhTar, collections, fhhTar, syncPath, syncPath)
    print command
    return runCommand(command) == 0

def tarFileComp(x, y):
    xTime = datetime.strptime(x[:13], '%Y%m%d_%H%M')
    yTime = datetime.strptime(y[:13], '%Y%m%d_%H%M')
    if xTime > yTime:
        return -1
    if xTime < yTime:
        return 1
    return 0

def deleteOldCompressedFile():
    thisTarFile = backupTime + '.tar.gz'
    tarFiles = [f for f in os.listdir(outPath) if os.path.isfile(os.path.join(outPath, f)) and f.endswith('.tar.gz') and f != thisTarFile ]
    if len(tarFiles) < maxCompressedFileNum:
        return True

    tarFiles.sort(tarFileComp)
    removeTarFiles = tarFiles[maxCompressedFileNum:]
    for f in removeTarFiles:
        command = 'rm -f ' + os.path.join(outPath, f)
        ret = runCommand(command)
        if ret != 0:
            return False

    return True

def getIp():
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        if not ip.startswith('127'):
            return ip
    return socket.gethostbyname(socket.gethostname())

def getDiskStatus():
    p = subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out

def getBackupFiles():
    p = subprocess.Popen('du -sh ' + outPath + '/*', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print out,err
    return out

def toHtml(s):
    lines = s.split("\n")
    newlines = ['<p>' + line + '</p>' for line in lines]
    return "\n".join(newlines)

def sendMail(isBackupOk=False, msg=None):
    receivers = emailReivers

    ip = getIp()
    description = "成功" if isBackupOk else "失败"
    subject = "%s 数据库备份%s(%s)" % (backupTime, description, ip)
    if msg is not None:
        description += ': ' + msg

    content = """
备份主机ip:%s
备份时间: %s
备份文件: %s
%s

主机磁盘信息:
%s

备份数据列表:
%s
    """ % (ip, backupTime, outFilePath, description, getDiskStatus(), getBackupFiles())
    data = {
        "to": (',').join(receivers),
        "title": subject,
        "content": toHtml(content),
        "contentType":"text"
    }
    command = """curl -H "Content-Type: application/json" -X POST -d '%s' http://10.90.13.148/api/send_mail""" % (json.dumps(data))
    runCommand(command)

def start():
    if not backup():
        sendMail(False, 'mongodump 失败')
        return

    if not syncFhh():
        sendmail(False, 'sync fhh 文件失败')
        return

    if not compress():
        sendMail(False, '压缩失败')
        return

    if not deleteOldCompressedFile():
        sendMail(False, '清理旧的压缩文件失败')
        return

    sendMail(True, "成功啦！！！")

if __name__ == '__main__':
    start()
