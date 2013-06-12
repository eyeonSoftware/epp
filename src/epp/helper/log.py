#!/usr/bin/env python
#coding=utf-8

'''
log.py
####################################


:copyright: 2013 by eyeon Software Inc., see AUTHORS for more details
:license: Some rights reserved, see LICENSE for more details
'''

import __main__
import inspect
import logging
import socket
import getpass
import os
import sys

from epp.helper.osplus import app_path
from epp.__INFO__ import DEBUG, __TITLE__

from PySide.QtGui import QMessageBox, QApplication, QStyleFactory, QPalette, QColor

# -------------------------------------------------------------------------------------
class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
      self.leftalign = "\n"+30*" "
 
   def write(self, buf):
      stack = inspect.stack()[1][0]
      if len(buf.strip()) > 0:
          log(buf.rstrip().replace("\n", self.leftalign) + " (PRINT)", self.log_level, stack=stack)

# -------------------------------------------------------------------------------------
def setup_log(TITLE, DEBUG=False):
    """docstring for setup_log"""
    hostname = socket.gethostbyaddr(socket.gethostname())[0]
    user = getpass.getuser()

    # In case of debuggin use the console - else write log files
    if DEBUG == False:

        log_dir = app_path("logs")
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            
        log_filepath = os.path.join(log_dir,"epp_{0}_{1}.log".format(hostname, user))
        logging.basicConfig(filename=log_filepath, format="%(asctime)s [%(levelname)-7s] %(message)s (%(mod)s:%(line)s)", datefmt="%Y-%m-%d %H:%M:%S")
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(format="[%(levelname)-7s] %(message)s (%(mod)s:%(line)s)", datefmt="%Y-%m-%d %H:%M:%S")
        logging.getLogger().setLevel(logging.DEBUG)

    info("------------------------------------------------")
    info("{0} as {1} on {2}".format(TITLE, user, hostname))

    # Print to Log
    sl = StreamToLogger(logging.getLogger(), logging.DEBUG)
    #sys.stdout = sl

# -------------------------------------------------------------------------------------
def log(msg, level, msgbox=False, parent="auto", stack=None):
    """docstring for error"""

    if stack is None:
        stack = inspect.stack()[1][0]

    #print inspect.stack()
    #print stack
    #print inspect.getmodule(stack)


    if inspect.getmodule(stack) is None:
        mod = inspect.stack()[1][1]
    else:
        mod = inspect.getmodule(stack).__name__
    lineno = stack.f_lineno

    if mod == "__main__":
        mod = "__main__:" + os.path.basename(__main__.__file__)

    logging.log(level, msg, extra={"mod": mod, "line": lineno})

    if msgbox:
        if parent == "auto":
            qapp = QApplication.instance()
            if qapp is None:
                qapp = QApplication([])
                qapp.setStyle(QStyleFactory.create("plastique") )
                palette = QPalette(QColor(62, 62, 62), QColor(62, 62, 62))
                palette.setColor(palette.Highlight, QColor(255*0.6, 198*0.6, 0))
                qapp.setPalette(palette)
            parent = qapp.activeWindow()

        if level == logging.DEBUG:
            QMessageBox.info(parent, logging.getLevelName(level).capitalize(), msg)
        elif level == logging.INFO:
            QMessageBox.information(parent, logging.getLevelName(level).capitalize(), msg)
        elif level == logging.WARNING:
            QMessageBox.warning(parent, logging.getLevelName(level).capitalize(), msg)
        elif level == logging.ERROR:
            QMessageBox.critical(parent, logging.getLevelName(level).capitalize(), msg)
        elif level == logging.CRITICAL:
            QMessageBox.critical(parent, logging.getLevelName(level).capitalize(), msg)

# -------------------------------------------------------------------------------------
def debug(msg, msgbox=False, parent="auto"):
    """docstring for error"""
    stack = inspect.stack()[1][0]
    log(msg, logging.DEBUG, msgbox, parent, stack)

# -------------------------------------------------------------------------------------
def info(msg, msgbox=False, parent="auto"):
    """docstring for error"""
    stack = inspect.stack()[1][0]
    log(msg, logging.INFO, msgbox, parent, stack)

# -------------------------------------------------------------------------------------
def warning(msg, msgbox=False, parent="auto"):
    """docstring for error"""
    stack = inspect.stack()[1][0]
    log(msg, logging.WARNING, msgbox, parent, stack)

# -------------------------------------------------------------------------------------
def error(msg, msgbox=False, parent="auto"):
    """docstring for error"""
    stack = inspect.stack()[1][0]
    log(msg, logging.ERROR, msgbox, parent, stack)

# -------------------------------------------------------------------------------------
def critical(msg, msgbox=False, parent="auto"):
    """docstring for error"""
    stack = inspect.stack()[1][0]
    log(msg, logging.CRITICAL, msgbox, parent, stack)

# -------------------------------------------------------------------------------------
def exception(e, stack=None):
    """docstring for exception"""
    if stack is None:
        stack = inspect.stack()[1][0]

    if inspect.getmodule(stack) is None:
        mod = inspect.stack()[1][1]
    else:
        mod = inspect.getmodule(stack).__name__
    lineno = stack.f_lineno

    if mod == "__main__":
        mod = "__main__:" + os.path.basename(__main__.__file__)

    logging.critical(e, extra={"mod": mod, "line": lineno})

# Init
setup_log(__TITLE__, DEBUG)
