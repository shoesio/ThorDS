"""Exercise source restoration with a real local Git repository, without a device."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/restore-sources.py'
spec = importlib.util.spec_from_file_location('restore', SCRIPT)
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


class RestoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.origin = root / 'origin'
        self.origin.mkdir()
        self.git('init', '--quiet')
        self.git('config', 'user.name', 'ThorDS test')
        self.git('config', 'user.email', 'test@example.invalid')
        (self.origin / 'source.txt').write_text('original\n')
        self.git('add', '.')
        self.git('commit', '--quiet', '-m', 'baseline')
        commit = self.git('rev-parse', 'HEAD').strip()
        (self.origin / 'source.txt').write_text('modified\n')
        self.root = root / 'snapshot'
        self.snap = self.root / 'state/checkouts/build/test'
        self.extra = self.snap / 'untracked'
        self.extra.mkdir(parents=True)
        (self.snap / 'changes.patch').write_text(self.git('diff'))
        (self.extra / 'helper').write_text('#!/bin/sh\nexit 0\n')
        (self.extra / 'helper').chmod(0o755)
        (self.extra / 'masked.service').symlink_to('/dev/null')
        (self.root / 'state/checkouts.json').write_text(json.dumps([
            {'path': 'build/test', 'origin': str(self.origin), 'commit': commit}]))
        self.hashes = {}
        for p in [self.snap / 'changes.patch', self.extra / 'helper']:
            self.hashes[str(p.relative_to(self.root))] = {
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'executable': bool(p.stat().st_mode & 0o111)}
        self.hashes[str((self.extra / 'masked.service').relative_to(self.root))] = {'symlink': '/dev/null'}
        (self.root / 'state/source-hashes.json').write_text(json.dumps(self.hashes))
        restore.ROOT = self.root
        self.dest = root / 'restored'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.origin), *args], text=True)

    def test_restores_changes_executables_and_masks(self):
        restore.restore('build/test', self.dest)
        self.assertEqual((self.dest / 'source.txt').read_text(), 'modified\n')
        self.assertTrue(os.access(self.dest / 'helper', os.X_OK))
        self.assertEqual(os.readlink(self.dest / 'masked.service'), '/dev/null')

    def test_refuses_existing_destination(self):
        self.dest.mkdir()
        (self.dest / 'keep').write_text('untouched')
        with self.assertRaises(SystemExit):
            restore.restore('build/test', self.dest)
        self.assertEqual((self.dest / 'keep').read_text(), 'untouched')

    def test_rejects_modified_source_before_clone(self):
        (self.extra / 'helper').write_text('changed')
        with self.assertRaises(SystemExit):
            restore.restore('build/test', self.dest)
        self.assertFalse(self.dest.exists())

    def test_rejects_changed_mask_before_clone(self):
        (self.extra / 'masked.service').unlink()
        (self.extra / 'masked.service').symlink_to('/etc/passwd')
        with self.assertRaises(SystemExit):
            restore.restore('build/test', self.dest)
        self.assertFalse(self.dest.exists())

    def test_rejects_unknown_checkout(self):
        with self.assertRaises(SystemExit):
            restore.restore('missing', self.dest)
        self.assertFalse(self.dest.exists())


if __name__ == '__main__':
    unittest.main()
