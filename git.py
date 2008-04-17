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

def show(file, rev='HEAD'):
    (out, err, ret) = git_call("show %s:%s" % (rev, file))
    return (out, ret)

def ls(file=None, rev='HEAD'):
    if file == None:
        (out, err, ret) = git_call("ls-tree -r %s" % rev)
    else:
        (out, err, ret) = git_call("ls-tree -r %s:%s" % (rev,file))
    return (out.splitlines(), ret)

def type(file, rev='HEAD'):
    (out, err, ret) = git_call("cat-file -t %s:%s" % (rev, file))
    return (out.strip(), ret)
