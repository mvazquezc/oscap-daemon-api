import dbus
import json
import os
from datetime import datetime

OBJECT_PATH = "/OpenSCAP/daemon"
DBUS_INTERFACE = "org.OpenSCAP.daemon.Interface"
BUS_NAME = "org.OpenSCAP.daemon"

class OScapDaemonApi:
    def __init__(self):
        self.dbusIface = self.connect()
        
    def connect(self):     
        varName = "OSCAPD_SESSION_BUS"
        obj = None
        if varName in os.environ and os.environ[varName] == "1":
            bus = dbus.SessionBus()
        else:
            bus = dbus.SystemBus()
        if bus is None:
            print "Cannot connect to the bus."
        try:
            obj = bus.get_object(BUS_NAME,OBJECT_PATH)
        except:
            pass
        if obj is None:
            print "Cannot connect to the bus. Is the daemon running?"
        return dbus.Interface(obj, DBUS_INTERFACE)

    def get_ssg(self, ssgFile, tailoringFile):
        if ssgFile == "system":
            ssgChoices = self.dbusIface.GetSSGChoices()
        else:
            ssgChoices = [ssgFile]
        ssgs = []
        for ssgChoice in ssgChoices:
            try:
                ssgFile = os.path.abspath(ssgChoice)
                if tailoringFile in [None, ""]:
                   tailoringFile = ""
                else:
                    tailoringFile = os.path.abspath(tailoringFile)
                profiles = self.dbusIface.GetProfileChoicesForInput(ssgFile, tailoringFile)
                ssgProfile = []
                for profileId,profileName in profiles.items():
                    ssgProfile.append({ 'profileId': profileId, 'profileName': profileName })
                ssgs.append({ 'ssgfile': ssgFile, 'tailoringFile': tailoringFile, 'profiles': ssgProfile })
            except:
                break 
        ssgsJson = '{ "ssgs":' + json.dumps(ssgs, indent=4) + '}'
        return ssgsJson

    def get_task(self, task):
        if task == "all":
            tasksIds = self.dbusIface.ListTaskIDs()
        else:
            tasksIds = [task]
        tasks = []
        for taskId in tasksIds:
            try:
                title = self.dbusIface.GetTaskTitle(taskId)
                target = self.dbusIface.GetTaskTarget(taskId)
                modifiedTimestamp = self.dbusIface.GetTaskModifiedTimestamp(taskId)
                modified = datetime.fromtimestamp(modifiedTimestamp)
                enabled = self.dbusIface.GetTaskEnabled(taskId)
                taskResultsIds = self.dbusIface.GetTaskResultIDs(taskId)
                taskResults = []
                for taskResultId in taskResultsIds:
                    exitCode = self.dbusIface.GetExitCodeOfTaskResult(taskId, taskResultId)
                    timestamp = self.dbusIface.GetResultCreatedTimestamp(taskId, taskResultId)
                    # Exit code 0 means evaluation was successful and machine is compliant.
                    # Exit code 1 means there was an error while evaluating.
                    # Exit code 2 means there were no errors but the machine is not compliant.
                    if exitCode == 0:
                        status = "Compliant"
                    elif exitCode == 1:
                        status = "Non-Compliant"
                    elif exitCode == 2:
                        status = "Evaluation Error"
                    else:
                        status = "Unknow status for exitCode " + exitCode
                    taskResults.append({ 'taskResultId': str(taskResultId), 'taskResulttimestamp': timestamp, 'taskResultStatus': status }) 
                tasks.append({ 'id': str(taskId), 'title': title, 'target': target, 'modified': str(modified), 'enabled': enabled, 'results': taskResults })
            except:
                break 
        tasksJson = '{ "tasks":' + json.dumps(tasks, indent=4) + '}'
        return tasksJson

    def get_task_guide(self, task):
        guideHtml = ""
        try:
            guideHtml = self.dbusIface.GenerateGuideForTask(task)
        except:
            pass
        return guideHtml

    def get_task_result(self, task, result):
        resultHtml = ""
        try:
            resultHtml = self.dbusIface.GenerateReportForTaskResult(task, result)
        except:
            pass
        return resultHtml

    def remove_task_result(self, task, result):
        tasksIds = [task]
        taskResultsIds = [result]
        remove = []
        for taskId in tasksIds:
            taskResults = []
            for taskResultId in taskResultsIds:
                try:
                    if taskResultId == "all":
                        self.dbusIface.RemoveTaskResults(taskId)
                    else:
                        self.dbusIface.RemoveTaskResult(taskId,taskResultId)
                    taskResults.append({ 'taskResultId': str(taskResultId), 'removed': 'true' })
                except:
                    break
            remove.append({ 'id': str(taskId), 'taskResultsRemoved': taskResults })
        removeJson = '{ "tasks":' + json.dumps(remove, indent=4) + '}'
        return removeJson

    def run_task_outside_schedule(self, task):
        tasksIds = [task]
        run = []
        for taskId in tasksIds:    
            try:
                taskEnabled = self.dbusIface.GetTaskEnabled(taskId)
                if taskEnabled:
                    try:
                        self.dbusIface.RunTaskOutsideSchedule(task)
                        run.append({ 'id': taskId, 'running': 'true' })
                    except:
                        run.append({ 'id': taskId, 'running': 'Task seems to be already running' })
                else:
                    run.append({ 'id': taskId, 'running': 'Task must be enabled first' })
            except:
               break
        runJson = '{ "tasks": ' + json.dumps(run, indent=4) + '}'
        return runJson

    def remove_task(self, task):
        tasksIds = [task]
        delete = []
        for taskId in tasksIds:
            try:
                taskSchedule = self.dbusIface.GetTaskEnabled(taskId)
                if taskSchedule == 0:
                    self.dbusIface.RemoveTask(taskId, True) #TODO: remove results or not
                    delete.append({ 'id': taskId, 'removed': 'true' })
                else:
                    delete.append({ 'id': taskId, 'removed': 'enabled tasks cannot be deleted' })
            except:
                break
        deleteJson = '{ "tasks":' + json.dumps(delete, indent=4) + '}'
        return deleteJson

    def task_schedule(self, task, status):
        tasksIds = [task]
        schedule = []
        for taskId in tasksIds:
           try:
               if status == "enable":
                   self.dbusIface.SetTaskEnabled(taskId, True) 
               elif status == "disable":
                   self.dbusIface.SetTaskEnabled(taskId, False)
               else:
                   status = "not_modified"
               schedule.append({ 'id': taskId, 'schedule': status })
           except:
               break
        scheduleJson = '{ "tasks":' + json.dumps(schedule, indent=4) + '}'
        return scheduleJson

    def new_task(self, taskTitle, taskTarget, taskSSG, taskTailoring, taskProfileId, taskOnlineRemediation, taskScheduleNotBefore, taskScheduleRepeatAfter):
        # Setup defaults / normalize input
        if taskTarget == "":
            taskTarget = "localhost"

        if taskOnlineRemediation not in [1,"y","Y","yes"]:
            taskOnlineRemediation = False

        if taskScheduleNotBefore == "":
            taskScheduleNotBefore = datetime.now()
        else:
            try:
                taskScheduleNotBefore = datetime.strptime(taskScheduleNotBefore, "%Y-%m-%d %H:%M")
            except:
                taskScheduleNotBefore = datetime.now()

        if taskScheduleRepeatAfter == "":
            taskScheduleRepeatAfter = False
        elif taskScheduleRepeatAfter == "@daily":
            taskScheduleRepeatAfter = 1 * 24
        elif taskScheduleRepeatAfter == "@weekly":
            taskScheduleRepeatAfter = 7 * 24
        elif taskScheduleRepeatAfter == "@monthly":
            taskScheduleRepeatAfter = 30 * 24
        else:
            try:
                taskScheduleRepeatAfter = int(taskScheduleRepeatAfter)
            except:
                taskScheduleRepeatAfter = False

        taskId = self.dbusIface.CreateTask()
        self.dbusIface.SetTaskTitle(taskId, str(taskTitle))
        self.dbusIface.SetTaskTarget(taskId, taskTarget)
        self.dbusIface.SetTaskInput(taskId, taskSSG)
        self.dbusIface.SetTaskTailoring(taskId, taskTailoring)
        self.dbusIface.SetTaskProfileID(taskId, taskProfileId)
        self.dbusIface.SetTaskOnlineRemediation(taskId, taskOnlineRemediation)
        self.dbusIface.SetTaskScheduleNotBefore(taskId, taskScheduleNotBefore.strftime("%Y-%m-%dT%H:%M"))
        self.dbusIface.SetTaskScheduleRepeatAfter(taskId, taskScheduleRepeatAfter)
        task = [ { 'id' : taskId, 'enabled' : '0'} ]
        createJson = '{ "tasks":' + json.dumps(task, indent=4) + '}'
        return createJson

    def update_task(self, taskId, taskTitle, taskTarget, taskSSG, taskTailoring, taskProfileId, taskOnlineRemediation, taskScheduleNotBefore, taskScheduleRepeatAfter):
        task = []
        try:
            enabled = self.dbusIface.GetTaskEnabled(taskId)          
            if taskTitle != "":
                 self.dbusIface.SetTaskTitle(taskId, str(taskTitle))
            if taskTarget != "":
                 self.dbusIface.SetTaskTarget(taskId, taskTarget)
            if taskSSG != "":
                 self.dbusIface.SetTaskInput(taskId, taskSSG)
            if taskTailoring != "":
                 self.dbusIface.SetTaskTailoring(taskId, taskTailoring)
            if taskProfileId != "":
                 self.dbusIface.SetTaskProfileID(taskId, taskProfileId)
            if taskOnlineRemediation != "":
                if taskOnlineRemediation not in [1,"y","Y","yes"]:
                    taskOnlineRemediation = False 
                self.dbusIface.SetTaskOnlineRemediation(taskId, taskOnlineRemediation)
            if taskScheduleNotBefore != "":
                try:
                    taskScheduleNotBefore = datetime.strptime(taskScheduleNotBefore, "%Y-%m-%d %H:%M")
                except:
                    taskScheduleNotBefore = datetime.now()
                self.dbusIface.SetTaskScheduleNotBefore(taskId, taskScheduleNotBefore.strftime("%Y-%m-%dT%H:%M"))
            if taskScheduleRepeatAfter != "":
                if taskScheduleRepeatAfter == "@daily":
                    taskScheduleRepeatAfter = 1 * 24
                elif taskScheduleRepeatAfter == "@weekly":
                    taskScheduleRepeatAfter = 7 * 24
                elif taskScheduleRepeatAfter == "@monthly":
                    taskScheduleRepeatAfter = 30 * 24
                else:
                    try:
                        taskScheduleRepeatAfter = int(taskScheduleRepeatAfter)
                    except:
                        taskScheduleRepeatAfter = False
                self.dbusIface.SetTaskScheduleRepeatAfter(taskId, taskScheduleRepeatAfter)
            task.append({ 'id': str(taskId), 'enabled': enabled, 'updated': 'true' })
        except:
            pass
        updateJson = '{ "tasks":' + json.dumps(task, indent=4) + '}'
        return updateJson

