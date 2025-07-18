# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start_gasolio.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('platts/platts_viewer.html', 'platts'),
        ('serviceAccount.json', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'engineio.async_drivers.threading',
        'flask',
        'selenium',
        'firebase_admin',
        'webdriver_manager',
        'requests'
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
    name='Gasolio Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='platts/icon.ico'  # Aggiungi un'icona se la hai
) 