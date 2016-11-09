#!/usr/bin/env python
#coding=utf8
 
import httplib, urllib
import time
import os
import sys
import ConfigParser
from collections import namedtuple
import json

'''
pythonHostConfig.ini
[HostAgent]
ipaddr = 192.168.0.138
port = 8080
url = /edCenter/module/welcome/getDataTestAction
datetime = timenu
cupname = cpunu
memname = memnu
diskname = disknu
'''

disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
usage_ntuple = namedtuple('usage', 'total used free percent')
# 统计某磁盘使用情况，返回对象
def disk_usage(path):
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
        return usage_ntuple(total/1024, used/1024, free/1024, '%.1f%%' %percent)
    except ZeroDivisionError:
        percent = 0
def disk_if(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
        # return '%.1f%%' % percent
        return percent
    except ZeroDivisionError:
        percent = 0

def getpinginfo(ipaddress):
    try:
        command = 'ping %s -c 4' %ipaddress  # 可以直接在命令行中执行的命令
        # command = 'ping 192.168.0.22 -c 4'
        with os.popen(command) as f:
            ping = f.readline().split()
            ping1 = '1: '+f.readline()
            ping2 = '2: '+f.readline()
            ping3 = '3: '+f.readline()
            ping4 = '4: '+f.readline()
            ping5 = '5: '+f.readline()
            ping6 = '6: '+f.readline()
            ping7 = '7: '+f.readline()
            ping8 = float(f.readline().split()[3].split('/')[1])
            ping9 = '9: '+f.readline()
            # sump = ping1+ping2+ping3+ping4
            # avg = float(sump)/4
            # print round(avg,3)
            return ping8
    except Exception,e:
        return False
def readCpuInfo():
    f = open('/proc/stat') 
    lines = f.readlines(); 
    f.close()
    for line in lines: 
        line = line.lstrip() 
        counters = line.split() 
        if len(counters) < 5: 
            continue
        if counters[0].startswith('cpu'):
            break
    total = 0
    for i in xrange(1, len(counters)): 
        total = total + float(counters[i])
    idle = float(counters[4])
    return {'total':total, 'idle':idle}


def calcCpuUsage(counters1, counters2):
    idle = counters2['idle'] - counters1['idle']
    total = counters2['total'] - counters1['total']
    return 100 - (idle / total) * 100


def getmem():
    with open('/proc/meminfo') as f:
        total = float(f.readline().split()[1])
        free = float(f.readline().split()[1])
        buffers = float(f.readline().split()[1])
        cache = float(f.readline().split()[1])

    mem_use = total - free
    #mem_use = total - free -buffers -cache
    # print 'total: '+str(total)
    # print 'memuse: '+str(mem_use)
    return mem_use / total * 100


httpClient = None

try:
    while True:
        try:
            starttime = time.time()
            if __name__ == '__main__':
                cf = ConfigParser.RawConfigParser()
                cf.read("difoconf.ini")
                ipaddr = cf.get("HostAgent", "ipaddr")
                port = cf.get("HostAgent", "port")
                url = cf.get("HostAgent", "url")
                datetime = cf.get("HostAgent", "datetime")
                cupname = cf.get("HostAgent", "cupname")
                memname = cf.get("HostAgent", "memname")
                diskname = cf.get("HostAgent", "diskname")
                pingname = cf.get("HostAgent", "pingname")

                counters1 = readCpuInfo()
                time.sleep(1.9)
                timenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                counters2 = readCpuInfo()
                # print calcCpuUsage(counters1, counters2)
                time_nu = "%s" %timenow
                cpu_nu = "%.1f" %calcCpuUsage(counters1, counters2)
                mem_nu = "%.1f" %getmem()
                disk_nu = "%.1f" %disk_if('/')
                #ping_nu = getpinginfo()
                ping_nu = "%.1f" %getpinginfo(ipaddr)
                # print 'cpunulen: '+str(len(cpu_nu))
                # print 'memnulen: '+str(len(mem_nu))
                # print 'disknulen: '+str(len(disk_nu))
                # print 'pingnulen: '+str(len(ping_nu))


                # params = urllib.urlencode(
                #     {datetime: time_nu,
                #      cupname: cpu_nu,
                #      memname: mem_nu,
                #      diskname: disk_nu,
                #      pingname: ping_nu
                #     }
                # )
                params = {
                    'hostinfo':{
                        datetime: time_nu,
                        cupname: cpu_nu,
                        memname: mem_nu,
                        diskname: disk_nu,
                        pingname: ping_nu
                    }
                }
                # print '[+]params: ',params
                jsondata = json.dumps(params)
                # print '+++++++++++++++++++++++++++++'
                print '[+]jsondata: ',jsondata
                # headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
                zhongjian = time.time()
                # httpClient = httplib.HTTPSConnection( ipaddr, port, timeout=None)
                # httpClient.request("POST", url, params, headers)
                
                # response = httpClient.getresponse()
                # print response.status, response.reason
                # print response.read()
                # tmp = response.read()
                # print 'receive: '+str(len(tmp))
                url1 = 'https://%s:%s%s' % (ipaddr, port, url)
                request = os.popen(
                    r"curl -k -H 'Content-type:application/json' -X POST --data '%s' '%s' 2>/dev/null" % (
                    jsondata, url1) )
                print '[+]request:', request.read( )
                stoptime = time.time()
                # print "总时间：%.1fs, 程序处理时间：%.1fs, http访问时间：%.1fs" %((stoptime - starttime),(zhongjian - starttime),(stoptime - zhongjian))
                # print ""
                # print response.getheaders() #获取头信息

        except Exception, e:
            print "5秒后重试......"
            time.sleep(5)
            continue
        # finally:
        #     if httpClient:
        #         httpClient.close()
except Exception, e:
    print e
    # print "exception!!!!!!"
    # httpClient.close()
except KeyboardInterrupt:
    # httpClient.close()
    exit()
# finally:
#     if httpClient:
#         httpClient.close()
