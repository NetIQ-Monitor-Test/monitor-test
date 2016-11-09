#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "wanghn"

import httplib
import socket
import time
import os
import ConfigParser
import json
import urllib2

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
        responsecheck = urllib2.urlopen( "http://ids122.avict.com:8080/nidp/app/heartbeat" ).read( )
        if 'Success' in responsecheck:
            urlhealthcheckresult['heartbeat'] = True
            return urlhealthcheckresult
        # print '[+]responsecheck:',responsecheck
    except Exception, e:
        urlhealthcheckresult['heartbeat'] = False
        return urlhealthcheckresult

def nldapcheck():
    nldapcheckresult = {}
    try:
        check_cmd = os.popen( 'nldap_check' ).read( ).strip( ).replace( '\n', '' ).split( '.' )
        matchtcp=re.match(".*is listening(.*)TCP.*",check_cmd[0])
        matchtls=re.match(".*is listening(.*)TLS.*",check_cmd[1])
        # print '[+]matchtcp:',matchtcp.group()
        # print '[+]matchtls:',matchtls.group()
        if matchtcp and matchtls:
            nldapcheckresult['TCP'] = True
            nldapcheckresult['TLS'] = True
        elif not matchtcp and matchtls:
            nldapcheckresult['TCP'] = False
            nldapcheckresult['TLS'] = True
        elif matchtcp and not matchtls:
            nldapcheckresult['TCP'] = True
            nldapcheckresult['TLS'] = False
        else:
            nldapcheckresult['TCP'] = False
            nldapcheckresult['TLS'] = False
        return nldapcheckresult
    except Exception,e:
        nldapcheckresult['TCP'] = False
        nldapcheckresult['TLS'] = False
        return nldapcheckresult

if __name__ == '__main__':
    cf = ConfigParser.RawConfigParser( )
    cf.read( "/root/python/ids_health_config.ini" )
    smmodifytime = os.stat( r"/root/python/ids_health_config.ini" ).st_mtime
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
    nldapstatus = cf.get( "HostAgent", "nldapstatus" )
    urlcheckstatus = cf.get( "HostAgent", "urlcheckstatus" )
    service_result = servi.split( ',' )
    ip_result = webaddress.split( ',' )
    port_result = webport.split( ',' )
    ctrlags = 1
    num = True
    ser = servicestate( service_result )
    webcip_state = monitorwebapp( ip_result )
    webcp_state = conport( ip_result, port_result )
    nldap_check_state = nldapcheck()
    url_health_check_state = urlhealthcheck()

    time_nu = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( time.time( ) ) )

    params = {
        'ids_health':{
            servstate: ser,
            webcipstatus: webcip_state,
            webcpstatus: webcp_state,
            nldapstatus: nldap_check_state,
            urlcheckstatus: url_health_check_state
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
        # print 'response:',response.read( )
        url1 = 'https://%s:%s%s' % (ipaddr, port, url)
        request = os.popen(
            r"curl -k -H 'Content-type:application/json' -X POST --data '%s' '%s' 2>/dev/null" % (data, url1) )
        print '[+]request:', request.read( )
    except Exception, e:
        print 'err',e
    # finally:
    #     if httpClient:
    #         httpClient.close( )