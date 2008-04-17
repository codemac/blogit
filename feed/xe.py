# xe -- XML elements Python classes

# This is the BSD license. For more information, see:
# http://www.opensource.org/licenses/bsd-license.php
#
# Copyright (c) 2006, Steve R. Hastings
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
# 
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the
#       distribution.
# 
#     * Neither the name of Steve R. Hastings nor the names
#       of any contributors may be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



"""
Classes to work with XML elements in a Pythonic way.

This library module contains classes to represent XML elements.

Some important classes:

    TextElement  an XML element that contains text data
    NestElement  an XML element that contains other XML elements
    Element      can act like a TextElement or a NestElement
    XMLDoc       a container for XML element items

    ListElement  an XML element that holds 0 or more elements of a type
    Collection   a container that holds 0 or more elements of a type

    XMLText      a container for pieces of text not in an element

When you are nesting elements inside other elements, you give each
nested element a name; it's usually best to use the tag name value as
the name of the nested element.

Most of this module is designed for working with structured XML data,
such as syndication feed files.  To work with unstructured data, you
will probably want to use a Collection of ElementItem; see the XMLText
class for more information.


Please send questions, comments, and bug reports to: xe@langri.com
"""


import types



module_name = "xe"
module_version = "0.7.4"
module_banner = "%s version %s" % (module_name, module_version)



def set_indent_str(s):
    """
    Set the default string used to indent tags.

    Arguments:
        s -- string to use as the new tag indent string.

    The default indent is a single tab character.
    """
    global s_indent
    global lst_indent
    s_indent = s
    lst_indent = [s_indent*i for i in range(25)]

set_indent_str("\t")



class TFC(object):
    """
    TFC stands for "Tag Format Control".
    A TFC controls how tags are converted to strings.

    Arguments to __init__():
        level  Specifies what indent level to start at.  Default 0.
        mode   Specifies how to format the output:
            mode_terse -- minimal output (not indented)
            mode_normal -- default output (indented)
            mode_verbose -- output as much information as possible

    Normally, if a nested XML item has no data, it will be left out of the
    tag string; but with mode_verbose you will get an empty compact tag.
    For example, if a foo tag contains a nested bar tag, and the bar tag
    is empty, with mode_verbose you will get:
    <foo>
        <bar/>
    </foo>

    With mode_normal or mode_terse, you would just get: "<foo/>"

    With mode_verbose on a collection, you get a comment similar to this:
        <!-- collection of Author with 0 elements -->

    Methods:
        show_all()
            Return True if TFC set to make a tag string even if the item
            is blank.
        terse()
            Return True if TFC set for terse tag strings.
        verbose()
            Return True if TFC set for verbose tag strings.

        indent_by(incr)
            Return a TFC instance that indents by incr levels.
        s_indent(extra_indent=0)
            Return an indent string.
    """
    mode_terse, mode_normal, mode_verbose = range(3)

    def __init__(self, level=None, mode=None, tfc=None):
        """
        Arguments:
            level
                Indent level at which to start.  Default: 0
            mode
                How to format the output.  Default: mode_normal
                    mode_terse -- minimal output (not indented)
                    mode_normal -- default output (indented)
                    mode_verbose -- output as much information as possible
            tfc
                If provided, initialize this TFC from specified tfc.

        See the doc string for the whole class for examples what of
        mode_verbose does for tag output.
        """
        if tfc is not None:
            # copy settings from another TFC
            self.level = tfc.level
            self.mode = tfc.mode
            self.attr_sep = tfc.attr_sep
            self.tag_sep = tfc.tag_sep
        else:
            # set defaults
            self.level = 0
            self.mode = TFC.mode_normal
            self.attr_sep = " "
            self.tag_sep = "\n"

        # override defaults if arguments specified
        if level is not None:
            self.level = level
        if mode is not None:
            self.mode = mode

    def show_all(self):
        """
        Return True if TFC is set to show even empty elements.

        Empty tags usually just don't appear in a tag string; but we
        want a tag string even for an empty tag if the current level
        is 0, so that if you print a tag you don't ever just get an
        empty string.

        And if the mode is mode_verbose, of course we always get tag
        strings for everything.

        The tag string code uses this to decide when to return a tag
        string for an empty element, and when to return just an empty
        string.
        """
        return self.level == 0 or self.mode == TFC.mode_verbose

    def terse(self):
        """
        Return True if TFC set for terse tag strings.

        Terse means there will be no indenting.
        """
        return self.mode == TFC.mode_terse

    def verbose(self):
        """
        Return True if TFC set for verbose printing.

        Normally, if an XML item has no data, nothing is printed, but with
        mode_verbose you will get an empty compact tag for blank elements.
        For a collection you will get a comment similar to this:
            <!-- collection of Author with 0 elements -->
        """
        return self.mode == TFC.mode_verbose

    def indent_by(self, incr):
        """
        Return a TFC instance that indents by incr levels.  The mode will
        be unchanged.

        Pass this to a function that takes a TFC to get a temporary indent.
        """
        return TFC(level=self.level + incr, tfc=self)

    def s_indent(self, extra_indent=0):
        """
        Return an indent string.

        Return a string of white space that indents correctly for the 
        current TFC settings.  If specified, extra_indent will be added
        to the current indent level.
        """
        if self.mode == TFC.mode_terse:
            return ""
        level = self.level + extra_indent

        try:
            return lst_indent[level]
        except IndexError:
            return s_indent * level

    def attr_join(self, lst):
        if self.terse():
            sep = self.attr_sep
        else:
            # multiline attributes are treated much like tags: they are
            # put on multiple lines, indented.
            sep = self.tag_sep + self.s_indent(extra_indent=2)
        return sep.join(lst)

    def tag_join(self, lst):
        return self.tag_sep.join(lst)




# Here are all of the possible XML items.
#
# Supported by xe:
# XML Declaration: <?xml ... ?>
# Comments: <!-- ... -->
# Elements: <tag_name>...</tag_name>
#
# Minimal support:
# Markup Declarations: <!KEYWORD ... >
# Processing Instructions (PIs): <?KEYWORD ... ?>
# CDATA sections: <![CDATA[ ... ]]>
#
# Not currently supported:
# INCLUDE and IGNORE directives: <!KEYWORD[ ... ]]>


class XMLItem(object):
    """
    Abstract base class for all xe classes that represent XML.

    All xe classes that work with XML data inherit from this
    class.  All it does is provide a few default methods, and be a root
    for the inheritance tree.

    An XMLItem has several methods that return an XML tag representation
    of its contents.  Each XMLItem knows how to make an XML string
    representation of itself (its "tag string").  An XMLItem that
    contains other XMLItems will ask each one to make a tag string; so
    asking the top-level XMLItem for a tag string will cause the entire
    tree of XMLItems to recursively make tag strings, and you get a full
    XML representation with tags appropriately nested and indented.
    """
    def _tag_not_visible(self, tfc):
        if tfc.show_all():
            return False
        return not self

    def _s_tag(self, tfc):
        """
        A stub which must always be overridden by child classes.
        """
        assert False, "XMLItem is an abstract class with no tag strings."

    def s_tag(self, level=0):
        """
        Return a tag string.

        The XML tag string will be indented.

        If the item is empty, and it's not a top-level item (level is
        not 0), an empty string ("") will be returned.  If it is a
        top-level item, an empty compact tag string will be returned,
        like this:  <tagname/>
        """
        tfc = TFC(level, TFC.mode_normal)
        return self._s_tag(tfc)

    def s_tag_verbose(self, level=0):
        """
        Return a tag string showing all possible information.

        The XML tag will be indented.  All empty elements will have
        empty compact tag strings like this:  <tagname/>

        Empty Collection elements will have an XML Comment describing
        the collection.
        """
        tfc = TFC(level, TFC.mode_verbose)
        return self._s_tag(tfc)

    def s_tag_terse(self, level=0):
        """
        Return a minimal tag string without indentation.

        If the item is empty, and it's not a top-level item (level is
        not 0), an empty string ("") will be returned.  If it is a
        top-level item, an empty compact tag string will be returned,
        like this:  <tagname/>
        """
        tfc = TFC(level, TFC.mode_terse)
        return self._s_tag(tfc)

    def __str__(self):
        return self.s_tag()

    def level(self):
        """
        Return an integer describing what level this tag is.

        The root tag of an XML document is level 0; document-level comments
        or other document-level declarations are also level 0.  Tags nested
        inside the root tag are level 1, tags nested inside those tags are
        level 2, and so on.

        This is currently only used by the debug_tree() functions.  When
        printing tags normally, the code that walks the tree keeps track of
        what level is current.
        """
        level = 0
        while self._parent != None:
            self = self._parent
            if isinstance(self, ElementItem):
                level += 1
        return level

    def s_name(self):
        """
        Return a name for the current item.

        Used only by the debug_tree() functions.
        """
        if self._name:
            return self._name
        return "unnamed_instance_of_" + type(self).__name__

    def debug_tree(self):
        """
        Return a verbose tree showing the current tag and its children.

        This is for debugging; it's not valid XML syntax.
        """
        level = self.level()
        return "%2d) %s -- %s" % (level, self.s_name(), str(self))

    def import_xml(self, source, lst_errors):
        """
        Import XML data from source; log errors to lst_errors.

        Get as much data as possible; any data that is not imported will
        be appended to lst_errors, in text form.
        """
        assert False, "need to overload this to actually work"



class DocItem(XMLItem):
    """
    Abstract class: any XMLItem that can be document-level.

    An XML document has a "root element", with all the XML elements
    nested inside it; but there are some items that can appear outside
    the root element, such as comments and processing instructions.  All
    such items inherit from this class.
    """
    pass



class ElementItem(XMLItem):
    """
    Abstract class: any XMLItem that can be a common element.

    Basically, any XMLItem that can be inside the root element (or
    can BE the root element) will inherit from this class.
    """
    pass



class Comment(DocItem,ElementItem):
    """
    An XML comment.

    Attributes:
        text -- the text of the comment
    """
    def __init__(self, text=""):
        """
        text -- the text of the comment
        """
        self._parent = None
        self._name = ""
        self._direct_types = []
        self.tag_name = "comment"
        self.text = text

    def _s_tag(self, tfc):
        if self._tag_not_visible(tfc):
            return ""

        if self.text == "":
            return tfc.s_indent() + "<!-- -->"

        if self.text.find("\n") >= 0:
            lst = []
            lst.append(tfc.s_indent() + "<!--")
            lst.append(self.text)
            lst.append(tfc.s_indent() + "-->")
            return tfc.tag_join(lst)

        s = "%s%s%s%s" % (tfc.s_indent(), "<!-- ", self.text, " -->")
        return s

    def __nonzero__(self):
        # Returns True if there is any comment text.
        # Returns False otherwise.
        return not not self.text

    def text_check(self):
        pass



class PI(DocItem,ElementItem):
    """
    XML Processing Instruction (PI).

    Attributes:
        keyword
        text
    """
    def __init__(self, keyword, text=""):
        self._parent = None
        self._name = ""
        self._direct_types = []
        self.keyword = keyword
        self.text = ""

    def _s_tag(self, tfc):
        if self._tag_not_visible(tfc):
            return ""

        if self.text.find("\n") >= 0:
            lst = []
            lst.append("%s%s%s" % (tfc.s_indent(), "<?", self.keyword))
            lst.append(self.text)
            lst.append("%s%s" % (tfc.s_indent(), "?>"))
            return tfc.tag_join(lst)

        s = "%s%s%s %s%s"% \
                (tfc.s_indent(), "<?", self.keyword, self.text, "?>")
        return s

    def __nonzero__(self):
        # Returns True if there is any keyword.
        # Returns False otherwise.
        return not not self.keyword
    def text_check(self):
        pass



class MarkupDecl(DocItem):
    """
    XML Markup Declaration.

    Used for <!ENTITY ...>, <!ATTLIST ...>, etc. declarations.

    Attributes:
        keyword
        text
    """
    def __init__(self):
        self._parent = None
        self._name = ""
        self.keyword = ""
        self.text = ""

    def _s_tag(self, tfc):
        if self._tag_not_visible(tfc):
            return ""

        # REVIEW: can I factor out a common _s_tag()?
        if self.text.find("\n") >= 0:
            lst = []
            lst.append("%s%s%s" % (tfc.s_indent(), "<!", self.keyword))
            lst.append(self.text)
            lst.append("%s%s" % (tfc.s_indent(), ">"))
            return tfc.tag_join(lst)

        s = "%s%s%s %s%s" % \
                (tfc.s_indent(), "<!", self.keyword, self.text, ">")
        return s

    def __nonzero__(self):
        # Returns True if there is any keyword.
        # Returns False otherwise.
        return not not self.keyword
    def text_check(self):
        pass



class CDATA(DocItem):
    """
    CDATA declaration.

    Attributes:
        text
    """
    def __init__(self):
        self._parent = None
        self._name = ""
        self.keyword = ""
        self.text = ""

    def _s_tag(self, tfc):
        if self._tag_not_visible(tfc):
            return ""

        s = "%s%s%s%s" % (tfc.s_indent(), "<![CDATA[", self.text, "]]>")
        return s

    def __nonzero__(self):
        # Returns True if there is any keyword.
        # Returns False otherwise.
        return not not self.keyword
    def text_check(self):
        pass



def _assign_compatible(o, value):
    """
    Return True if value is type compatible for assigning to object o.

    value is compatible with object o when:
        * both o and value have the exact same type
        * o is set to None
        * both o and value are string types
    """
    t_o = type(o)
    t_val = type(value)

    return t_o is t_val or \
            t_o is types.NoneType or \
            t_o in types.StringTypes and t_val in types.StringTypes

class Node(ElementItem):
    """
    Abstract base class describing things common to nodes.

    XMLText and all of the XML element classes inherit from this.
    """
    def __init__(self):
        self._lock = False
        self._parent = None
        self._name = ""
        self._direct_types = []
        self._lock = True

    def __delattr__(self, name):
        raise TypeError, "cannot delete elements"

    def __getattr__(self, name):
        if name == "_lock":
            # If the "_lock" hasn't been created yet, we always want it
            # to be False, i.e. we are not locked.
            return False
        else:
            raise AttributeError, name

    def __setattr__(self, name, value):
        # Here's how this works:
        #
        # 0) "self._lock" is a boolean, set to False during __init__()
        # but turned True afterwards.  When it's False, you can add new
        # members to the class instance without any sort of checks; once
        # it's set True, __setattr__() starts checking assignments.
        # By default, when _lock is True, you cannot add a new member to
        # the class instance, and any assignment to an old member has to
        # be of matching type.  So if you say "a.text = string", the
        # .text member has to exist and be a string member.
        #
        # This is the default __setattr__() for all element types.  It
        # gets overloaded by the __setattr__() in NestElement, because
        # for nested elments, it makes sense to be able to add new
        # elements nested inside.
        #
        # This is moderately nice.  But later in class Nest there is a
        # version of __setattr__() that is *very* nice; check it out.
        #
        # 1) This checks assignments to _parent, and makes sure they are
        # plausible (either an XMLItem, or None).

        try:
            _lock = self._lock
        except AttributeError:
            _lock = False

        if not _lock:
            self.__dict__[name] = value
            return

        if not name in self.__dict__:
            # brand-new item
            if _lock:
                raise TypeError, "element cannot nest other elements"

        if name == "_parent":
            if not (isinstance(value, XMLItem) or value is None):
                raise TypeError, "only XMLItem or None is permitted"
            self.__dict__[name] = value
            return

        # locked item so do checks
        if not _assign_compatible(self.__dict__[name], value):
            raise TypeError, \
                    "value's type is not compatible:" + str(type(value))

        self.__dict__[name] = value
        

    def has_contents(self):
        """
        Return True if the contents are not empty.

        Note that the contents could be empty but the attributes might
        not be; an element is only empty if both attributs and contents
        are empty.
        """
        assert False, "Node is an abstract class; it has no contents."

    def multiline_contents(self):
        """
        Return True if the contents do not all fit on one line.
        """
        assert False, "Node is an abstract class; it has no contents."

    def s_contents(self, tfc):
        """
        Return a string with any contents of the element.

        For simple contents, just return the contents.
        If the contents are nested tags, they should be correctly
        indented, so this needs to take a TFC to control the indenting.
        """
        assert False, "Node is an abstract class; it has no contents."

    def direct(self, value):
        """
        Handle direct assign of a value to the element's contents.

        Some elements can handle a direct assign.  Those elements need
        to overload this method and make it do the right thing.
        
        For example, you might be able to assign a time float value to a
        timestamp element.  In that case, the timestamp element needs to
        add types.FloatType to its direct_types list, and add a
        .direct() method that overloads this default one to be able to
        correctly handle a float value.
        """
        assert False, "cannot call Node.direct(); must subclass it"



class XMLText(Node):
    """
    Class to represent simple, bare text in an XML document.

    This is NOT an XML element.  It has no tag name or attributes.

    If you want to try working with unstructured XML data, I suggest you
    create a Collection() of XMLItem() so you can tuck in all the
    XMLText items and XML elements you encounter, without needing to
    invent names for each one.
    """
    def __init__(self, text=""):
        Node.__init__(self)
        self._lock = False
        self.text = text
        self._lock = True

    def __nonzero__(self):
        """
        Return True if there are any contents.

        Return False otherwise.
        """
        return self.text != ""

    def text_check(self):
        pass

    def has_contents(self):
        """
        Return True if the contents are not empty.

        Return False otherwise.
        """
        return self.text != ""

    def multiline_contents(self):
        """
        Return True if the contents do not all fit on one line.
        """
        return self.text.find("\n") >= 0

    def s_contents(self, tfc):
        """
        Return a string with any contents.
        """
        return self.text

    def _s_tag(self, tfc):
        if self.text == "":
            return ""
        return tfc.s_indent() + self.text

    def __str__(self):
        return self.text



# string constants
_s_text = "text"
_s_value = "value"
_s_tf = "tf"
_s_time_offset = "time_offset"



class Attrs(object):
    """
    Class to manage a dictionary of attribute values.

    Remembers in what order the attributes were assigned; when creating
    a string representation of the attributes, they will always appear
    in the same order.
    """
    def __init__(self):
        self._attrs_names = []
        self._attrs_dict = {}

    def __cmp__(self, o):
        return cmp(self._attrs_dict, o._attrs_dict)

    def __getitem__(self, k):
        return self._attrs_dict[k]

    def __setitem__(self, k, value):
        if k not in self._attrs_dict:
            # first time assigned; also update _attrs_names
            self._attrs_names.append(k)
        self._attrs_dict[k] = value

    def __delitem__(self, k):
        self._attrs_names.remove(k)
        del(self._attrs_dict[k])

    def __nonzero__(self):
        for value in self._attrs_dict.values():
            if str(value):
                return True
        return False

    def lst_attrs(self):
        lst = []
        for name in self._attrs_names:
            s_value = str(self._attrs_dict[name])
            if s_value:
                s = '%s="%s"' % (name, s_value)
                lst.append(s)
        return lst

    def print_attrs(self):
        print "Attributes:"
        print "    " + "\n    ".join(self.lst_attrs())

    def set_names(self, attr_names):
        for name in attr_names:
            if name not in self._attrs_dict:
                self.__setitem__(name, "")



class CoreElement(Node):
    """
    Abstract base class describing things common to all XML elements.

    All of the XML element classes inherit from this.
    """
    def __init__(self, tag_name, def_attr_name=None, def_attr_value=None,
            attr_names=[], direct_types=[]):
        """
        Arguments:
            tag_name -- the XML tag name of this item
            def_attr_name -- name of any default attribute this item has
            def_attr_value -- default value of any default attribute
            attr_names -- a list of expected attribute names
            direct_types -- a list of types that can be direct assigned

            attr_names also sets the order in which the attribute names
            will be put in the tag string.

            See the doc string for direct() to learn about direct_types
            and direct assigns.
        """
        Node.__init__(self)
        self._lock = False
        # dictionary of attributes and their values
        self.tag_name = tag_name
        self.attrs = Attrs()
        if def_attr_name:
            self.attrs[def_attr_name] = def_attr_value
        self.attrs.set_names(attr_names)
        self._direct_types = direct_types
        self._lock = True

    def __nonzero__(self):
        """
        Return True if any attrs are set or there are any contents.

        Return False otherwise.
        """
        return self.attrs.__nonzero__() or self.has_contents()

    def has_contents(self):
        """
        Return True if the contents are not empty.

        Note that the contents could be empty but the attributes might
        not be; an element is only empty if both attributs and contents
        are empty.
        """
        assert False, "CoreElement is an abstract class; it has no contents."

    def multiline_contents(self):
        """
        Return True if the contents do not all fit on one line.
        """
        assert False, "CoreElement is an abstract class; it has no contents."

    def s_contents(self, tfc):
        """
        Return a string with any contents of the element.

        For simple contents, just return the contents.
        If the contents are nested tags, they should be correctly
        indented, so this needs to take a TFC to control the indenting.
        """
        assert False, "CoreElement is an abstract class; it has no contents."

    def _s_start_tag_name_attrs(self, tfc):
        """
        Return a string with the start tag name, and any attributes.

        Wrap this in correct angle brackets to get a start tag, or a
        compact tag.
        """
        lst_attrs = self.attrs.lst_attrs()
        if len(lst_attrs) == 0:
            return self.tag_name

        if len(lst_attrs) == 1:
            # just one attr so do on one line
            return "%s %s" % (self.tag_name, lst_attrs[0])

        # more than one attr so do a nice nested tag
        assert len(lst_attrs) > 1

        lst = [self.tag_name] + lst_attrs

        return tfc.attr_join(lst)

    def _s_tag(self, tfc):
        if self._tag_not_visible(tfc):
            return ""

        lst = []
        si = tfc.s_indent()

        lst.append(si + "<" + self._s_start_tag_name_attrs(tfc))

        if not self.has_contents():
            lst.append("/>")
        else:
            if self.multiline_contents():
                lst_contents = [">", self.s_contents(tfc.indent_by(1)), si]
                s = tfc.tag_join(lst_contents)
                lst.append(s)
            else:
                lst.append(">")
                lst.append(self.s_contents(tfc))
            lst.append("</" + self.tag_name + ">")

        return "".join(lst)

    def s_start_tag(self, tfc):
        return tfc.s_indent() + "<" + self._s_start_tag_name_attrs(tfc) + ">"

    def s_end_tag(self):
        return "</" + self.tag_name + ">"

    def s_compact_tag(self, tfc):
        return tfc.s_indent() + "<" + self._s_start_tag_name_attrs(tfc) + "/>"

    def direct(self, value):
        """
        Handle direct assign of a value to the element's contents.

        Some elements can handle a direct assign.  Those elements need
        to overload this method and make it do the right thing.
        
        For example, you might be able to assign a time float value to a
        timestamp element.  In that case, the timestamp element needs to
        add types.FloatType to its direct_types list, and add a
        .direct() method that overloads this default one to be able to
        correctly handle a float value.
        """
        assert False, "cannot call CoreElement.direct(); must subclass it"

    def import_xml(self, source, lst_errors=None):
        """
        Import XML data from source; log errors to lst_errors.

        "source" can be a filename, a URL, a string, or an xml.dom node
        data structure (as returned by xml.dom.minidom.parse()).

        Get as much data as possible; any data that is not imported will
        be appended to lst_errors, in text form.

        lst_errors is optional.
        """
        return _xe_import_xml(self, source, lst_errors)



class TextElement(CoreElement):
    """
    An element with simple text data.

    Cannot have other elements nested inside it.

    Attributes:
        attrs
        text
    """
    def __init__(self, tag_name, text="",
            def_attr_name=None, def_attr_value=None, attr_names=[]):
        CoreElement.__init__(self, tag_name,
                def_attr_name, def_attr_value, attr_names)
        self._lock = False
        self.text = text
        self._lock = True

    def text_check(self):
        pass

    def has_contents(self):
        return not not self.text

    def multiline_contents(self):
        return self.text.find("\n") >= 0

    def s_contents(self, tfc):
        return self.text



class CustomTimestampElement(CoreElement):
    def __init__(self, tag_name, tf, time_offset, s_offset_default,
            s_from_tf, tf_from_s, cleanup_time_offset):
        lst = [types.FloatType, types.NoneType] + list(types.StringTypes)
        CoreElement.__init__(self, tag_name, direct_types=lst)
        self._lock = False

        self.s_from_tf = s_from_tf
        self.tf_from_s = tf_from_s
        self.cleanup_time_offset = cleanup_time_offset

        self.s_offset_default = s_offset_default

        self.tf = None
        if time_offset is None:
            self.time_offset = s_offset_default
        else:
            self.time_offset = cleanup_time_offset(time_offset)

        self._lock = True
        self.direct(tf)

    def check_tf(self, tf):
        try:
            tf = float(tf)
        except (TypeError, ValueError):
            raise TypeError, "invalid time float value"
        return tf

    def __getattr__(self, name):
        if name == _s_text:
            return self.s_from_tf(self.tf, self.time_offset)
        return CoreElement.__getattr__(self, name)

    def __setattr__(self, name, value):
        if name == _s_text:
            if type(value) not in types.StringTypes:
                raise TypeError, "can only assign a string to .text"
            tf = self.tf_from_s(value)
            if tf is None:
                raise ValueError, "value must be a valid timestamp string"
            self.__dict__[_s_tf] = tf
            return

        if name == _s_tf:
            if value is None:
                self.__dict__[name] = None
            else:
                self.__dict__[name] = self.check_tf(value)
            return

        if name == _s_time_offset:
            if value is None:
                self.__dict__[name] = None
            else:
                try:
                    value = self.cleanup_time_offset(value)
                except (TypeError, ValueError):
                    raise ValueError, \
                            "value must be a valid time offset string"
                self.__dict__[name] = value
            return

        CoreElement.__setattr__(self, name, value)

    def __nonzero__(self):
        return self.tf is not None

    def __cmp__(self, o):
        try:
            n = cmp(self.tf, o.tf)
        except AttributeError:
            return cmp(self.tf, o)

        if n:
            return n
        # cmp() == zero, so values match; compare attrs to break the tie.
        # If values and attrs match, self and o should be considered equal.
        return cmp(self.attrs, o.attrs)

    def has_contents(self):
        return self.tf is not None

    def multiline_contents(self):
        return False

    def s_contents(self, tfc):
        if self.tf is None:
            return ""
        return self.s_from_tf(self.tf, self.time_offset)

    def direct(self, value):
        """
        Handle direct assignment.

        Supported types for direct assignment: float, string
        """
        assert self._direct_types == \
                [types.FloatType, types.NoneType] + list(types.StringTypes)
        assert type(value) in self._direct_types

        if value is None:
            self.tf = value
        elif type(value) == types.FloatType:
            self.tf = value
        elif type(value) in types.StringTypes:
            tf = self.tf_from_s(value)
            if tf is None:
                raise ValueError, "value must be a valid timestamp string"
            self.tf = tf
        else:
            # direct should never even be called unless the type is
            # compatible so this error should never happen
            raise TypeError, "cannot direct assign that type"

    def update(self):
        from time import time as tf_utc

        self.tf = tf_utc()
        return self

try:
    import feed.date.rfc3339 as rfc3339

    class TimestampElement(CustomTimestampElement):
        def __init__(self, tag_name, tf=None, time_offset=None):
            CustomTimestampElement.__init__(self,
                    tag_name,
                    tf,
                    time_offset,
                    rfc3339.s_offset_default,
                    rfc3339.timestamp_from_tf,
                    rfc3339.tf_from_timestamp,
                    rfc3339.cleanup_time_offset)
except ImportError:
    pass




class CustomElement(CoreElement):
    """
    Class to represent arbitrary data structures as xe elements.

    Make a class that inherits from CustomElement.  This class should
    then define four class methods:
      __init__() -- call CustomElement.__init__(), then do any custom
              setup
      check_value() -- return value; raise ValueError or TypeError if
              there is a problem with the value
      value_from_s() -- convert a string to the custom value; raise
              ValueError if there is any problem
      s_from_value() -- convert self.value to a string

    These three functions should be class methods so they can inspect
    the self values.  See the IntElement class for a simple example of a
    class implemented with CustomElement.

    """
    # If you need to provide multiple values to your conversion
    # functions, make the conversion functions part of your subclass
    # and have them get those values through self.
    def __init__(self, tag_name, value, cust_type):
        lst = [cust_type, types.NoneType] + list(types.StringTypes)
        CoreElement.__init__(self, tag_name, direct_types=lst)
        self._lock = False
        self.cust_type = cust_type
        # get .value added to dict in case .direct() needs it
        self.value = None
        self._lock = True

        # use .direct() so that init can be done with value or string
        self.direct(value)

    def __getattr__(self, name):
        if name == _s_text:
            return self.s_from_value()
        return CoreElement.__getattr__(self, name)

    def __setattr__(self, name, value):
        if name == _s_text:
            if type(value) not in types.StringTypes:
                raise TypeError, "can only assign a string to .text"
            self.value = self.value_from_s(value)
            return

        if name == _s_value:
            if value is None:
                self.__dict__[name] = None
            else:
                self.__dict__[name] = self.check_value(value)
            return

        CoreElement.__setattr__(self, name, value)

    def __nonzero__(self):
        return self.value is not None

    def __cmp__(self, o):
        try:
            n = cmp(self.value, o.value)
        except AttributeError:
            return cmp(self.value, o)

        if n:
            return n
        # cmp() == zero, so values match; compare attrs to break the tie.
        # If values and attrs match, self and o should be considered equal.
        return cmp(self.attrs, o.attrs)

    def has_contents(self):
        return self.value is not None

    def multiline_contents(self):
        # overload this for any type that can be have multiline contents
        return False

    def s_contents(self, tfc):
        return self.s_from_value()

    def direct(self, value):
        """
        Handle direct assignment.

        Supported types for direct assignment are in self._direct_types
        """
        assert self._direct_types == \
                [self.cust_type, types.NoneType] + list(types.StringTypes)
        assert type(value) in self._direct_types

        if value is None:
            self.value = None
        elif type(value) in types.StringTypes:
            self.value = self.value_from_s(value)
        else:
            self.value = self.check_value(value)



class IntElement(CustomElement):
    def __init__(self, tag_name, value=None, min=None, max=None):
        # define min and max first because check_value() needs them
        self._lock = False
        self.min = min
        self.max = max
        self._lock = True
        # now it's safe to init the value (and everything else too)
        CustomElement.__init__(self, tag_name, value, types.IntType)

    def check_value(self, value):
        assert self.cust_type is types.IntType
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError, "value must be an integer type"

        if self.min is not None and value < self.min:
            raise ValueError, "minimum value is %d" % self.min
        if self.max is not None and value > self.max:
            raise ValueError, "maximum value is %d" % self.max

        return value

    def value_from_s(self, s):
        assert type(s) in types.StringTypes

        value = int(s)
        return self.check_value(value)

    def s_from_value(self):
        if self.value is None:
            return ""
        return str(self.value)



class FloatElement(CustomElement):
    def __init__(self, tag_name, value=None, min=None, max=None,
            s_format=None):
        CustomElement.__init__(self, tag_name, value, types.FloatType)
        self._lock = False
        self.min = min
        self.max = max
        self.s_format = s_format
        self._lock = True

    def check_value(self, value):
        assert self.cust_type is types.FloatType
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise TypeError, "value must be a float type"

        if self.min is not None and value < self.min:
            raise ValueError, "minimum value is %d" % self.min
        if self.max is not None and value > self.max:
            raise ValueError, "maximum value is %d" % self.max

        return value

    def value_from_s(self, s):
        assert type(s) in types.StringTypes

        value = float(s)
        return self.check_value(value)

    def s_from_value(self):
        if self.value is None:
            return ""
        if self.s_format is None:
            return str(self.value)
        return self.s_format % self.value



class Nest(XMLItem):
    """
    A data structure that can store XML elements, nested inside it.

    Note: this is not an XML element!  Because it is not an XML
    element, it has no tags.  Its string representation is the
    representations of the elements nested inside it.

    NestElement and XMLDoc inherit from this.
    """
    def __init__(self):
        self._lock = False
        self._parent = None
        self._name = ""
        self._element_names = []
        self._lock = True

    def _do_setattr(self, name, value):
        if isinstance(value, XMLItem):
            value._parent = self
            value._name = name
            if name not in self.__dict__:
                # item being added for the first time ever
                self._element_names.append(name)
        self.__dict__[name] = value

    def __setattr__(self, name, value):
        # Lots of magic here!  This is important stuff.  Here's how it works:
        #
        # 0) self._lock is a boolean, set to False initially and then set
        # to True at the end of __init__().  When it's False, you can add new
        # members to the class instance without any sort of checks; once
        # it's set True, __setattr__() starts checking assignments.  By
        # default, when _lock is True, any assignment to an old member
        # has to be of matching type.  You can add a new member to the
        # class instance, but __setattr__() checks to ensure that the
        # new member is an XMLItem.
        #
        # 1) Whether self._lock is set or not, if the value is an XMLitem,
        # then this will properly add the XMLItem into the tree
        # structure.  The XMLItem will have _parent set to the parent,
        # will have _name set to its name in the parent, and will be
        # added to the parent's elements list.  This is handled by
        # _do_setattr().
        #
        # 2) As a convenience for the user, if the user is assigning a
        # string, and self is an XMLItem that has a .text value, this
        # will assign the string to the .text value.  This allows usages
        # like "e.title = string", which is very nice.  Before I added
        # this, I frequently wrote "e.title = string" and was frustrated
        # when my title element was replaced by a simple string; it's
        # better if this can just work.
        #
        # 3) Similar to the above, an element can advertise that it will
        # accept certain types directly.  If you are assigning "value"
        # to a subobject o, then if type(value) is in the o._direct_types
        # list, this will call o.direct(value) to do the direct
        # assignment.  Example: see the Timestamp elements in atomfeed.
        #
        # 4) This checks assignments to _parent, and makes sure they are
        # plausible (either an XMLItem, or None).

        try:
            _lock = self._lock
        except AttributeError:
            _lock = False

        if not _lock:
            self._do_setattr(name, value)
            return

        if not name in self.__dict__:
            # brand-new item
            if _lock:
                self.nest_check()
                if not isinstance(value, XMLItem):
                    # Often, this error is because of a typo.  The user
                    # didn't mean to insert a new item, but misspelled
                    # an existing item.
                    raise TypeError, \
                    "cannot insert non-XMLItem (did you misspell something?)"
            self._do_setattr(name, value)
            return

        if name == "_parent":
            if not (isinstance(value, XMLItem) or value is None):
                raise TypeError, "only XMLItem or None is permitted"
            self.__dict__[name] = value
            return

        if name == "_name" and type(value) in types.StringTypes:
            self.__dict__[name] = value
            return

        o = self.__dict__[name]

        # direct-assign the value if that is supported
        if isinstance(o, ElementItem) and type(value) in o._direct_types:
            o.direct(value)
            return

        # Allow string assignment to go to the .text attribute, for
        # elements that allow it.  All TextElements allow it;
        # Elements will allow it if they do not nave nested elements.
        # text_check() raises an error if it's not allowed.
        if isinstance(o, ElementItem) and \
                _s_text in o.__dict__ and \
                type(value) in types.StringTypes:
            o.text_check()
            o.text = value
            return

        # locked item so do checks
        if not _assign_compatible(o, value):
            raise TypeError, "value's type is not compatible"

        self._do_setattr(name, value)
        
    def __delattr__(self, name):
        # This won't be used often, if ever, but if anyone tries it, it
        # should work.  Can only delete nested ElementItems.
        if not isinstance(self.name, ElementItem):
            raise TypeError, "cannot delete %s" % name
        self._element_names.remove(name)
        del(self.__dict__[name])

    def nest_check(self):
        pass

    def has_contents(self):
        for name in self._element_names:
            if self.__dict__[name]:
                return True
        # empty iff all of the elements were empty
        return False

    def __nonzero__(self):
        return self.has_contents()

    def multiline_contents(self):
        # for any contents, we want multiline so nested tags are indented
        return self.has_contents()

    def s_contents(self, tfc):
        if len(self._element_names) == 0:
            return ""

        lst = []
        for name in self._element_names:
            element = self.__dict__[name]
            s = element._s_tag(tfc)
            if s:
                lst.append(s)

        return tfc.tag_join(lst)

    def debug_tree(self):
        lst = []
        level = self.level()
        num_elem = len(self._element_names)
        tup = (level, self.s_name(), self.__class__.__name__, num_elem)
        s = "%2d) %s -- %s containing %d elements" % tup
        lst.append(s)
        for name in self._element_names:
            element = self.__dict__[name]
            s = element.debug_tree()
            lst.append(s)
        return tfc.tag_join(lst)

    def _s_tag(self, tfc):
        return self.s_contents(tfc)




class NestElement(Nest,CoreElement):
    """
    An element that can have other elements nested inside it.

    Attributes:
        attrs -- a dictionary mapping XML attribute names to values
        _element_names -- a list of other elements nested inside
    """
    def __init__(self, tag_name, def_attr_name=None, def_attr_value=None,
            attr_names=[], direct_types=[]):
        """
        Arguments:
            tag_name -- the XML tag name of this item
            def_attr_name -- name of any default attribute this item has
            def_attr_value -- default value of any default attribute
            attr_names -- a list of expected attribute names
            direct_types -- a list of types that can be direct assigned

            attr_names also sets the order in which the attribute names
            will be put in the tag string.

            See the doc string for CoreElement.direct() to learn about
            direct_types and direct assigns.
        """
        CoreElement.__init__(self, tag_name, def_attr_name, def_attr_value,
                attr_names, direct_types)
        self._lock = False
        self._element_names = []
        self._lock = True

    def __nonzero__(self):
        return CoreElement.__nonzero__(self)

    def _s_tag(self, tfc):
        return CoreElement._s_tag(self, tfc)



class Element(NestElement,TextElement):
    """
    A class to represent an arbitrary XML tag.  Can either have other XML
    elements nested inside it, or else can have a text string value, but
    never both at the same time.

    This is intended for user-defined XML tags.  The user can just use
    "Element" for all custom tags.

    This isn't essential.  You can use TextElement for tags with a text
    string value, and NestElement for tags that nest other elements.
    This is here for convenience; you can just use Element for
    everything if you like.

    Attributes:
        attrs -- a dictionary mapping XML attribute names to values
        _element_names -- a list of other elements nested inside, if any
        text -- a text string value, if any

    Note: if text is set, elements will be empty, and vice-versa.  If you
    have elements nested inside and try to set the .text, this will raise
    an exception, and vice-versa.
    """
    def __init__(self, tag_name, def_attr_name=None, def_attr_value=None,
            attr_names=[], direct_types=[]):
        """
        Arguments:
            tag_name -- the XML tag name of this item
            def_attr_name -- name of any default attribute this item has
            def_attr_value -- default value of any default attribute
            attr_names -- a list of expected attribute names
            direct_types -- a list of types that can be direct assigned

            attr_names also sets the order in which the attribute names
            will be put in the tag string.

            See the doc string for CoreElement.direct() to learn about
            direct_types and direct assigns.
        """
        NestElement.__init__(self, tag_name, def_attr_name, def_attr_value,
                attr_names, direct_types)
        self._lock = False
        self.text = ""
        self._lock = True

    def nest_check(self):
        if self.text:
            raise TypeError, "Element has text contents so cannot nest"

    def text_check(self):
        if len(self._element_names) > 0:
            raise TypeError, "Element has nested elements so cannot assign text"

    def has_contents(self):
        return NestElement.has_contents(self) or TextElement.has_contents(self)

    def multiline_contents(self):
        return NestElement.has_contents(self) or self.text.find("\n") >= 0

    def s_contents(self, tfc):
        if len(self._element_names) > 0:
            return NestElement.s_contents(self, tfc)
        if self.text:
            return TextElement.s_contents(self, tfc)
        return ""

    def debug_tree(self):
        lst = []
        num_elem = len(self._element_names)
        level = self.level()
        if self.text:
            return XMLItem.debug_tree(self)
        elif num_elem > 0:
            tup = (self.s_name(), self.__class__.__name__, num_elem, level)
            s = "# %s -- instance of %s containing %d elements (current level: %d)" % tup
            lst.append(s)
            for name in self._element_names:
                element = self.__dict__[name]
                s = element.debug_tree()
                lst.append(s)
            return tfc.tag_join(lst)
        else:
            tup = (self.s_name(), level)
            s = "%s -- empty Element (current level: %d)" % tup
            return s
        assert(False, "not possible to reach this line.")



class Collection(XMLItem):
    """
    A container for 0 or more XML elements of a type.

    Note: this is not an XML element!  Because it is not an XML
    element, it has no tags.  Its string representation is the
    representations of the elements nested inside it.

    A Collection contains 0 or more Elements, but isn't an XML element.
    Use where a run of 0 or more Elements of the same type is legal.

    When you init your Collection, you specify what class of Element it
    will contain.  Attempts to append an Element of a different class
    will raise an exception.  Note, however, that the various Element
    classes all inherit from base classes, and you can specify a class
    from higher up in the inheritance tree.  You could, if you wanted,
    make a Collection containing "XMLItem" and then any XML element
    class would be legal in that collection.  (Example: XMLDoc, which
    contains two collections of DocItem.)

    Attributes:
        contains -- the class of element this Collection will contain
        items -- a list of elements nested inside

    Note: The string representation of a Collection is just the string
    representations of the elements inside it.  However, a verbose
    string reprentation will have an XML comment like this:

    <!-- Collection of <class> with <n> elements -->

    where <n> is the number of elements in the Collection and <class> is
    the name of the class in this Collection.
    """
    class Flags(object):
        def __init__(self):
            self.unique_values = False
            self.sorted = False

    def __init__(self, element_class):
        """
        Arguments:
            element_class -- the class of XML elements to allow

            To allow any XML element, use "XMLItem" for element_class
        """
        self._lock = False
        self._parent = None
        self._name = ""
        self._flags = Collection.Flags()
        self.items = []
        self.contains = element_class
        self._lock = True
    def __len__(self):
        return len(self.items)
    def __getitem__(self, i):
        return self.items[i]
    def __setitem__(self, i, value):
        o = self.items[i]
        # direct-assign the value if that is supported
        if isinstance(o, ElementItem) and type(value) in o._direct_types:
            o.direct(value)
            return

        if not isinstance(value, self.contains):
            raise TypeError, "object is the wrong type for this collection"

        self.items[i] = value
    def __delitem__(self, i):
        del(self.items[i])

    def __nonzero__(self):
        # there are no attrs; collection is nonzero if any element is
        for element in self.items:
            if element:
                return True
        return False

    def s_coll(self):
        """
        Return a string describing the collection.

        The string will be something like:

        "collection of XMLItem with 2 elements."
        """
        name = self.contains.__name__
        n = len(self.items)
        if n == 1:
            el = "element"
        else:
            el = "elements"
        return "collection of %s with %d %s" % (name, n, el)

    def append(self, element):
        assert issubclass(self.contains, XMLItem)
        if not isinstance(element, self.contains):
            raise TypeError, "object is the wrong type for this collection"
        if self._flags.unique_values:
            for o in self.items:
                if element == o:
                    return
        element._parent = self
        self.items.append(element)
        if self._flags.sorted:
            self.items.sort()

    def insert(self, i, element):
        """
        Insert element before index i.

        """
        assert issubclass(self.contains, XMLItem)
        if not isinstance(element, self.contains):
            raise TypeError, "object is the wrong type for this collection"
        if self._flags.unique_values:
            for o in self.items:
                if element == o:
                    return
        element._parent = self
        self.items.insert(i, element)
        if self._flags.sorted:
            self.items.sort()

    def _s_tag(self, tfc):
        # A collection exists only as a place to put real elements.
        # There are no start or end tags...
        # When tfc.verbose() is true, we do put an XML comment
        # identifying the collection, and we indent the elements under
        # that comment, to better show the structure.

        if not self.items and not tfc.show_all():
            return ""

        lst = []

        if tfc.verbose():
            s = "%s%s%s%s" % (tfc.s_indent(), "<!-- ", self.s_coll(), " -->")
            lst.append(s)
            tfc = tfc.indent_by(1)

        for element in self.items:
            s = element._s_tag(tfc)
            if s:
                lst.append(s)

        return tfc.tag_join(lst)

    def debug_tree(self):
        level = self.level()
        s = "%2d) %s -- %s" % (level, self.s_name(), self.s_coll())
        lst = []
        lst.append(s)
        for element in self.items:
            s = element.debug_tree()
            lst.append(s)
        return tfc.tag_join(lst)



class ListElement(Collection, CoreElement):
    """
    A container for 0 or more XML elements of a type.

    Similar to a Collection, but this is an element.  It has attributes
    and its representation is an XML tag.

    When you init your ListElement, you specify what class of Element it
    will contain.  Attempts to append an Element of a different class
    will raise an exception.  Note, however, that the various Element
    classes all inherit from base classes, and you can specify a class
    from higher up in the inheritance tree.  You could, if you wanted,
    make a ListElement containing "ElementItem" and then any XML element
    would be allowed.  (For working with unstructured XML, you will
    probably want to do just that: use a ListElement of ElementItem.)

    Attributes:
        contains -- the class of element this ListElement will contain
        items -- a list of elements nested inside
    """
    def __init__(self, element_class, tag_name,
             def_attr_name=None, def_attr_value=None,
            attr_names=[], direct_types=[]):
        """
        Arguments:
            element_class -- the class of XML elements to allow

            To allow any XML element, use "XMLItem" for element_class
        """
        if not issubclass(element_class, XMLItem):
          raise TypeError, "element_class must be an XMLItem"

        if type(tag_name) not in types.StringTypes:
            raise TypeError, "tag_name must be a string"

        CoreElement.__init__(self, tag_name, def_attr_name, def_attr_value,
                attr_names, direct_types)
        Collection.__init__(self, element_class)
        self._flags.show_when_empty = False

#    # REVIEW: just inherit these from Collection?
#    def __len__(self):
#        return len(self.items)
#    def __getitem__(self, i):
#        return self.items[i]
#    def __setitem__(self, i, value):
#        o = self.items[i]
#        # direct-assign the value if that is supported
#        if isinstance(o, ElementItem) and type(value) in o._direct_types:
#            o.direct(value)
#            return
#
#        if not isinstance(value, self.contains):
#            raise TypeError, "object is the wrong type for this ListElement"
#
#        self.items[i] = value
#    def __delitem__(self, i):
#        del(self.items[i])

    def _tag_not_visible(self, tfc):
        if self._flags.show_when_empty:
            return False
        return CoreElement._tag_not_visible(self, tfc)

    def has_contents(self):
        return Collection.__nonzero__(self)

    def multiline_contents(self):
        # if we have any contents at all, they should be multiline
        return self.has_contents()

    def s_contents(self, tfc):
        return Collection._s_tag(self, tfc)

    def __nonzero__(self):
        return CoreElement.__nonzero__(self)

    def _s_tag(self, tfc):
        return CoreElement._s_tag(self, tfc)



class XMLDeclaration(DocItem):
    def __init__(self):
        self._parent = None
        self._name = ""
        self.attrs = Attrs()
        self.attrs["version"] = "1.0"
        self.attrs["encoding"] = "utf-8"
        self.attrs["standalone"] = ""

    def _s_tag(self, tfc):
        # An XMLDeclaration() instance is never empty, so always prints.

        lst_attrs = self.attrs.lst_attrs()
        s_attrs = " ".join(lst_attrs)

        s = "%s%s %s%s" % (tfc.s_indent(), "<?xml", s_attrs, "?>")

        return s

    def __nonzero__(self):
        # Returns True because the XML Declaration is never empty.
        return True



class XMLDoc(Nest):
    """
    A data structure to represent an XML Document.  It will have the
    following structure:

    the XML Declaration item
    0 or more document-level XML items
    exactly one XML item (the "root tag")
    0 or more document-level XML items

    document level XML items are: Comment, PI, MarkupDecl


    Attributes:
        xml_decl
            the XMLDeclaration item
        top
            a collection of DocItem at top (above root_element)
        root_element
            the XML tag containing your data
        end
            a collection of DocItem at end (below root_element)

    Note: usually the root_element has lots of ElementItems nested inside!
    """
    def __init__(self, root_element=None):
        """
        Arguments:
            root_element -- an ElementItem to hold all the data in the
                    XMLDoc.  Usually this will be a NestElement or
                    Element with lots of ElementItems inside.
        """
        Nest.__init__(self)

        self._name = "XMLDoc"

        self.xml_decl = XMLDeclaration()
        self.top = Collection(DocItem)

        if root_element is None:
            root_element = Comment("no root element yet")
        self.root_element = root_element

        self.end = Collection(DocItem)

    def __setattr__(self, name, value):
        # root_element may always be set to any ElementItem
        if name == "root_element":
            if not (isinstance(value, ElementItem)):
                raise TypeError, "only ElementItem is permitted"

            Nest._do_setattr(self, name, value)
        else:
            # for all other, fall through to inherited behavior
            Nest.__setattr__(self, name, value)

    def Validate(self):
        """
        Return True if XMLDoc is valid.

        Currently doesn't test very much.
        """
        # XMLDoc never has parent.  Never change this!
        assert self._parent == None
        return True


import xml.dom.minidom as mdom

def _xe_import_xml(x, source, lst_errors=None):
    """
    Import XML data from source; log errors to lst_errors.

    "source" can be a filename, a URL, a string, or an xml.dom node
    data structure (as returned by xml.dom.minidom.parse()).

    Get as much data as possible; any data that is not imported will
    be appended to lst_errors, in text form.

    Arguments:
        x -- an xe object
        source -- filename, URL, string, or xml.dom node data structure
        lst_errors -- a list to receive any errors

    If lst_errors is not specified or None, errors will not be logged.

    """

    # NOTES
    #
    # These functions take a "lst_errors" argument.  When they find an XML
    # node they cannot import, they will append the text form of the node
    # to the lst_errors list.  On a perfectly successful import,
    # lst_errors will not have anything added to it.
    #
    # The way this works:
    #
    # If you point the import code at XML data, it will use Python's
    # xml.dom.minidom module to read and parse the XML.  (If you need 
    # more control over the process, you can do this parsing by hand, and
    # pass the xml.dom.minidom node data structure to the import code.)
    # The import code walks the node data structure, and matches up tag
    # names with tag names inside your xe data structure.  If everything
    # matches nicely, it imports the node into the data structure.
    #
    # If it sees a tag name that your data structure doesn't know about,
    # and the node is a simple text element node, xe will simply add a new
    # TextElement to your xe data structure and fill in the information
    # from the node.
    #
    # Any XML nodes that the import code cannot handle will be converted
    # to XML text strings, and those strings will be appended to
    # lst_errors.
    #
    #
    # Key functions:
    #     import_node_element() -- smart node import function

    def log_error(node, lst_errors):
        if lst_errors is None:
            return
        s = node.toxml()
        lst_errors.append(s)

    def parse_info(x):
        if not isinstance(x, XMLItem):
            raise TypeError

        if isinstance(x, Collection):
            o = x.contains()
            if "tag_name" in o.__dict__:
                tup = (o.tag_name, x)
            else:
                # FUTURE: handle this case later someday
                # for now, we will only read in by specific tag names
                tup = ("*", x)
            return tup
        else:
            tup = (x.tag_name, x)
            return tup

    def import_attrs(x, node):
        if node.hasAttributes():
            for name, value in node.attributes.items():
                x.attrs[name] = value

    def make_py_name(tag_name):
        """
        Return legal Python identifier name translated from tag_name.

        Any character not legal for a Python identifier becomes an
        underscore character ("_").

        Example:
        >>> print make_py_name("foaf:name")
        foaf_name
        """
        lst = []
        for c in tag_name:
            if c.isalnum() or c == "_":
                lst.append(c)
            else:
                lst.append("_")
        if lst[0].isnumeric():
            # if first character is a number, prepend something.
            lst.insert("elem", 0)
        return "".join(lst)

    def import_node_nest(x, node, lst_errors):
        assert node.nodeType == mdom.Node.ELEMENT_NODE
        if not isinstance(x, Nest):
            print "tried to import node on non-Nest"
            print "x:", str(x)
            print "node:", node.toxml()
            raise TypeError, "attempt to nest in non-Nest:" + str(type(x))

        try:
            # if parse info dict was cached earlier, just use it
            d = x._lst_parse_info
        except AttributeError:
            # need to build the parse info dict
            lst_elements = [x.__dict__[name] for name in x._element_names]
            d = dict([parse_info(e) for e in lst_elements])

            # cache the parse info dict for possible later reuse
            x._lock = False
            x._lst_parse_info = d
            x._lock = True

        try:
            import_attrs(x, node)
        except:
            log_error(node, lst_errors)

        for n in node.childNodes:
            if n.nodeType != mdom.Node.ELEMENT_NODE:
                # if it's not an element, we don't handle it at all
                # FUTURE: handle non-element nodes
                if n.nodeType == mdom.Node.TEXT_NODE and \
                        n.nodeValue.lstrip() == "":
                    # if it's a text node with just some white space,
                    # just skip it; don't even log it
                    continue
                log_error(n, lst_errors)
            elif n.tagName in d:
                import_node_element(d[n.tagName], n, lst_errors)
            else:
                # Whatever it is, treat it as a text element and add it
                tag_name = n.tagName
                o = TextElement(tag_name)
                x.__setattr__(make_py_name(tag_name), o)
                import_node_element(o, n, lst_errors)

    def import_node_text(x, node, lst_errors):
        try:
            import_attrs(x, node)
            lst = []
            for child in node.childNodes:
                if child.nodeType == mdom.Node.TEXT_NODE:
                    lst.append(child.nodeValue)
                else:
                    lst.append(child.toxml())
            x.text = "".join(lst)
        except:
            log_error(node, lst_errors)

    def import_node_element(x, node, lst_errors=None):
        """
        Import data from xml.dom.minidom node; log errors to lst_errors.

        Get as much data as possible; any data that is not imported will
        be appended to lst_errors, in text form.

        Arguments:
            x -- an xe object
            node -- an xml.dom.minidom node object
            lst_errors -- a list to receive any errors

        If lst_errors is not specified or None, errors will not be logged.
        """
        assert node.nodeType == mdom.Node.ELEMENT_NODE

        if isinstance(x, Collection):
            o = x.contains()
            import_node_element(o, node, lst_errors)
            x.append(o)
            return

        if isinstance(x, Nest):
            import_node_nest(x, node, lst_errors)
        else:
            import_node_text(x, node, lst_errors)
        return x

    def mini_open_anything(source):
        """
        Return file-like object from source.

        Try source several ways, to see if it is:
            * a file-like object (e.g. an already-opened file)
            * a URL
            * a filename

        This is inspired by the wonderful openAnything() by Mark Pilgrim:
        http://diveintopython.org/http_web_services/
        """
        try:
            # check to see if source already has readlines and close
            # methods
            if callable(source.readlines) and callable(source.close):
                # okay, looks like a file-like object; return it
                return source
        except AttributeError:
            pass

        if type(source) not in types.StringTypes:
            raise TypeError, "source isn't even a string"

        import urllib
        try:
            # see if source works as a URL
            return urllib.urlopen(source)
        except (IOError, OSError):
            pass

        try:
            # see if source works as a filename
            return open(source)
        except (IOError, OSError):
            pass

        return None


    # The actual _xe_import_xml() function body is below!
    # def _xe_import_xml(x, source, lst_errors=None):

    if not isinstance(x, XMLItem):
        # not an xe element
        raise TypeError, "x must be an xe element with a tag_name"
    try:
        tag_name = x.tag_name
    except AttributeError:
        raise TypeError, "x must be an xe element with a tag_name"

    temp_doc = None
    if isinstance(source, mdom.Node):
        # source is already an xml.dom.minidom node structure
        lst_nodes = source.getElementsByTagName(tag_name)
    else:
        # Not a Node, so we need to parse source.
        try:
            f = mini_open_anything(source)
        except TypeError:
            raise TypeError, "source is the wrong type; cannot import it"

        if f is not None:
            # We don't catch the exception for parse(); if it fails,
            # we want the exception raised.
            temp_doc = mdom.parse(f)
            lst_nodes = temp_doc.getElementsByTagName(tag_name)
        else:
            # We couldn't open it.  Maybe it's a string of XML?
            # We don't catch the exception for parseString(); if it fails,
            # we want the exception raised.
            temp_doc = mdom.parseString(source)
            lst_nodes = temp_doc.getElementsByTagName(tag_name)

    if len(lst_nodes) != 1:
        temp_doc and temp_doc.unlink()
        raise ValueError, "source contains more than one element to load"

    node = lst_nodes[0]
    import_node_element(x, node, lst_errors)
    temp_doc and temp_doc.unlink()
    return x

def print_log(lst_errors):
    """
    Print lst_errors in a nice format.
    """
    if len(lst_errors) == 0:
        print "No errors!"
    else:
        print "Could not handle these lines of XML:"
        print "\t" + "\n\t".join(lst_errors)




if __name__ == "__main__":
    def diff(s0, s1):
        """
        Compare two strings, line by line; return a report on any differences.
        """
        from difflib import ndiff
        lst0 = s0.split("\n")
        lst1 = s1.split("\n")
        report = '\n'.join(ndiff(lst0, lst1))
        return report

    def self_test_diff(message):
        """
        Check to see if a test failed; if so, print a diff.

        message: string to print on test failure

        Implicit arguments:
            failed_tests -- count of failed tests; will be incremented
            correct -- the expected result of the test
            result -- the actual result of the test
        """
        global failed_tests

        if result != correct:
            failed_tests += 1
            print module_banner
            print "%s: test case failed, diff follows:" % message
            print diff(correct, result)
            print



    failed_tests = 0

    # Since this file is indented using spaces, let's indent our test
    # code using spaces too so it will compare right.
    set_indent_str("    ")


    # Test: generate a trivial XML document

    xmldoc = XMLDoc()
    correct = """\
<?xml version="1.0" encoding="utf-8"?>
<!-- no root element yet -->"""

    result = str(xmldoc)
    self_test_diff("generate trivial XML document")


    # Test: verify that xmldoc.Validate() succeeds

    try:
        b = xmldoc.Validate()
    except:
        b = False

    if not b:
        failed_tests += 1
        print "test case failed:"
        print "xmldoc.Validate() failed."
        print


    # Test: does Element work both nested an non-nested?
    correct = """\
<test>
    some text
    <test:agent number="007">James Bond</test:agent>
    <test:pet
            type="cat"
            nickname="Mei-Mei">Matrix</test:pet>
    some more text
    <secret_agent agency="U.N.C.L.E.">Napoleon Solo</secret_agent>
</test>"""

    class TestPet(Element):
        def __init__(self, name=""):
            Element.__init__(self, "test:pet")
            self.text = name

    class TestAgent(Element):
        def __init__(self, name=""):
            Element.__init__(self, "test:agent")
            self.text = name

    class Test(Element):
        def __init__(self):
            Element.__init__(self, "test")
            self.text0 = XMLText()
            self.test_agent = TestAgent()
            self.test_pet = TestPet()
            self.text1 = XMLText()

    test = Test()
    test.text0 = "some text"
    test.test_agent = "James Bond"
    test.test_agent.attrs["number"] = "007"
    test.test_pet = "Matrix"
    test.test_pet.attrs["type"] = "cat"
    test.test_pet.attrs["nickname"] = "Mei-Mei"
    test.text1 = "some more text"
    test.secret_agent = TextElement("secret_agent")
    test.secret_agent = "Napoleon Solo"
    test.secret_agent.attrs["agency"] = "U.N.C.L.E."

    result = str(test)
    self_test_diff("test Element with both text and nested")

    test1 = NestElement("paper_size")
    correct = """\
<paper_size>
    <width>8.5</width>
    <height>11</height>
</paper_size>"""
    test1.import_xml(correct)
    result = str(test1)
    self_test_diff("test Element import")


    from sys import exit
    s_module = module_name + " " + module_version
    if failed_tests == 0:
        print s_module + ": self-test: all tests succeeded!"
        exit(0)
    elif failed_tests == 1:
        print s_module + " self-test: 1 test failed."
        exit(1)
    else:
        print s_module + " self-test: %d tests failed." % failed_tests
        exit(1)
