# First attempt at the git backed blog!

import web
import git
import feed

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
        xmldoc, atom = feed.new_xmldoc_feed()
        feed.title = "My Feed!"
        feed.id = "http://codemac.net" # << url to feed
        feed.updated = "last date of entry?"
        links = Link("http://codemac.net") # << url to home.
        feed.links.append(link)
        author = Author("Jeff Mickey")
        feed.authors.append(author)
        
        
        entry = feed.atom.Entry()
        entry.title = "" # title
        entry.id = "" # The url
        entry.updated = "" # date updated
        entry.content = "" # das content!
        feed.entries.append(entry)
        print str(xmldoc)
        

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    web.run(urls, globals(), web.reloader)
