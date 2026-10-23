import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

source=Path('/Users/admin/ThorDS/build/thorch-work/packages/thords-kiosk/rootfs/usr/bin/thords-wake-policy')
loader=importlib.machinery.SourceFileLoader('wake', str(source))
spec=importlib.util.spec_from_loader(loader.name, loader)
wake=importlib.util.module_from_spec(spec)
loader.exec_module(wake)

class WakeTests(unittest.TestCase):
    def test_restore_preserves_original_value(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'wake-settings.json'
            state.write_text('{"/sys/devices/test/power/wakeup": "enabled"}')
            with patch.object(wake,'STATE',state), patch.object(Path,'write_text') as write:
                wake.restore()
                write.assert_called_once_with('enabled')
            self.assertFalse(state.exists())
    def test_failed_restore_is_retained_for_retry(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'wake-settings.json'
            state.write_text('{"/sys/devices/test/power/wakeup": "enabled"}')
            real=Path.write_text
            def write(p,value):
                if str(p).startswith('/sys/'):
                    raise PermissionError()
                return real(p,value)
            with patch.object(wake,'STATE',state), patch.object(Path,'write_text',write):
                with self.assertRaises(OSError): wake.restore()
            self.assertIn('enabled',state.read_text())
    def test_invalid_restore_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            state=Path(d)/'wake-settings.json';state.write_text('{"/etc/passwd":"enabled"}')
            with patch.object(wake,'STATE',state):
                with self.assertRaises(ValueError): wake.restore()
            self.assertTrue(state.exists())
    def test_ledger_bounded(self):
        with tempfile.TemporaryDirectory() as d:
            log=Path(d)/'ledger';log.write_text('\n'.join(['{}']*600))
            original=Path.read_text
            def read(p,*a,**kw):
                if str(p)=='/sys/power/pm_wakeup_irq': return '17'
                if str(p)=='/proc/interrupts': return '17: 1 0 hall-lid\n'
                return original(p,*a,**kw)
            with patch.object(wake,'LOG',log),patch.object(Path,'read_text',read):wake.ledger()
            self.assertEqual(len(log.read_text().splitlines()),250)
            self.assertIn('hall-lid',log.read_text())
unittest.main()
