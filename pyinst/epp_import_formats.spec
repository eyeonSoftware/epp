# -*- mode: python -*-
#? py

a = Analysis(['C:\\eyeon\\repos\\epp\\src\\epp\\bin\\epp_import_formats.py'],
             pathex=['C:\\Python\\pyinstaller'],
             hiddenimports=[],
             hookspath=None,
            )
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\epp_import_formats', 'import_formats.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='..\\src\\_rc\\epp_128.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'epp_import_formats'))
