#!/bin/bash
date=`date +%Y%m%d_%-H:%-M:%S`
while :
    do
        #sleep 30
        pid1=`ps -ef|grep difomonitor.py|grep -v grep`
        if [ -z "$pid1" ];
        then
            python /root/python/difomonitor.py &
        fi
    done

