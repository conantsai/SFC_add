#! /usr/bin/env python3
#-*- coding:utf-8 -*-

import json
import os

from agents import nat

from flask import Flask,redirect
from flask import request
from flask import session
from flask import jsonify

app = Flask(__name__)

@app.route('/nat/rulelist', methods=['GET', 'POST'])
def rulelist():
    list = ""
    if request.method == 'POST':
        command = request.form['command']
        list = nat.rulelist(command)
        return json.dumps({"rulelist":list})
    else:
        return json.dumps({"rulelist":"error"})


@app.route('/nat/traceroute',methods=['GET','POST'])
def traceroute():
    print("----------")
    status = "Unknow"
    orderlist = ""
    if request.method == 'POST' :
        command = request.form['command']
        orderlist = nat.nattraceroute(command)
        #for line in os.popen(command.split("/")[0]):
        #    orderlist = orderlist + line.split("(")[1].split(")")[0] + ">"
        return json.dumps({"order":orderlist})
    else:
        return json.dumps({"order":"error"})

@app.route('/nat/rt',methods=['GET','POST'])
def rt():
    status = "Unknow"
    if request.method == 'POST' :
        command = request.form['command']
        print(command)
        status = nat.natrt(command)
        return json.dumps({"status":status})
    else:
        return json.dumps({"status":"error"})

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port='5000')
