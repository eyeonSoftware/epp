from datetime import datetime
from epp.__INFO__ import __VERSION_RAW__, __VERSION_STATE__, __NAME__, __COPYRIGHT__, __DESCRIPTION__
import platform

# Make sure its 4 digits long
ver = __VERSION_RAW__
state = __VERSION_STATE__
if state.strip() != "":
    state = " (" + state + ")"
while len(ver) < 4:
    ver += (0,)

print """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({0}),
    prodvers=({0}),
    mask=0x0,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904E4', 
        [StringStruct('CompanyName', 'eyeon Software Inc.'),
        StringStruct('ProductName', '{3}'),
        StringStruct('ProductVersion', '{0}'),
        StringStruct('InternalName', ''),
        StringStruct('OriginalFilename', '{2}'),
        StringStruct('FileVersion', '{1}'),
        StringStruct('FileDescription', '{3}{5}'),
        StringStruct('LegalCopyright', '{4}'),])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1252])])
  ]
)
""".format(",".join([str(i) for i in ver]), ".".join([str(i) for i in ver[:3]]),
        'epp_launcher.exe'.format(platform.architecture()[0]), __NAME__, __COPYRIGHT__, state)
