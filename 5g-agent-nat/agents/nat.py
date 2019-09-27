#! /usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import json
from pprint import pprint
from urllib import request
from urllib import parse
from http import cookiejar

def natrt(command):
    #print(command)
    os.system(command)
    return True

def nattraceroute(command):
    orderlist = ""
    for line in os.popen(command.split("/")[0]):
        orderlist = orderlist + line.split("(")[1].split(")")[0] + ">"
    return orderlist

def rulelist(command):
    list = ""
    for line in os.popen(command):
        list = list + line
    print (list)
    return list
