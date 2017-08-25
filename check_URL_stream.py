#!/usr/bin/env python
######################################
# Script: check_URL_streams.py
# Date: 07/17/2017
# Author: Satish Botla
# Version 1.1
# Input: url.txt: all the hls.00 urls
######################################
import urllib2
import time

f = open('newurl.txt', 'r')
content = f.readlines()
content = [x.strip() for x in content]
for url in content:
    try:
        connection = urllib2.urlopen(url)
        #print(url , connection.getcode())
        time.sleep(1)
        connection.close()
    except urllib2.HTTPError, e:
        print(url , e.getcode())

