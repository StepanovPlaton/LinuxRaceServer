#!/usr/bin/env python3

# -*- coding: utf-8 -*-

from flask import Flask, render_template, send_file, request, jsonify
from time import sleep
import threading

from Modules.SocketServer import *
from Modules.DataBaseAPI import *

Server = SocketServerClass(DataBaseAPI, 9090)
FlaskServer = Flask(__name__, template_folder="templates")

@FlaskServer.route("/")
def index(): return "Hello World!"

FlaskServer.run(host='0.0.0.0', port=8080)
