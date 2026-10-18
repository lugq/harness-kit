import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('updater', ROOT/'skills/harness-update/scripts/update.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/'source'
        self.source.mkdir()
        shutil.copytree(ROOT/'skills', self.source/'skills', ignore=shutil.ignore_patterns('__pycache__'))
        self.parent = self.root/'installed'
        self.parent.mkdir()
        for name in u.NAMES:
            shutil.copytree(self.source/'skills'/name, self.parent/name)
        self.before = {name: u.hashes(self.parent/name) for name in u.NAMES}

    def baseline(self):
        for name in u.NAMES:
            (self.parent/name/u.STATE).write_text(json.dumps({'commit': 'old', 'files': self.before[name]}))

    def assert_original(self):
        self.assertEqual(self.before, {name: u.hashes(self.parent/name) for name in u.NAMES})

    def test_package_and_blank_project_links(self):
        for name in u.NAMES:
            u.validate(self.source/'skills'/name, name)
        project = self.root/'blank'
        shutil.copytree(self.source/'skills/harness-init/assets', project)
        for p in project.rglob('*.md'):
            for link in u.re.findall(r'\[[^\]]*\]\(([^)]+)\)', p.read_text()):
                self.assertTrue((p.parent/link).exists(), (p, link))
        self.assertTrue((project/'.harness/verification.md').exists())

    def test_standard_install_first_real_upgrade(self):
        subprocess.run(['git', 'init', '-q', str(self.source)], check=True)
        def commit(message):
            u.git('-C', self.source, 'add', '.')
            u.git('-C', self.source, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', message)
        commit('version one')
        with (self.source/'skills/harness-init/SKILL.md').open('a') as f:
            f.write('\nVersion two\n')
        commit('version two')
        revision = u.git('-C', self.source, 'rev-parse', 'HEAD').decode().strip()
        u.update(self.source, self.parent, revision)
        for name in u.NAMES:
            self.assertEqual(u.hashes(self.parent/name), u.hashes(self.source/'skills'/name))
            self.assertEqual(json.loads((self.parent/name/u.STATE).read_text())['commit'], revision)

    def test_check_does_not_write(self):
        u.update(self.source, self.parent, 'new', check=True)
        self.assert_original()
        self.assertFalse((self.parent/u.TRANSACTION).exists())
        self.assertFalse((self.parent/u.NAMES[0]/u.STATE).exists())

    def test_local_changes_and_extra_files_block_both(self):
        self.baseline()
        (self.parent/u.NAMES[0]/'extra.txt').write_text('local')
        before = {n: u.hashes(self.parent/n) for n in u.NAMES}
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')
        self.assertEqual(before, {n: u.hashes(self.parent/n) for n in u.NAMES})

    def test_unknown_no_baseline_copy_blocks(self):
        (self.parent/u.NAMES[0]/'extra.txt').write_text('local')
        with patch.object(u, 'historical_match', return_value=None):
            with self.assertRaises(ValueError):
                u.update(self.source, self.parent, 'new')
        self.assertFalse((self.parent/u.TRANSACTION).exists())

    def test_invalid_package_does_not_replace(self):
        for name in u.NAMES:
            (self.source/'skills'/name/'SKILL.md').write_text('broken')
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')
        self.assert_original()

    def test_missing_reference_blocks(self):
        with (self.source/'skills/harness-init/SKILL.md').open('a') as f:
            f.write('\n[missing](references/absent.md)\n')
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')
        self.assert_original()

    def test_staging_copy_failure_preserves_install(self):
        with patch.object(u.shutil, 'copytree', side_effect=OSError('disk full')):
            with self.assertRaises(OSError):
                u.update(self.source, self.parent, 'new')
        self.assert_original()
        self.assertFalse((self.parent/u.TRANSACTION).exists())

    def test_second_replace_interrupt_rolls_back_pair(self):
        original = Path.rename
        def fail(path, dst):
            if path == self.parent/u.TRANSACTION/'new'/u.NAMES[1]:
                raise KeyboardInterrupt()
            return original(path, dst)
        with patch.object(Path, 'rename', fail):
            with self.assertRaises(KeyboardInterrupt):
                u.update(self.source, self.parent, 'new')
        self.assert_original()
        self.assertFalse((self.parent/u.TRANSACTION).exists())

    def test_failed_rollback_preserves_backup_and_can_resume(self):
        original = Path.rename
        def fail(path, dst):
            if path == self.parent/u.TRANSACTION/'new'/u.NAMES[1] or 'backup' in path.parts:
                raise OSError('replace failure')
            return original(path, dst)
        with patch.object(Path, 'rename', fail):
            with self.assertRaises(RuntimeError):
                u.update(self.source, self.parent, 'new')
        self.assertTrue((self.parent/u.TRANSACTION/'backup'/u.NAMES[0]).is_dir())
        u.recover(self.parent)
        self.assert_original()

    def test_hard_interruption_residue_requires_explicit_recovery(self):
        txn = self.parent/u.TRANSACTION
        (txn/'backup').mkdir(parents=True)
        (self.parent/u.NAMES[0]).rename(txn/'backup'/u.NAMES[0])
        shutil.copytree(self.source/'skills'/u.NAMES[0], self.parent/u.NAMES[0])
        with (self.parent/u.NAMES[0]/'SKILL.md').open('a') as f:
            f.write('\nnew incomplete run\n')
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')
        u.recover(self.parent)
        self.assert_original()

    def test_git_disables_prompts_and_has_timeout(self):
        with patch.object(u.subprocess, 'check_output', return_value=b'') as run:
            u.git('status')
        self.assertEqual(run.call_args.kwargs['timeout'], 120)
        self.assertEqual(run.call_args.kwargs['env']['GIT_TERMINAL_PROMPT'], '0')

    def test_https_can_reuse_gh_without_changing_config(self):
        with patch.object(u.shutil, 'which', return_value='/usr/local/bin/gh'):
            with patch.object(u.subprocess, 'check_output', return_value=b'') as run:
                u.git('clone', 'https://github.com/lugq/harness-kit.git', 'destination')
        self.assertIn('credential.helper=!gh auth git-credential', run.call_args.args[0])

    def test_committed_cleanup_failure_does_not_roll_back_one_skill(self):
        self.baseline()
        with (self.source/'skills/harness-init/SKILL.md').open('a') as f:
            f.write('\nNew release\n')
        original = shutil.rmtree
        txn = self.parent/u.TRANSACTION
        def fail(path, *args, **kwargs):
            if path == txn:
                original(txn/'backup'/u.NAMES[0])
                raise OSError('cleanup interrupted')
            return original(path, *args, **kwargs)
        with patch.object(u.shutil, 'rmtree', fail):
            with self.assertRaises(OSError):
                u.update(self.source, self.parent, 'new')
        self.assertTrue((txn/'committed').exists())
        u.recover(self.parent)
        for name in u.NAMES:
            self.assertEqual(u.hashes(self.parent/name), u.hashes(self.source/'skills'/name))

    def test_symlink_extra_blocks(self):
        (self.parent/u.NAMES[0]/'linked').symlink_to(self.root)
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')

    def test_two_entry_install_migrates_to_three(self):
        shutil.rmtree(self.parent/'harness-spec')
        self.baseline_for_existing()
        u.update(self.source, self.parent, 'new', check=True)
        self.assertFalse((self.parent/'harness-spec').exists())
        u.update(self.source, self.parent, 'new')
        for name in u.NAMES:
            self.assertEqual(u.hashes(self.parent/name), u.hashes(self.source/'skills'/name))

    def baseline_for_existing(self):
        for name in u.NAMES:
            if (self.parent/name).exists():
                (self.parent/name/u.STATE).write_text(json.dumps({'commit': 'old', 'files': self.before[name]}))

    def test_new_entry_removed_on_failed_migration(self):
        shutil.rmtree(self.parent/'harness-spec')
        self.baseline_for_existing()
        original = Path.write_text
        def fail(path, *args, **kwargs):
            if path.name == 'committed':
                raise OSError('interrupted before commit marker')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'write_text', fail):
            with self.assertRaises(OSError):
                u.update(self.source, self.parent, 'new')
        self.assertFalse((self.parent/'harness-spec').exists())
        for name in ('harness-init', 'harness-update'):
            self.assertEqual(u.hashes(self.parent/name), self.before[name])

    def test_new_entry_local_edits_block_update(self):
        self.baseline()
        (self.parent/'harness-spec'/'local.md').write_text('local edits')
        with self.assertRaises(ValueError):
            u.update(self.source, self.parent, 'new')
        self.assertTrue((self.parent/'harness-spec'/'local.md').exists())


if __name__ == '__main__':
    unittest.main()
