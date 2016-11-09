#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "wanghn"

import os
os.popen("kill -s 9 `ps -ef | grep startsmoni.sh | grep -v grep | awk '{print $2}'`").readline()
os.popen("kill -s 9 `ps -ef | grep servicemonitor.py | grep -v grep | awk '{print $2}'`").readline()

