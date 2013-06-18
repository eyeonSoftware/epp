from datetime import datetime

__VERSION_RAW__ = (0, 3, 2, 15, )
__VERSION_STATE__ = ""
__VERSION__ =  ".".join([str(i) for i in __VERSION_RAW__]) + __VERSION_STATE__
__NAME__ = "epp"
__TITLE__ = "{0} v{1}".format(__NAME__, __VERSION__)
__COPYRIGHT__ = ("Copyright {0} see AUTHORS for details".format(datetime.now().strftime("%Y")))
__LICENSE__ = "FreeBSD see LICENSE for details"
__DESCRIPTION__ = "{0}\n{1}\n\nLicensed under {2}".format(__NAME__, __COPYRIGHT__, __LICENSE__)
__HELP__ = "https://bitbucket.org/bfloch/epp/wiki/Home"
__ISSUETRACKER__ = "https://bitbucket.org/bfloch/epp/issues"
DEBUG = __VERSION_STATE__.lower().strip().endswith("dev")
