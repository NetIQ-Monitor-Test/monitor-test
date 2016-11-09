#!/bin/bash
date=`date +%Y%m%d_%-H:%-M:%S`
while :
    do
        #sleep 30
        pid2=`ps -ef|grep servicemonitor.py|grep -v grep`
        if [ -z "$pid2" ];
        then
            python /root/python/servicemonitor.py &
        fi
    done

