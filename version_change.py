#!/usr/bin/env python
#coding=utf-8
#? py __INFO__.py . . . +

'''
version_build_up.py
####################################

Set the build version up.

Examples:

version_change __INFO__.py . + 0 0
> Version changed: v0.3.1.2 -> v0.4.0.0

version_change __INFO__.py . . . +
> Version changed: v0.3.1.2 -> v0.3.1.3

version_change __INFO__.py + 0 0 0
> Version changed: v0.3.1.2 -> v1.0.0.0

:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import fileinput
import os
import re
import shutil
import sys

# -------------------------------------------------------------------------------------
def main():
    """docstring for main"""
    
    pat_version = re.compile("__VERSION_RAW__\s*=\s*.*$")

    filepath = os.path.abspath(sys.argv[1])

    if len(sys.argv) < 6:
        raise ValueError("Version has to be 4 digits, + or .")

    ops = sys.argv[2:6]

    # Create a backup
    curdir = os.path.dirname(os.path.abspath( __file__ ))
    bak_filepath = os.path.join(curdir, os.path.basename(filepath)+".bak")
    if os.path.isfile(bak_filepath):
        os.remove(bak_filepath)
    shutil.copy2(filepath, bak_filepath)

    for line in fileinput.input(filepath, inplace=1):
        
        if pat_version.match(line) is not None:
            exec(line.lstrip())
            ver = list(__VERSION_RAW__)
            while len(ver) < 4:
                ver += (0,)

            old_ver = list(ver)

            for i, op in enumerate(ops):
                if op == "+":
                    ver[i] = ver[i] + 1
                elif op == ".":
                    pass
                else:
                    ver[i] = int(op)
            
            print "__VERSION_RAW__ = ({0}, {1}, {2}, {3}, )".format(*ver)
        else:
            print line,

    print "Version changed: v{0}.{1}.{2}.{3} -> v{4}.{5}.{6}.{7}".format(*(old_ver+ver))

if __name__ == '__main__':
    main()
