#!/usr/bin/env python
#coding=utf-8
#? py

'''
settings.py
####################################

XML Based Settings Reader/Writer

.. Note:: You may not use < or > in Topic or Key.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''
import cgi
import os
import re
from htmlentitydefs import name2codepoint

from BeautifulSoup import BeautifulSoup, Tag, NavigableString


# Helping Function for Escaping XML/Html tags
# -------------------------------------------------------------------------------------
def unescape(s):
    "unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml"
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

# -------------------------------------------------------------------------------------
escape = cgi.escape    
    
# #############################################################################################
class XMLSettings(object):
    """Saves Settings in XML file"""
    # -------------------------------------------------------------------------------------
    # Attributes

    # Default Settings Header
    HEADER = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    HEADER_SETTINGS = """<{0}>
    </{0}>"""

    PAT_FORMAT = re.compile(r">\s*<") # White spaces
    PAT_FORMAT_2 = re.compile(r"<([a-z0-9]*)>\s*<(/\1)>") # New lines on elements

    # -------------------------------------------------------------------------------------
    def filepath():
        doc = "The filepath property to the path"
        def fget(self):
            return self._filepath
        def fset(self, value):
            self._filepath = value
        return locals()
    filepath = property(**filepath())

    # -------------------------------------------------------------------------------------
    def cache():
        doc = "Cache property - do not reload file on access if true"
        def fget(self):
            return self._cache
        def fset(self, value):
            self._cache = value
        return locals()
    cache = property(**cache())

    # -------------------------------------------------------------------------------------
    # Private
    # -------------------------------------------------------------------------------------
    def __init__(self, filepath, root=None, cache=False):
        super(XMLSettings, self).__init__()

        self.root = root
        self.filepath = filepath
        self.cache = cache

        if os.path.isfile(self.filepath):
            self._soup = BeautifulSoup(open(self.filepath))
            if self.root is None:
                self.root = self._soup.first().name
        else:
            if self.root is None:
                self.root = "settings"

        self.HEADER_SETTINGS = self.HEADER_SETTINGS.format(self.root)

        if not os.path.isfile(self.filepath):
            self._soup = BeautifulSoup(self.HEADER + self.HEADER_SETTINGS)

    # -------------------------------------------------------------------------------------
    def __len__(self):
        """docstring for __len__"""
        root = self._soup.find(self.root)
        if root is None:
            return 0

        return len(root.findAll(recursive=False))

    # -------------------------------------------------------------------------------------
    def __iter__(self):
        """docstring for __len__"""
        root = self._soup.find(self.root)
        if root is None:
            raise StopIteration

        for element in root.findAll(recursive=False):
            yield (element.name, dict(element.attrs))

    # -------------------------------------------------------------------------------------
    def _set_element(self, root, tagname, text=None, attr=None):
        """Creates if not available an element at the soup root element
        
        :return: tag object or None
        :rtype: Tag
        """

        # Add Topic if not available
        if attr is None:
            if root.find(re.compile(tagname+"$", re.I)) is None:
                new_tag = Tag(self._soup, tagname)
                root.insert(0, new_tag)
        else:                
            if root.find(re.compile(tagname+"$", re.I), attr) is None:
                new_tag = Tag(self._soup, tagname, attr.items())
                root.insert(0, new_tag)

        settings = self._soup.find(self.root)
        tag = settings.find(re.compile(tagname+"$", re.I))


        # Something to insert
        if tag is not None and text is not None:
            if tag.text.strip() == "":
                tag.insert(0, NavigableString(text))
            else:
                tag.contents[0].replaceWith(text)

        return tag

    # -------------------------------------------------------------------------------------
    def _set(self, topic, key, value, topic_attr=None):
        """Set key and value at topic
        
        :return: success status
        :rtype: bool"""

        # In case it is an empty document
        if not unicode(self._soup).strip().startswith("<?xml"):
            self._soup.insert(0, NavigableString(self.HEADER))

        # In case settings root is not defined
        settings = self._soup.find(self.root)
        if settings is None:
            self._soup.insert(1, Tag(self._soup, self.root))
            settings = self._soup.find(self.root)

        # Add Topic
        topic_tag = self._set_element(settings, topic.lower(), attr=topic_attr)

        if topic_tag is None:
            return False

        # Add key and value
        key_tag = self._set_element(topic_tag, key.lower(), escape(value))
        # Add "" since XML may introduce whitespaces.
        #key_tag = self._set_element(topic_tag, key, '"{0}"'.format(value))

        return key_tag is not None

    # -------------------------------------------------------------------------------------
    def _get(self, topic, key, topic_attr=None):
        """Get key at topic
        
        :return: success status
        :rtype: bool"""
        
        # In case settings root is not defined
        settings = self._soup.find(self.root)
        if settings is None:
            return None

        if topic_attr is None:
            topic_tag = settings.find(re.compile(topic+"$", re.I))
        else:
            topic_tag = settings.find(re.compile(topic+"$", re.I), topic_attr)

        if topic_tag is None:
            return None

        key_tag = topic_tag.find(re.compile(key+"$", re.I))

        if key_tag is None or len(key_tag.contents) < 1:
            return None

        value = unescape(key_tag.contents[0]).strip()
        #if value.startswith('"') and value.endswith('"'):
        #    value = value.strip('"')

        return value

    # -------------------------------------------------------------------------------------
    def _save(self, filepath=None):
        """Save the File"""
        if filepath is None:
            filepath = self.filepath

        with open(filepath, 'w') as f:
            # For the newline make sure that content is escaped
            pretty_content = self._soup.renderContents()
            
            pretty_content = self.PAT_FORMAT.sub(">\\n<", pretty_content)
            pretty_content = self.PAT_FORMAT_2.sub("<\\1><\\2>", pretty_content)
            f.write(pretty_content)
            
    # -------------------------------------------------------------------------------------
    # Public
    # -------------------------------------------------------------------------------------
    def set(self, topic, key, value, topic_attr=None):
        """Set key and value at topic
        
        :return: success status
        :rtype: bool"""

        # Won't even bother
        if "<" in topic or ">" in topic:
            return False
        if "<" in key or ">" in key:
            return False

        ret = self._set(topic, key, value, topic_attr=topic_attr)
        if ret == True:
            self._save()

        return ret

    # -------------------------------------------------------------------------------------
    def get(self, topic, key, default_value=None, create=False, topic_attr=None):
        """Get key at topic
        
        :return: success status
        :rtype: bool"""

        if not os.path.isfile(self.filepath):
            return default_value

        # Won't even bother
        if "<" in topic or ">" in topic:
            return default_value
        if "<" in key or ">" in key:
            return default_value

        # Only reload if not cached
        if not self.cache:
            self._soup = BeautifulSoup(open(self.filepath))

        ret = self._get(topic, key, topic_attr=topic_attr)
        if ret is None:
            if create:
                self.set(topic, key, default_value, topic_attr=topic_attr)

            return default_value

        return ret

    # -------------------------------------------------------------------------------------
    def remove(self, topic, key=None):
        """Remove a complete topic or key from topic"""

        if not os.path.isfile(self.filepath):
            return False

        if "<" in topic or ">" in topic:
            return False
        if key is not None and ("<" in key or ">" in key):
            return False

        # Only reload if not cached
        if not self.cache:
            self._soup = BeautifulSoup(open(self.filepath))

        # In case settings root is not defined
        settings = self._soup.find(self.root)
        if settings is None:
            return False

        topic_tag = settings.find(re.compile(topic+"$", re.I))

        if topic_tag is None:
            return False

        # Delete the whole topic
        if key is None:
            topic_tag.extract()
        else:
            # Delete only key            
            key_tag = topic_tag.find(re.compile(key+"$", re.I))
            if key_tag is None:
                return False

            key_tag.extract()

        self._save()

        return True

    # -------------------------------------------------------------------------------------
    def findall(self, topic, key, attr="name"):
        """docstring for finall"""
        entries = {}
        for name, attrs in sorted(self):
            if name.lower() == topic and attr in attrs:
                entries[attrs[attr]] = self.get(topic, key, topic_attr={attr: attrs[attr]})

        return entries

# -------------------------------------------------------------------------------------
def test():
    """Simple Unit Test"""
    import tempfile

    f, filepath = tempfile.mkstemp()

    # Don't care for the handle.
    os.close(f)

    settings = XMLSettings(filepath)
    assert settings.set("Paths", "TempPath", "C:\\temp") == True
    assert settings.set("Paths", "SettingsPath", "D:\\nettings") == True
    assert settings.set("User", "Admin", "John Doe") == True
    assert settings.get("Paths", "TempPath") == "C:\\temp"

    # Remove Key in Topic
    assert settings.remove("Paths", "TempPath") == True
    # Remove whole Topic
    settings.remove("Paths") == True

    print(filepath)

    # Manually clean up
    #os.remove(filepath)


if __name__ == '__main__':
    test()                

