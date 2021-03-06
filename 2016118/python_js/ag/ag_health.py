#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "wanghn"
# ag_health_check

import httplib
import socket
import time
import os
import ConfigParser
import json
import urllib2
import commands
import re


def monitorwebapp(ip_result):
    webcip_state = {}
    timenow = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( time.time( ) ) )
    for m in xrange( len( ip_result ) ):
        ping_cmd = os.popen( 'ping %s -c 1 | grep -c time=' % ip_result[m] ).read( )
        if ping_cmd != '0\n':
            webcip_state[ip_result[m]] = True
        else:
            webcip_state[ip_result[m]] = False
    # print 'monitorwebapp result:',webcip_state
    return webcip_state

def conport(ip_result,port_result):
    webcp_state = {}
    for n in xrange( len( port_result ) ):
        ip_port = (ip_result[n], int( port_result[n] ))
        sk = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        sk.settimeout( 1 )
        # print ip_port
        try:
            sk.connect(ip_port)
            if ip_result[n] in webcp_state:
                webcp_state[ip_result[n]].update({port_result[n]:True})
            else:
                webcp_state[ip_result[n]]=({port_result[n]:True})
        except Exception:
            if ip_result[n] in webcp_state:
                webcp_state[ip_result[n]].update({port_result[n]:False})
            else:
                webcp_state[ip_result[n]]=({port_result[n]:False})
        sk.close( )

    # print 'conport result:', webcp_state
    return webcp_state

def servicestate(service_result):
    ser = {}
    for i in xrange( len( service_result ) ):
        ret = os.popen( 'ps -ef|grep %s|grep -v grep' % service_result[i] ).readlines( )
        if len( ret ) > 0:
            ser[service_result[i]]=True
        else:
            ser[service_result[i]]=False

    # print 'servicestate resut:',ser
    return ser

def urlhealthcheck():
    urlhealthcheckresult = {}
    try:
        responsecheck = urllib2.urlopen( "http://ag125.avict.com:80/nesp/app/heartbeat" ).read( )
        if 'Success' in responsecheck:
            urlhealthcheckresult['heartbeat'] = True
            return urlhealthcheckresult
        # print '[+]responsecheck:',responsecheck
    except Exception, e:
        urlhealthcheckresult['heartbeat'] = False
        return urlhealthcheckresult
def idsmetadata():
    idsmetadataresult = {}
    try:
        idscommand = urllib2.urlopen( "https://ids122.avict.com:8443/nidp/idff/metadata" ).read( )
        # idscommand = os.popen( 'curl -k https://ids122.avict.com:8443/nidp/idff/metadata').read( )
        if 'X509Certificate' in idscommand:
            idsmetadataresult['metadata'] = True
            return idsmetadataresult
        # print '[+]responsecheck:',responsecheck
    except Exception, e:
        idsmetadataresult['metadata'] = False
        return idsmetadataresult


if __name__ == '__main__':
    cf = ConfigParser.RawConfigParser( )
    cf.read( "/root/python/ag_health_config.ini" )
    smmodifytime = os.stat( r"/root/python/ag_health_config.ini" ).st_mtime
    ipaddr = cf.get( "HostAgent", "ipaddr" )
    port = cf.get( "HostAgent", "port" )
    servi = cf.get( "HostAgent", "services" )
    url = cf.get( "HostAgent", "url" )
    datetime = cf.get( "HostAgent", "datetime" )
    servstate = cf.get( "HostAgent", "servstate" )
    webaddress = cf.get( "HostAgent", "webaddress" )
    webport = cf.get( "HostAgent", "webport" )
    webcipstatus = cf.get( "HostAgent", "webcipstatus" )
    webcpstatus = cf.get( "HostAgent", "webcpstatus" )
    urlcheckstatus = cf.get( "HostAgent", "urlcheckstatus" )
    idsmetaatastatus = cf.get( "HostAgent", "idsmetaatastatus" )
    service_result = servi.split( ',' )
    ip_result = webaddress.split( ',' )
    port_result = webport.split( ',' )
    ctrlags = 1
    num = True
    ser = servicestate( service_result )
    webcip_state = monitorwebapp( ip_result )
    webcp_state = conport( ip_result, port_result )
    url_health_check_state = urlhealthcheck()
    ids_metada_state = idsmetadata()

    time_nu = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( time.time( ) ) )

    params = {
        'ag_health':{
            servstate: ser,
            webcipstatus: webcip_state,
            webcpstatus: webcp_state,
            urlcheckstatus: url_health_check_state,
            idsmetaatastatus: ids_metada_state
        }
         }
    # print "params::::",params
    data = json.dumps(params)
    print "result:",data
    try:
        # headers = {"Content-type": "application/json"}
        # middletime = time.time( )
        # httpClient = httplib.HTTPSConnection( ipaddr, port, timeout=None )
        # httpClient.request( "POST", url, data, headers )
        # response = httpClient.getresponse( )
        url1 = 'https://%s:%s%s' %(ipaddr,port,url)
        # url1 = 'https://www.baidu.com'
        # request = os.popen( "curl -k -H 'Content-type:application/json' -X POST -d",data,url1)
        request = os.popen( r"curl -k -H 'Content-type:application/json' -X POST --data '%s' '%s' 2>/dev/null" %(data,url1))
        print '[+]request:',request.read()
        # print 'response:',response.read()
    except Exception, e:
        print 'err',e
    # finally:
    #     if httpClient:
    #         httpClient.close( )
