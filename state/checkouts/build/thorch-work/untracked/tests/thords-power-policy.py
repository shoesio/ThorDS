#!/usr/bin/env python3
"""Exercise power policy against fake hardware, including unsafe IRQ routing."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'packages/thords-kiosk/rootfs/usr/bin'


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = dict(os.environ, THORDS_SYSFS_ROOT=str(self.root / 'sys'),
                        THORDS_PROC_ROOT=str(self.root / 'proc'),
                        THORDS_POWER_CONFIG=str(self.root / 'power.conf'))
        self.write('bin/systemctl', '#!/bin/sh\nexit 3\n', executable=True)
        self.env['PATH'] = str(self.root / 'bin') + ':' + self.env['PATH']
        for n in (0, 3, 7):
            base = f'sys/devices/system/cpu/cpufreq/policy{n}/'
            self.write(base + 'scaling_available_governors', 'performance schedutil ondemand')
            self.write(base + 'scaling_governor', 'performance')
            self.write(base + 'scaling_max_freq', '3000000')
        self.write('sys/class/devfreq/3d00000.gpu/available_governors', 'performance simple_ondemand')
        self.write('sys/class/devfreq/3d00000.gpu/governor', 'performance')
        self.write('sys/devices/system/cpu/cpu0/cpuidle/state1/disable', '1')
        self.write('proc/irq/default_smp_affinity', '07')
        self.write('proc/interrupts', '198: 1 0 gpu-irq\n200: 0 0 gmu\n')
        for irq in (198, 200):
            self.write(f'proc/irq/{irq}/smp_affinity_list', '0-2')
            self.write(f'proc/irq/{irq}/effective_affinity', 'f8')

    def write(self, name, value, executable=False):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value)
        if executable:
            p.chmod(0o755)

    def run_policy(self, name, *args):
        return subprocess.run(['bash', str(BIN / name), *args], env=self.env,
                              capture_output=True, text=True)

    def test_adaptive_and_performance(self):
        for profile, cpu, gpu in [('balanced', 'schedutil', 'simple_ondemand'),
                                  ('performance', 'performance', 'performance')]:
            result = self.run_policy('thords-performance', profile)
            self.assertEqual(result.returncode, 0, result.stderr)
            for n in (0, 3, 7):
                base = self.root / f'sys/devices/system/cpu/cpufreq/policy{n}'
                self.assertEqual((base/'scaling_governor').read_text(), cpu)
                self.assertEqual((base/'scaling_max_freq').read_text(), '3000000')
            self.assertEqual((self.root/'sys/class/devfreq/3d00000.gpu/governor').read_text(), gpu)

    def test_unsupported_governor_does_not_partially_change_clocks(self):
        self.write('sys/class/devfreq/3d00000.gpu/available_governors', 'performance')
        self.assertNotEqual(self.run_policy('thords-performance').returncode, 0)
        self.assertEqual((self.root/'sys/devices/system/cpu/cpufreq/policy0/scaling_governor').read_text(), 'performance')

    def test_deep_idle_requires_verified_gpu_affinity(self):
        self.assertEqual(self.run_policy('thords-irq-policy').returncode, 0)
        idle = self.root/'sys/devices/system/cpu/cpu0/cpuidle/state1/disable'
        self.assertEqual(idle.read_text(), '0')
        self.write('proc/irq/200/effective_affinity', '01')
        self.assertNotEqual(self.run_policy('thords-irq-policy').returncode, 0)
        self.assertEqual(idle.read_text(), '1')

    def test_irqbalance_keeps_old_idle_workaround(self):
        self.write('bin/systemctl', '#!/bin/sh\nexit 0\n', executable=True)
        self.assertNotEqual(self.run_policy('thords-irq-policy').returncode, 0)
        self.assertEqual((self.root/'sys/devices/system/cpu/cpu0/cpuidle/state1/disable').read_text(), '1')

    def test_battery_units_and_charge_reset(self):
        summary = runpy.run_path(str(BIN/'thords-power-sample'))['summarize']
        a = dict(boottime=0, iv_watts=4, capacity=80, status='Discharging', charge_counter=5000000, voltage_now=4000000)
        b = dict(a, boottime=3600, charge_counter=4000000)
        self.assertEqual(summary([a, b])['charge_based_watts'], 4)
        self.assertIsNone(summary([a, dict(b, status='Charging')])['charge_based_watts'])
        self.assertIsNone(summary([a, dict(b, charge_counter=6000000)])['charge_based_watts'])


if __name__ == '__main__':
    unittest.main()
