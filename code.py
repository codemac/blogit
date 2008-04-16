# First attempt at the git backed blog!

import web
import git

urls = (
    '/', 'index',
    '/(.*)', 'page',
    '/(.*)\.atom', 'atomize',
)

class index:
    def GET(self):
        print "Hello, world!"

def dirify(start, list):
    result = '<table>'
    dir = []
    for entry in list:
        e = entry.split()
        e[3] = '<a href="' + start + '/' + e[3] + '">' + e[3] + '</a>'
        result += '<tr>'
        for i in e:
            result += '<td>' + i + '</td>'
        result += '</tr>'
    result += '</table>'
    return result

class page:
    def GET(self, file):
        file = file.rstrip('/')
        (out, ret) = git.ls(file)
        if ret == 128:
            (out, ret) = git.show(file)
            if ret == 128:
                web.webapi.notfound()
            else:
                print out
        else:
            print dirify(file, out)


            
        

# Make an atom feed out of a directory in git.
class atomize:
    def GET(self, dir):
        print "Not yet!"
        

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    web.run(urls, globals(), web.reloader)
