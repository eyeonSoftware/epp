#!/usr/bin/env python
#coding=utf-8

'''
dir.py
####################################

Creation on XML based directory strucutres.

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

from optparse import OptionParser
import os
import shutil
import sys
import time

import epp.helper.xml.basexml as xh

def str2bool(v):
  return v.lower() in ["yes", "y", "true", "t", "1"]


# #############################################################################################
class StructHandler(object):
    """
    This class represents a struct handler
    """

    # -------------------------------------------------------------------------------------
    # Attributes
    root = ""       # Root Directory
    file = ""
    struct = {}     # Dict with structure
    parsedict = []       # Parsing arguments
    pathList = []

    # -------------------------------------------------------------------------------------
    def multiple_replace(self, text, wordDict):
        """
        take a text and replace words that match the key in a dictionary
        with the associated value, return the changed text
        """
        for key in wordDict:
            text = text.replace('$'+key+';', str(wordDict[key]))
            text = text.replace('$'+key, str(wordDict[key]))
            
            text = text.replace('$__TIMEFS__;', time.strftime("%H_%M_%S"))
            text = text.replace('$__TIMEFS__', time.strftime("%H_%M_%S"))
            
            text = text.replace('$__TIME__;', time.strftime("%H:%M:%S"))
            text = text.replace('$__TIME__', time.strftime("%H:%M:%S"))
            
            text = text.replace('$__DATEFS__;', time.strftime("%y_%m_%d"))
            text = text.replace('$__DATEFS__', time.strftime("%y_%m_%d"))
            
            text = text.replace('$__DATE__;', time.strftime("%m/%d/%y"))
            text = text.replace('$__DATE__', time.strftime("%m/%d/%y"))
            
            text = text.replace('$__ROOT__;', self.root )
            text = text.replace('$__ROOT__', self.root )
            

        if self.environ:
            for key in os.environ:
                old_text = text
                text = text.replace('%'+key+'%', os.environ[key])
                if text != old_text:
                    self.used_environ[key] = os.environ[key]

        return text

    # -------------------------------------------------------------------------------------
    # Private
    def verify_parsedict(self, parsedict):

        if isinstance(parsedict, dict):
            return parsedict

        d = {}

        for cur_arg in parsedict:
            
            cur_dict = cur_arg.split("=", 1)

            if len(cur_dict) == 2:

                if cur_dict[0] in d.keys():
                    #TODO HANDLE PARAMETER MORE THAN ONCE (override)
                    pass

                d[cur_dict[0]] = cur_dict[1]
            else:
                #TODO HANDLE WRONG ARGUMENTS!
                pass

        return d

    # -------------------------------------------------------------------------------------
    def path(self):
        return os.path.join(*self.pathList)


    
    # -------------------------------------------------------------------------------------
    def file_append(self, file, entry):

        if 'content' in entry:

            try:
                _parse = str2bool(entry['attrib']['parse'])
            except:
                _parse = False

            f = open(file, 'a')
            for curline in entry['content'].split("\n"):
                if _parse:
                    curline = self.multiple_replace(curline.strip(), self.parsedict)

                f.write("\n" + curline)
            f.close

    # -------------------------------------------------------------------------------------
    def file_prepend(self, file, entry):

        if 'content' in entry:

            # read the current contents of the file
            f = open(file)
            text = f.read()
            f.close()
            # open the file again for writing
            f = open(file, 'w')

            try:
                _parse = str2bool(entry['attrib']['parse'])
            except:
                _parse = False

            for curline in entry['content'].split("\n"):
                if _parse:
                    curline = self.multiple_replace(curline.strip(), self.parsedict)

                f.write(curline + "\n")

            # write the original contents
            f.write(text)
            f.close()

    # -------------------------------------------------------------------------------------
    def file_create(self, file, entry):

        if 'content' in entry:

            # read the current contents of the file
            try:
                _override = str2bool(entry['attrib']['override'])
            except:
                _override = False

            # Don't override?
            if os.path.isfile(file) and _override == False:
                return

            # open the file again for writing
            f = open(file, 'w')

            try:
                _parse = str2bool(entry['attrib']['parse'])
            except:
                _parse = False

            try:
                _unescape = str2bool(entry['attrib']['unescape'])
            except:
                _unescape = False

            for curline in entry['content'].split("\n"):
                if _unescape:
                    curline = curline.replace("&lt;", "<").replace("&gt;", ">")
                if _parse:
                    curline = self.multiple_replace(curline.strip(), self.parsedict)

                f.write(curline + "\n")

            f.close()

    # -------------------------------------------------------------------------------------
    def parse_tag_file(self, struct):
        if not 'name' in struct['attrib']:
            raise ValueError("XML File corrupt: Filename missing")

        filename = struct['attrib']['name']
        filepath = os.path.join(self.path(), filename)

        if 'src' in struct['attrib']:
            src_filepath = struct['attrib']['src']
            if not os.path.isabs(src_filepath):
                src_filepath = os.path.join(os.path.dirname(self.file), src_filepath)
            # Copy the file
            if os.path.isfile(src_filepath):
                shutil.copyfile(src_filepath, filepath)
            else:
                raise ValueError("File does not exist %s" % src_filepath)
        else:
            # Create empty file
            if os.path.isfile(filepath):
                if self.overwrite == 'r':
                    raise ValueError("File already exists %s" % filepath)
                elif self.overwrite == 'y':
                    os.remove(filepath)
                    f = open(filepath, 'w')
                    f.close()
                else:
                    pass
            else:
                f = open(filepath, 'w')
                f.close()



        if 'children' in struct:
            for cur_child in struct['children']:
                
                for cur_name, cur_entry in cur_child.items():
                    
                    if cur_name.lower() == 'append':
                        self.file_append(filepath, cur_entry)
                    elif cur_name.lower() == 'prepend':
                        self.file_prepend(filepath, cur_entry)
                    elif cur_name.lower() == 'create':
                        self.file_create(filepath, cur_entry)

    # -------------------------------------------------------------------------------------
    def parse_struct(self, struct):

        #print struct
        #print "\n\n"
        self.used_environ = {}

        for cur_name, cur_entry in struct.items():

            _children_to_parse = True

            if cur_name.lower() == "__comment__":
                continue

            if 'attrib' in cur_entry:
                for cur_attrib_name, cur_attrib_entry in cur_entry['attrib'].items():
                    struct[cur_name]['attrib'][cur_attrib_name] = self.multiple_replace(cur_attrib_entry, self.parsedict)

            if cur_name.lower() == "folder":
                #Create dir
                self.pathList.append( cur_entry['attrib']['name'] )
                if not os.path.isdir(self.path()):
                    os.makedirs(self.path())
            
            if cur_name.lower() == "file":
                _children_to_parse = False
                self.parse_tag_file(cur_entry)

            
            # Debug
            #try:
                #print (self.level*" _ " + cur_name + ": " + cur_entry['attrib']['name'])
            #except:
                #print (self.level*" _ " + cur_name)

            # ---------------------------------------------------- 
            # Children

            if 'children' in cur_entry and _children_to_parse:
                self.level += 1
                struct[cur_name]['children'] = map(self.parse_struct, struct[cur_name]['children'])
                self.level -= 1

        if cur_name.lower() == "folder":
            self.pathList.pop()

        #print ("")
        return struct

    def doprint(self, obj):
        pass
        #print self.level*" --", obj

    # -------------------------------------------------------------------------------------
    def __init__(self, file_, root, overwrite, environ, parsedict):
        """
        Constructor.
        """

        self.file = file_
        self.root = root
        self.environ = environ
        self.overwrite = overwrite


        self.pathList = []
        self.pathList.append(root)

        self.parsedict = self.verify_parsedict(parsedict)

        struct = xh.xmlfile_to_dict(self.file)

        self.level = 0

        self.parse_struct(struct)
        self.struct = struct

    # -------------------------------------------------------------------------------------
    # Public


# -------------------------------------------------------------------------------------
def struct_from_dict():

    pass



# #############################################################################################
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file", help="Template XML file")
    parser.add_option("-r", "--root", dest="root", metavar="ROOTDIR", help="Root directory")
    parser.add_option("-m", "--makeroot", dest="makeroot", default=False, action="store_true", help="Make root directory if it does not exist")
    parser.add_option("-o", "--overwrite", dest="overwrite", default="y", metavar="OVERWRITEMODE", help="Overwrite files that exists. [y]es (default) [n]o [r]aise error ")
    parser.add_option("-e", "--environ", dest="environ", default=False, action="store_true", help="Parse Environment Variables (%ENV%)")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    (options, args) = parser.parse_args()

    if not os.path.isfile(options.file):
        parser.error("Template File does not exist")

    if not options.root == None and not os.path.isdir(options.root):
        if options.makeroot == False:
            parser.error("Root dir does not exist")
        else:
            try:
               os.makedirs(options.root)
            except:
                parser.error("Root dir could not be created")

    sh = StructHandler(options.file, options.root, options.overwrite, options.environ, args)
