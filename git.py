# Git interface
import settings
import os
import subprocess

def git_call(rest, repo=settings.repo, gitexec=settings.gitexec):
    call = subprocess.Popen("%s --git-dir=%s %s" % (gitexec, repo, rest),
                            shell=True,
                            stdout=subprocess.PIPE)
    (out, err) = call.communicate()
    retcode = call.returncode
    return (out, err, retcode)

def show(file, rev=settings.revision):
    (out, err, ret) = git_call("show %s:%s" % (rev, file))
    return (out, ret)

def ls(file=None, name=False, rev=settings.revision):
    final = "ls-tree -r"
    if name:
        final += " --name-only"
    final += " %s" % rev
    if file != None:
        final += ":%s" % file
    (out, err, ret) = git_call(final)
    return (out.splitlines(), ret)

def type(file, rev=settings.revision):
    (out, err, ret) = git_call("cat-file -t %s:%s" % (rev, file))
    return (out.strip(), ret)

def log(file=None, num=None, format=None, rev=settings.revision):
    final = "log"
    if num != None:
        final += " -%d" % num
    if format != None:
        final += " --pretty=format:%s" % format
    final += " %s" % rev
    if file != None:
        final += " -- %s" % file
    (out, err, ret) = git_call(final)
    return (out.splitlines(), err)
        
