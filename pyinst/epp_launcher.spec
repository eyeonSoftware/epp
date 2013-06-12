# -*- mode: python -*-

# create version.txt
import inspect, os, platform
current_path = os.path.dirname(inspect.getfile( inspect.currentframe() ) )
os.system("python {0} > {1}".format( os.path.join(current_path, "version.py"), os.path.join(current_path, "version.txt")))

a = Analysis(['C:\\eyeon\\repos\\epp\\src\\epp\\bin\\epp_launcher.py',
            'C:\\eyeon\\repos\\epp\\src\\epp\\helper\\xml\\dir_query.py'],
             pathex=['C:\\eyeon\\repos\\epp\\pyinst'],
             hiddenimports=[ ],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\epp_launcher', 'launcher.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='..\\src\\_rc\\epp_128.ico',
          version="version.txt"
          )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'epp_launcher'))
