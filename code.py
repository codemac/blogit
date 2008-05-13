# First attempt at the git backed blog!

import web
import git
import settings
import feed.atom
from jinja import Environment, FunctionLoader


urls = (
    '/', 'index',
    '/(.*)\.atom', 'atomize',
    '/(.*)', 'page',
)

# Template environment
def load_template(templ):
    (res, err) = git.show(settings.templates + '/' + templ)
    return res

tenv = Environment(loader=FunctionLoader(load_template))

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

# Get jinja comments that define the template dict to send.
# something like:
#    {# template : sometemplate.html #}
#    {# title : This is some entry #}
#    {# metadata : 23847123987129387 #}
def get_dict(str):
    fin = {}
    lines = str.splitlines()
    strfin = []
    for line in lines:
        if line.find("{#") > -1:
            (vari, colo, valu) = line.replace('{# ', ''
                                              ).replace(' #}', ''
                                                        ).partition(' : ')
            fin[vari] = valu
        else:
            strfin.append(line)

    fin['content'] = '\n'.join(strfin)

    if 'template' not in fin:
        fin['template'] = 'default.html'

    templ = fin['template']
    del fin['template']
    return (templ, fin)
            

    

class page:
    def GET(self, file):
        file = file.rstrip('/')
        (out, ret) = git.type(file)
        if ret == 128:
            web.webapi.notfound()
        elif out == 'blob':
            (fout, fret) = git.show(file)
            (templ, dict) = get_dict(fout)
            templ = tenv.get_template(templ)
            print templ.render(dict)
        elif out == 'tree':
            print dirify(file, git.ls(file)[0])
        else:
            web.webapi.notfound()


# Make an atom feed out of a directory in git.
class atomize:
    def GET(self, dir):
        dir = dir.rstrip('/').lstrip('/')
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
        selflink.attrs['rel'] = "self"
        dfeed.links.append(selflink)

        for a in self.atom_authors(dir):
            author = feed.atom.Author(a)
            dfeed.authors.append(author)
        
        (eout, eerr) = git.ls(file=dir, name=True)
        for e in eout:
            if dir != '':
                e = dir + '/' + e
            entry = feed.atom.Entry()
            (entryc, ecerr) = git.show(e)
            entry.content = "<![CDATA[\n" + entryc + "\n]]>"
            entry.title = entryc.splitlines()[0]
            entry.id = settings.blog_url + '/' + e
            entry.updated = self.atom_date(e.lstrip('/'))

            dfeed.entries.append(entry)

        return str(xmldoc)


    def file_feed(self, file):
        xmldoc, dfeed = feed.atom.new_xmldoc_feed()
        dfeed.title = settings.blog_name + " " + file
        dfeed.id = settings.blog_url + '/' + file
        dfeed.updated = self.atom_date(file)
        links = feed.atom.Link(settings.blog_url)
        dfeed.links.append(links)
        selflink = feed.atom.Link(settings.blog_url + '/' + file + '.atom')
        selflink.attrs['rel'] = "self"
        dfeed.links.append(selflink)
        
        for a in self.atom_authors(file):
            author = feed.atom.Author(a)
            dfeed.authors.append(author)
        
        
        (blobs, berr) = git.log(file=file, num=10, format="%H")
        for b in blobs.splitlines():
            entry = feed.atom.Entry()
            (entryc, err) = git.log(file=file, num=1, extopts="--stat -p -M -C --full-index", rev=b)
            entry.content = "<![CDATA[\n" + entryc + "\n]]>"
            entry.title = "%s : %s" % (file, b)
            entry.id = settings.blog_url + '/' + file
            entry.updated = self.atom_date(file, rev=b)
            
            dfeed.entries.append(entry)
        
        return str(xmldoc)
        

    def atom_authors(self, arr):
        (arr, err) = git.log(file=arr, format="%an")
        res = []
        for a in arr.splitlines():
            if a not in res:
                res.append(a)
        return res

    def atom_date(self, file, rev=None):
        if rev == None:
            (arr, err) = git.log(file=file, num=1, format="%ai")
        else:
            (arr, err) = git.log(file=file, num=1, format="%ai", rev=rev)
        arr = arr.splitlines()[0].split()
        return arr[0] + 'T' + arr[1] + arr[2]
        

web.webapi.internalerror = web.debugerror
if __name__ == "__main__":
    web.run(urls, globals(), web.reloader)
