# First attempt at the git backed blog!

import web
import git
import settings
import feed.atom

urls = (
    '/', 'index',
    '/(.*)\.atom', 'atomize',
    '/(.*)', 'page',
)

class index:
    def GET(self):
        print dirify('/', git.ls()[0])

def dirify(start, list):
    result = '<table>\n'
    dir = []
    if start != '/':
        start = '/'+start+'/'
    for entry in list:
        e = entry.split()
        e[3] = '<a href="'+start+e[3]+'">'+e[3]+'</a>'
        result += '\t<tr>\n'
        for i in e:
            result += '\t\t<td>' + i + '</td>\n'
        result += '\t</tr>\n'
    result += '</table>\n'
    return result

class page:
    def GET(self, file):
        file = file.rstrip('/')
        (out, ret) = git.type(file)
        if ret == 128:
            web.webapi.notfound()
        elif out == 'blob':
            (fout, fret) = git.show(file)
            print fout
        elif out == 'tree':
            print dirify(file, git.ls(file)[0])
        else:
            web.webapi.notfound()


# Make an atom feed out of a directory in git.
class atomize:
    def GET(self, dir):
        dir = dir.rstrip('/')
        (out, ret) = git.type(dir)
        if ret == 128:
            web.webapi.notfound()
        elif out == 'blob':
            print self.file_feed(dir)
        elif out == 'tree':
            print self.dir_feed(dir)
        else:
            web.webapi.notfound()
    
    def dir_feed(self, dir):
        xmldoc, dfeed = feed.atom.new_xmldoc_feed()
        dfeed.title = settings.blog_name + " " + dir
        dfeed.id = settings.blog_url + '/' + dir # << url for feed
        dfeed.updated = self.atom_date(dir)
        links = feed.atom.Link(settings.blog_url) # << url to home.
        dfeed.links.append(links)
        selflink = feed.atom.Link(settings.blog_url + '/' + dir + '.atom')
        selflink.attrs.rel = "self"
        dfeed.links.append(selflink)

        (aout, aerr) = git.log(file=dir, format="%an")
        for a in self.atom_authors(aout):
            author = feed.atom.Author(a)
            dfeed.authors.append(author)
        
        (eout, eerr) = git.ls(file=dir, name=True)
        for e in eout:
            e = dir + '/' + e
            entry = feed.atom.Entry()
            (entry.content, ecerr) = git.show(e)
            entry.title = entry.content.text.splitlines()[0]
            entry.id = settings.blog_url + '/' + e
            entry.updated = self.atom_date(e.lstrip('/'))

            dfeed.entries.append(entry)

        return str(xmldoc)
    
    def atom_authors(self, arr):
        res = []
        for a in arr:
            if a not in res:
                res.append(a)
        return res

    def atom_date(self, file):
        (arr, err) = git.log(file=file, num=1, format="%ai") 
        arr = arr[0].split()
        return arr[0] + 'T' + arr[1] + arr[2]
        

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    web.run(urls, globals(), web.reloader)
