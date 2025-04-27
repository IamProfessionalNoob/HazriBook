# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# Check if icon exists
icon_file = 'app_icon.ico' if os.path.exists('app_icon.ico') else None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.py', '.'),
        ('database.py', '.'),
        ('messaging.py', '.'),
        ('staff.db', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'plotly',
        'streamlit_option_menu',
        'bcrypt',
        'xlsxwriter',
        'python-dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HaazriBook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file  # Now uses the icon if it exists, otherwise None
) 