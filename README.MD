# OpenSCAP Daemon API
> Python API on top of the OpenSCAP Daemon

> Inspired by oscapd-cli

> For who don't want to use foreman in order to manage Oscap Daemon via webUI

## Project Description
OScapDApi is a service that runs on top of the OpenSCAP Daemon (oscapd) providing a RESTful API.

Throught this API you can perform almost all operations already available in oscapd-cli tool. API 
interacts with the daemon using dbus.

## Features
* Get all/specific tasks registered on the daemon
* Create new tasks 
* Modify existing tasks
* Get task's guide info
* Get taks's results reports
* Delete all/specific results from tasks
* Launch specific tasks
* Enable/Disable specific tasks
* Get SSGs and its profiles
* Show SSG's profiles for a requested file

## Endpoints:

| Endpoint                                  | VERB   | CLI Equivalent                               | Description                                               |
|-------------------------------------------|--------|----------------------------------------------|-----------------------------------------------------------|
| /tasks                                    | GET    | oscapd-cli task                              | Gets all tasks with its information                       |
| /tasks                                    | POST   | oscapd-cli task-create -i                    | Creates new tasks                                         |
| /tasks/<int:taskId>                       | PUT    | oscapd-cli task <taskId> set-XXX             | Modify tasks                                              |
| /tasks/<int:taskId>                       | GET    | oscapd-cli task <taskId>                     | Gets information about <taskId>                           |
| /tasks/<int:taskId>                       | DELETE | oscapd-cli task <taskId> remove              | Remove task <taskId> and its results                      |
| /tasks/<int:taskId>/guide                 | GET    | oscapd-cli task <taskId> guide               | Gets <taskId> guide info. Note: HTML Output               |
| /tasks/<int:taskId>result/<int:resultId>  | GET    | oscapd-cli result <taskId> <resultId> report | Gets <resultId> report for <taskId>. Note: HTML Output    |
| /tasks/<int:taskId>/result                | DELETE | oscapd-cli result <taskId> remove            | Removes all results for <taskId>                          |
| /tasks/<int:taskId>/result/<int:resultId> | DELETE | oscapd-cli result <taskId> <resultId> remove | Removes <resultId> in <taskId>                            |
| /tasks/<int:taskId>/run                   | GET    | oscapd-cli task <taskId> run                 | Launch task with id <taskId>                              |
| /tasks/<int:taskId>/<string:schedule>     | PUT    | oscapd-cli task <taskId> enable/disable      | Enables/Disables <taskId>                                 |
| /ssgs                                     | GET    |                                              | Returns all SSGs installed on the system and its profiles |
| /ssgs                                     | POST   |                                              | Shows SSG's profiles within a json request                |

## Examples:

Get all tasks: 
```
curl -i http://127.0.0.1:5000/tasks -X GET
```

Create a new task:
```
newtask.json 
{
    "taskTitle":"New Task test",
    "taskTarget":"localhost",
    "taskSSG":"/usr/share/xml/scap/ssg/content/ssg-jre-ds.xml",
    "taskTailoring":"",
    "taskProfileId":"xccdf_org.ssgproject.content_profile_stig-java-upstream",
    "taskOnlineRemediation":"1",
    "taskScheduleNotBefore":"",
    "taskScheduleRepeatAfter":""
}
  
curl -i http://127.0.0.1:5000/tasks -X POST -H "Content-Type: application/json" -d '@newtask.json'
```

Update an existing task:   
```
updatetask.json
{
    "taskTitle":"New Task test modified",
    "taskTarget":"localhost",
    "taskSSG":"",
    "taskTailoring":"",
    "taskProfileId":"",
    "taskOnlineRemediation":"yes",
    "taskScheduleNotBefore":"",
    "taskScheduleRepeatAfter":""
}
    
curl -i http://127.0.0.1:5000/tasks/1 -X PUT -H "Content-Type: application/json" -d '@updatetask.json'
```

Get info from existing task:
```
curl -i http://127.0.0.1:5000/tasks/1 -X GET
``` 

Get guide info from existing task:
```
curl -i http://127.0.0.1:5000/tasks/1/guide -X GET
```

Get result from existing task:
```
curl -i http://127.0.0.1:5000/tasks/1/result/1 -X GET
```

Delete all results from existing task:
```
curl -i http://127.0.0.1:5000/tasks/1/result -X DELETE
```

Delete result from existing task:
```
curl -i http://127.0.0.1:5000/tasks/1/result/1 -X DELETE
```

Launch existing task:
```
curl -i http://127.0.0.1:5000/tasks/1/run -X GET
```

Enable/Disable existig task:
```
curl -i http://127.0.0.1:5000/tasks/1/enable -X PUT
curl -i http://127.0.0.1:5000/tasks/1/disable -X PUT
```

Get all SSGs installed on the system:
```
curl -i http://127.0.0.1:5000/ssgs -X GET
```

Get SSG's profiles within json's request:
```
ssg.json
{
    "ssgFile": "/usr/share/xml/scap/ssg/content/ssg-centos7-ds.xml",
    "tailoringFile": ""
}
    
curl -i http://127.0.0.1:5000/ssgs -X POST -H "Content-Type: application/json" -d '@ssg.json'
```
### Install
1. Install python, dbus-python, pip, pipenv
2. pipenv --site-packages
3. pipenv install
4. pipenv run python api.py

## Some references:
* https://github.com/OpenSCAP/openscap-daemon/blob/master/bin/oscapd-cli
* https://github.com/OpenSCAP/openscap-daemon/blob/master/openscap_daemon/dbus_daemon.py
* https://github.com/OpenSCAP/openscap-daemon/blob/master/openscap_daemon/system.py
* https://github.com/OpenSCAP/openscap-daemon/blob/master/openscap_daemon/task.py#
