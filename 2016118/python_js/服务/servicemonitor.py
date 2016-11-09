#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "wanghn"
import httplib
import json
import multiprocessing
import time
import os
import ConfigParser
import urllib


# def settings ():
#     cf = ConfigParser.RawConfigParser ()
#     cf.read ("smconfig.ini")
#     url = cf.get ("HostAgent", "services")
#     servstate = cf.get("HostAgent", "disknu")
#     result = url.split (',')
#     return result
global httpClient
global smmodifytime, ipaddr, port, url, servstate, servlen, alist, lock
global num, ctrlags

def serv(arg, ctr):
    global httpClient
    global smmodifytime, ipaddr, port, url, servstate, servlen, alist, lock
    global num, ctrlags
    try:
        while ctr == False:
            try:
                ser = {}
                smmodifytime2 = os.stat(r"/root/python/smoniconf.ini").st_mtime
                # print smmodifytime,smmodifytime2
                if smmodifytime2 == smmodifytime:
                    ret = os.popen('ps -ef|grep %s|grep -v grep' % arg).readlines()
                    if len(ret) > 0:
                        # ser = "%s1" % arg
                        ser[arg] = True
                        # params = urllib.urlencode(
                        #     {servstate: ser
                        #      }
                        # )
                        params = {
                            servstate: ser
                        }
                        jsondata = json.dumps(params)
                        print jsondata
                    # print "%s 进程状态正常！" % arg, time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (time.time ()))
                    # print '======================================'
                    else:
                        # return '%s:0' % arg
                        # ser = "%s0" % arg
                        ser[arg] = False
                        # ser = '%s\\:0' % arg
                        # params = urllib.urlencode(
                        #     {servstate: ser
                        #      }
                        # )
                        params = {
                            servstate: ser
                        }
                        jsondata = json.dumps( params )
                        print jsondata
                    # print "%s 进程状态异常！" % arg, time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (time.time ()))
                    # print '======================================'
                    time.sleep(3)
                    # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                    # middletime = time.time()
                    # httpClient = httplib.HTTPConnection ("192.168.0.138", 8080, timeout=30)
                    # httpClient.request ("POST", "/edCenter/module/welcome/getDataTestAction", params, headers)
                    # httpClient = httplib.HTTPSConnection(ipaddr, port, timeout=None)
                    # httpClient.request("POST", url, params, headers)
                    # response = httpClient.getresponse()
                    # print "-----------------------------------------------"
                    # print params
                    # print response.read()
                    url1 = 'https://%s:%s%s' % (ipaddr, port, url)
                    request = os.popen(
                        r"curl -k -H 'Content-type:application/json' -X POST --data '%s' '%s' 2>/dev/null" % (
                            jsondata, url1) )
                    print '[+]request:', request.read( )
                    print "--------------------------------------------------------------------------------------------"
                    stoptime = time.time()
                else:
                    # num = True
                    # ctr = True
                    # ctrlags = 0
                    mm = "kill -s 9 `ps -aux | grep servicemonitor.py | grep -v grep | awk '{print $2}'`"
                    # # mm = "ps -ef | grep servicemonitor.py | grep -v grep | awk '{print $2}'"
                    os.popen(mm).read()
                    # for i in xrange (servlen):
                    #     alist[i].close()
                    # if httpClient:
                    #     httpClient.close()
                    # main()
                    # break
            except Exception, e:
                print "5秒后重试......"
                print "--------------"
                time.sleep(5)
                continue
    except KeyboardInterrupt:
        exit(1)
    except Exception, e:
        exit(1)
    # finally:
    #     if httpClient:
    #         httpClient.close()


def main():
    global httpClient
    global smmodifytime, ipaddr, port, url, servstate, servlen, alist, lock
    global num, ctrlags
    try:
        starttime = time.time()
        # result = []
        # num = True
        # if __name__ == '__main__':
        cf = ConfigParser.RawConfigParser()
        cf.read("/root/python/smoniconf.ini")
        smmodifytime = os.stat(r"/root/python/smoniconf.ini").st_mtime
        ipaddr = cf.get("HostAgent", "ipaddr")
        port = cf.get("HostAgent", "port")
        servi = cf.get("HostAgent", "services")
        url = cf.get("HostAgent", "url")
        servstate = cf.get("HostAgent", "servstate")
        result = servi.split(',')
        # service = settings ()
        alist = ['novell' + x for x in result]
        servlen = len(result)
        # command = 'ps -ef|grep %s' % alist[i]
        # if num:
        #     command = 'ps -ef|grep servicemonitor.py | grep -v grep'
        #     with os.popen (command) as f:
        #         f = f.read ()
        #         print f.split ()[1]
        while num:
            for i in xrange(servlen):
                num = False
                alist[i] = multiprocessing.Process(target=serv, args=(result[i], num))
                alist[i].start()
            if ctrlags == 0:
                mm = "kill -s 9 `ps -ef | grep servicemonitor.py | grep -v grep | awk '{print $2}'`"
                # mm = "ps -ef | grep servicemonitor.py | grep -v grep | awk '{print $2}'"
                os.popen(mm).readline()
                main()

    except Exception, e:
        print e
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    ctrlags = 1
    num = True
    main()

