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

def show(file, rev='HEAD', repo=settings.repo):
    (out, err, retcode) = git_call("show %s:%s" % (rev, file))
    if retcode == 128:
        return 404
    else:
        return out
    
    

def ls(rev='HEAD', repo=settings.repo):
    result = os.popen("git --git-dir=%s ls-tree -r --name-only %s" % (repo, rev)).readlines()
    shown.close()
    return result
