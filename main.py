#!/usr/bin/env python3

import os, sys
from collections import namedtuple
from makefile_parse import interpret_theos_makefile
from contextlib import suppress
from enum import Enum

colors = [["\033[0;31m","\033[0;32m","\033[0;33m","\033[0;34m","\033[0;36m",
"\033[0;37m","\033[0m"],["\033[1;31m","\033[1;32m","\033[1;33m","\033[1;34m",
"\033[1;36m","\033[1;37m","\033[0m"]]

def dprintline(col: int, tool: str, textcol: int, bold: int, pusher: int, loc: str, msg: str):
    print("%s[%s]%s %s%s%s" % (
        colors[1][col], tool, colors[bold][textcol], loc + " >>> " if pusher else "", msg, colors[0][6]), file=sys.stdout)

dbstate = lambda loc, msg: dprintline(1, "theos-lint", 5, 1, 1, loc, msg)
dbwarn = lambda loc, msg: dprintline(2, "theos-lint", 5, 0, 1, loc, msg)
dberror = lambda loc, msg: dprintline(0, "theos-lint", 5, 1, 1, loc, msg)

class Severity(Enum):
    STATE = 0,
    WARN = 1,
    ERROR = 2

class Problem(object):
    def __init__(self, filename, fileline, severity, message="Problem Found"):
        self.name = filename
        self.line = str(fileline)
        self.sev = severity
        self.msg = message

class Project(object):
    
    def __init__(self):
        self.projectdict: dict = self.load_makefile()
        self.control: dict = {}
        self.cflines: list = []
        self.control, self.cflines = self.load_control()

    def load_control(self):
        lc = 0
        ctrl = {}
        cls = []
        with open('control') as control:
            for line in control:
                lc+=1
                cls.append(line)
                if ':' in line:
                    kv = (line.split(":", 1)[0], line.split(":", 1)[1])
                    if kv[0] in ctrl.keys():
                        # Nowhere else we can easily check this, 
                        # why not just do it here /shrug
                        dbwarn(f'control:{lc}', f'Duplicate control key "{kv[0]}"')
                    else:
                        ctrl[kv[0]] = kv[1].strip("\n")
        return (ctrl, cls)

    def load_makefile(self):
        with open('Makefile') as file:
            return interpret_theos_makefile(file)

class Checker(object):
    def __init__(self, project: Project):
        self.project = project 
        self.problems = []
    
    def foundProblem(self, filename: str, fileline: int, severity: Severity, message: str):
        self.problems.append(Problem(filename, fileline, severity.value, message))
    
    def check(self):
        self.check_control_format()
        self.check_dependencies()

    def check_control_format(self):
        # SYNTAX
        if self.project.cflines[-1] != "\n":
            self.foundProblem('control', len(self.project.cflines), Severity.ERROR, "Blank Line Required at end of control file")

    def check_dependencies(self):

        for k, v in self.project.projectdict.items():
            if isinstance(v, dict):
                if 'Cephei' in v['frameworks'] or 'CepheiPrefs' in v['frameworks']:
                    if self.project.control['Depends'] and 'ws.hbang.common' not in self.project.control['Depends']:
                        for i, line in enumerate(self.project.cflines):
                            if 'Depends:' in line:
                                self.foundProblem('control', i+1, Severity.ERROR, f'Project "{v["name"]}" depends on Cephei, but the control file is missing "ws.hbang.common (>= 1.11)" dependency')

                if v['type'] == "bundle":
                    if "Preferences" in v['frameworks']:
                        if self.project.control['Depends'] and 'preferenceloader' not in self.project.control['Depends']:
                            for i, line in enumerate(self.project.cflines):
                                if 'Depends:' in line:
                                    self.foundProblem('control', i+1, Severity.ERROR, "Project has prefs but is missing 'preferenceloader' dependency in control file")



project_checker = Checker(Project())
project_checker.check()
exitflag = 0
for problem in project_checker.problems:
    if problem.sev == Severity.STATE:
        dbstate(problem.name + ":" + problem.line, problem.msg)
    elif problem.sev == Severity.WARN:
        dbwarn(problem.name + ":" + problem.line, problem.msg)
    else:
        exitflag=1
        dberror(problem.name + ":" + problem.line, problem.msg)
exit(exitflag)
#print(project_checker.project.projectdict)