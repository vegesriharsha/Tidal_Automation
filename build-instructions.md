# Converting REST API Client to Executable

## Prerequisites
```bash
pip install pyinstaller
pip install requests
```

## Build Steps

1. Create a spec file named `rest_api_client.spec`:
```python
# rest_api_client.spec
block_cipher = None

a = Analysis(
    ['rest_api_client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RestApiClient',
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
    icon='app.ico'  # Optional: Add your icon file
)
```

2. Build Commands:
```bash
# Simple build
pyinstaller --onefile --windowed rest_api_client.py

# Build with spec file
pyinstaller rest_api_client.spec
```

3. Locate Executable:
- Windows: `dist/RestApiClient.exe`
- Linux/Mac: `dist/RestApiClient`

## Distribution
- Share the executable from the `dist` folder
- Include any required certificates or configuration files

## Troubleshooting
- If missing dependencies: Add to `hiddenimports` in spec file
- If SSL issues: Include certificates in `datas` section
- If tkinter errors: Ensure Python installation includes tkinter

## Notes
- Use `--onefile` for single executable
- Use `--windowed` to prevent console window
- Test executable in clean environment
- Verify all dependencies are included