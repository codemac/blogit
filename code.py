# First attempt at the git backed blog!

import web
import git

urls = (
    '/', 'index',
    '/atom/', 'atomize_all'
    '/atom/(.*)', 'atomize'
    '/(.*)', 'page',
)

class index:
    def GET(self):
        print "Hello, world!"

class page:
    def GET(self, file):
        res = git.show(file)
        if res == 404:
            web.webapi.notfound()
        else:
            print res

# Make an atom feed out of a directory in git.
class atomize:
    def GET(self, dir):
        

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    web.run(urls, globals(), web.reloader)
