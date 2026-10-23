from pathlib import Path
import os
import subprocess
import tempfile
root=Path('/Users/admin/ThorDS/build/thorch-work/packages/thords-kiosk/rootfs/usr/bin')
with tempfile.TemporaryDirectory() as d:
    config=Path(d)/'.config/azaharplus-emu/qt-config.ini'
    config.parent.mkdir(parents=True)
    config.write_text('resolution_factor=3\nresolution_factor\\default=true\ntexture_filter=0\ntexture_filter\\default=true\nfilter_mode=true\nfilter_mode\\default=true\n')
    subprocess.run(['bash',str(root/'thords-configure-performance')],env=dict(os.environ,HOME=d),check=True)
    s=config.read_text()
    assert 'resolution_factor=4\n' in s
    assert 'texture_filter=4\n' in s
    assert 'filter_mode=false\n' in s
    assert 'texture_filter\\default=false\n' in s
session=(root/'thords-session').read_text()
assert 'resolution_factor=3' not in session
assert 'texture_filter=0' not in session
assert 'texture_filter=1' not in session
assert 'custom_bottom_width=1240' in session
print('4x/xBRZ settings and HOME override checks passed')
