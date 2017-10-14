#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import io
import argparse
import json


if __name__ == '__main__' : 
    parser = argparse.ArgumentParser()

    parser.add_argument('--json', help='the configuration of connectors, json file path', default='connectors-config.json', action='store')

    args = parser.parse_args()

    print 'configuration file path :        ', args.json

    cf = open(os.path.join(args.json), "r")

    connector_json = cf.read()

    cf.close()

    if connector_json == '' : 
        print "connectors config json is empty"
        exit(1)

    connector_list = json.loads(connector_json)
    ocf = open(os.path.join('connectors-config.conf'), "w")
    octext = ''
    for conn in connector_list :
        name = conn['name']
        config = conn['config']
        
        line = '%s %s \n'%(name, json.dumps(config))
        octext += line
    
    ocf.write(octext)
    ocf.close()
    print 'connectors shell conf file build completed！'