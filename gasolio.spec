# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start_gasolio.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('platts/platts_viewer.html', 'platts'),
        # Include serviceAccount.json only if it exists
        # ('serviceAccount.json', '.'),
    ],
    hiddenimports=[
        'engineio.async_drivers.threading',
        'flask',
        'firebase_admin',
        'firebase_admin.credentials',
        'firebase_admin.firestore',
        'firebase_admin.auth',
        'requests',
        'investpy',
        'pandas',
        'numpy',
        'urllib3',
        'pkg_resources.py2_warn',
        'pkg_resources.markers',
        'threading',
        'webbrowser',
        'json',
        're',
        'functools',
        'os',
        'sys',
        'subprocess',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused modules to reduce size
        'selenium',
        'webdriver_manager',
        'tkinter'
    ],
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
    name='Gasolio_Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add icon if available - commented out if not present
    # icon='platts/icon.ico'
) 
