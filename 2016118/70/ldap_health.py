#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "wanghn"
# Ldap health check

import httplib
import urllib2
import socket
import time
import os
import ConfigParser
import urllib
import commands
import json


def driverstatus(driver_result):
    ds_result = {}
    for i in xrange( len( driver_result ) ):
        state, dxcmd_output = commands.getstatusoutput(
            '/opt/novell/eDirectory/bin/dxcmd -user %s -password %s -host %s -getstate %s' % (
                admin, password, host, driver_result[i]) )
        # state1, dxcmd_cache = commands.getstatusoutput(
        #     '/opt/novell/eDirectory/bin/dxcmd -user %s -password %s -host %s -getcachetransactions %s 0 99999 file.txt' % (
        #         admin, password, host, dxml_driver) )
        # dxcmd_output=os.system('/opt/novell/eDirectory/bin/dxcmd -user %s -password %s -host %s -getstate %s' %(admin,password,host,dxml_driver))
        # filesize = os.path.getsize( r'/home/file.txt' )
        # if filesize == 0 or filesize == 17:
        #     print ('no cache')
        # else:
        #     print ('cache sizes is %d Bytes' % filesize)
        # print ">>>>>>>>>>>>>>>>>>>>>>>>>>"
        # print state
        # print "<<<<<<<<<<<<<<<<<<<<<<<<<<"
        # timenow = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( time.time( ) ) )
        # time_nu = "%s" % timenow
        if state == 0:
            # stopped
            # print "Driver state 0 - Stopped"
            ds_result[driver_result[i]]='Stopped'
        elif state == 512:
            # running
            # print "Driver state 512 - Running"
            ds_result[driver_result[i]]='Running'
        elif state == 256:
            # starting
            # print "Driver state 256 - Starting"
            ds_result[driver_result[i]]='Starting'
            # print tresult
        elif state == 768:
            # stopping
            ds_result[driver_result[i]]='Stopping'
        else:
            print state
    
    # print 'driverstatus result:', ds_result
    return ds_result


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

if __name__ == '__main__':
	
    cf = ConfigParser.RawConfigParser( )
    cf.read( "health_check_config.ini" )
    smmodifytime = os.stat( r"health_check_config.ini" ).st_mtime
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

    admin = cf.get( "HostAgent", "admin" )
    password = cf.get( "HostAgent", "password" )
    dxml_driver = cf.get( "HostAgent", "dxml_driver" )
    host = cf.get( "HostAgent", "host" )
    driverstate = cf.get( "HostAgent", "driverstate" )
    data = cf.get( "HostAgent", "data" )

    driver_result = dxml_driver.split( ',' )
    service_result = servi.split( ',' )
    ip_result = webaddress.split( ',' )
    port_result = webport.split( ',' )
    ctrlags = 1
    num = True
    ser = servicestate( service_result )
    webcip_state = monitorwebapp( ip_result )
    ds_result = driverstatus(driver_result)
    webcp_state = conport( ip_result, port_result )

	
    time_nu = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( time.time( ) ) )
	
    params = {
        'ldap_health':{
            datetime: time_nu,
            driverstate: ds_result,
            servstate: ser,
            webcipstatus: webcip_state,
            webcpstatus: webcp_state
        }
         }
    print "params::::",params
    jsondata = json.dumps(params)
    print "[+]result:",jsondata
    try:
        url1 = 'https://%s:%s%s' % (ipaddr, port, url)
        request = os.popen(
            r"curl -k -H 'Content-type:application/json' -X POST --data '%s' '%s' 2>/dev/null" % (jsondata, url1) )
        print '[+]request:', request.read( )
        # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        # headers = {"Content-type": "application/json"}
        # middletime = time.time( )
        # httpClient = httplib.HTTPSConnection( ipaddr, port, timeout=None )
        # httpClient.request( "POST", url, jsondata, headers )
        # response = httpClient.getresponse( )
        # url1 = 'https://192.168.0.150:8443/edCenter/module/welcome/getDataTestAction'
        # httpClient = urllib2.Request(url1,jsondata,headers)
        # response = urllib2.urlopen(httpClient)
        # print '[+]response:',response.read( )
    except Exception, e:
        print 'err',e
    # finally:
    #     if httpClient:
    #         httpClient.close( )


