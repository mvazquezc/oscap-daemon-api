#!/usr/bin/python
try:
    import ConfigParser as configparser
except ImportError:
    # ConfigParser has been renamed to configparser in python3
    import configparser

import os
import os.path
from flask import Flask, jsonify, request
from lib.oscapdapi import OScapDaemonApi
from flask_basicauth import BasicAuth

app = Flask(__name__)

@app.route('/tasks', methods=['GET'])
def getTasks():
    response = oscapd.get_task("all")
    return response

@app.route('/tasks', methods=['POST'])
def newTask():
    content = request.get_json(silent=False)
    requiredFields = {'taskTitle', 'taskTarget', 'taskSSG', 'taskTailoring', 'taskProfileId', 'taskOnlineRemediation', 'taskScheduleNotBefore', 'taskScheduleRepeatAfter' } 
    if content is None:
        return '{ "Error" : "json data required" }', 400
    elif not requiredFields <= set(content):
        return '{ "Error": "There are missing fields in the request" }', 400
    elif content['taskSSG'] == "" or content['taskProfileId'] == "":
        return '{ "Error": "Both taskSSG and taskProfileId fields cannot be empty" }', 400
    else:
        response = oscapd.new_task(content['taskTitle'], content['taskTarget'],
            content['taskSSG'], content['taskTailoring'], content['taskProfileId'],
            content['taskOnlineRemediation'], content['taskScheduleNotBefore'],
            content['taskScheduleRepeatAfter'])
        return response, 201

@app.route('/tasks/<int:taskId>', methods=['PUT'])
def updateTask(taskId):
    content = request.get_json(silent=False)
    requiredFields = {'taskTitle', 'taskTarget', 'taskSSG', 'taskTailoring', 'taskProfileId', 'taskOnlineRemediation', 'taskScheduleNotBefore', 'taskScheduleRepeatAfter' }
    if content is None:
        return '{ "Error" : "json data required" }', 400
    elif not requiredFields <= set(content):
        return '{ "Error": "There are missing fields in the request" }', 400
    else:
        response = oscapd.update_task(taskId, content['taskTitle'], content['taskTarget'],
            content['taskSSG'], content['taskTailoring'], content['taskProfileId'],
            content['taskOnlineRemediation'], content['taskScheduleNotBefore'],
            content['taskScheduleRepeatAfter'])
        return response

@app.route('/tasks/<int:taskId>', methods=['GET'])
def getTask(taskId):
    response = oscapd.get_task(taskId)
    return response

@app.route('/tasks/<int:taskId>/guide', methods=['GET'])
def getTaskGuide(taskId):
    response = oscapd.get_task_guide(taskId)
    return response

@app.route('/tasks/<int:taskId>/result/<int:resultId>', methods=['GET'])
def getTaskResult(taskId,resultId):
    response = oscapd.get_task_result(taskId,resultId)
    return response

@app.route('/tasks/<int:taskId>/result', methods=['DELETE'])
def remoteTaskResults(taskId):
    response = oscapd.remove_task_result(taskId,"all")
    return response

@app.route('/tasks/<int:taskId>/result/<int:resultId>', methods=['DELETE'])
def removeTaskResult(taskId,resultId):
    response = oscapd.remove_task_result(taskId,resultId)
    return response

@app.route('/tasks/<int:taskId>/run', methods=['GET'])
def runTaskOutsideSchedule(taskId):
    response = oscapd.run_task_outside_schedule(taskId)
    return response

@app.route('/tasks/<int:taskId>', methods=['DELETE'])
def removeTask(taskId):
    response = oscapd.remove_task(taskId)
    return response

@app.route('/tasks/<int:taskId>/<string:schedule>', methods=['PUT'])
def taskSchedule(taskId,schedule):
    response = oscapd.task_schedule(taskId,schedule)
    return response

@app.route('/ssgs', methods=['GET'])
def getSSGs():
    response = oscapd.get_ssg("system","")
    return response

@app.route('/ssgs', methods=['POST']) 
def getSSG():
    content = request.get_json(silent=False)
    requiredFields = {'ssgFile', 'tailoringFile' }
    if content is None:
        return '{ "Error" : "json data required" }', 400
    elif not requiredFields <= set(content):
        return '{ "Error": "There are missing fields in the request" }', 400
    elif content['ssgFile'] == "":
        return '{ "Error": "ssgFile field cannot be empty" }', 400
    else:
        response = oscapd.get_ssg(content['ssgFile'],content['tailoringFile'])
        return response

if __name__ == "__main__":
    oscapd = OScapDaemonApi()
    config = configparser.ConfigParser()
    config.read('config.ini')
    c_debug = config.getboolean('Api','debug')
    c_host = config.get('Api','host')
    c_port = config.get('Api','port')
    c_auth = config.getboolean('Api','auth')
    if c_auth:
      basic_auth = BasicAuth(app)
      app.config['BASIC_AUTH_USERNAME'] = config.get('Api','username')
      app.config['BASIC_AUTH_PASSWORD'] = config.get('Api','password')
      app.config['BASIC_AUTH_FORCE'] = True
    # Uncomment when testing
    app.debug = c_debug
    app.run(host=c_host, port=c_port)
