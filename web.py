"""
 Module provides web interface to ongoing semantic web research by Jeremy 
 Nelson

"""
__author__ = "Jeremy Nelson"

import datetime
import os

from bottle import template, request, route, run, static_file

PROJECT_ROOT = os.path.abspath(__name__)


@route("/")
def index():
    record_sets = {}
    
    return template('index')

run(host='localhost', port=8042)
