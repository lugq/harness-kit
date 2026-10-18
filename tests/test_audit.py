import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', ROOT/'skills/harness-check/scripts/audit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.k = self.root/'.harness'
        (self.k/'specs').mkdir(parents=True)
        (self.k/'specs/api.md').write_text('# API\n')
        self.row = '| [API](specs/api.md) | Contract | Editing API |\n'
        (self.k/'index.md').write_text('| Document | Purpose | Read when |\n| --- | --- | --- |\n'+self.row)

    def findings(self): return a.audit(self.root)['findings']
    def codes(self): return [f['code'] for f in self.findings()]

    def test_read_only_clean_tree(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.findings(), [])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_duplicate_broken_and_orphan(self):
        with (self.k/'index.md').open('a') as f:
            f.write(self.row+'| [Missing](missing.md) | Purpose | Reading |\n')
        (self.k/'specs/orphan.md').write_text('# Orphan\n')
        self.assertTrue({'duplicate_registration','broken_link','unreachable_document'} <= set(self.codes()))

    def test_code_example_not_a_broken_link(self):
        (self.k/'specs/api.md').write_text('```md\n[example](missing.md)\n```\n')
        self.assertEqual(self.findings(), [])

    def test_placeholder_only_review(self):
        (self.k/'specs/api.md').write_text('TODO: evidence pending\n')
        self.assertEqual(self.findings()[0]['level'], 'review')

    def test_subindex_reachability(self):
        (self.k/'index.md').write_text('| [Specs](specs/index.md) | Navigation | Contracts |\n')
        (self.k/'specs/index.md').write_text('| [API](api.md) | Contract | Editing |\n')
        self.assertEqual(self.findings(), [])

    def test_multiple_valid_indexes_not_duplicate(self):
        with (self.k/'index.md').open('a') as f:
            f.write('| [Specs](specs/index.md) | Navigation | Contracts |\n')
        (self.k/'specs/index.md').write_text('| [API](api.md) | Contract | Editing |\n')
        self.assertEqual(self.findings(), [])

    def test_symlink_not_followed(self):
        outside = self.root/'old'
        outside.mkdir()
        (outside/'secret.md').write_text('do not read')
        (self.k/'linked').symlink_to(outside, target_is_directory=True)
        self.assertIn('symlink', self.codes())
        self.assertEqual(a.audit(self.root)['documents'], 2)

    def test_missing_index_and_custom_directory(self):
        (self.k/'index.md').unlink()
        self.assertIn('missing_index', self.codes())
        self.k.rename(self.root/'.custom')
        self.assertEqual(a.audit(self.root, '.custom')['documents'], 1)

    def test_missing_row_metadata(self):
        (self.k/'index.md').write_text('| [API](specs/api.md) | | |\n')
        self.assertIn('incomplete_index_row', self.codes())


if __name__ == '__main__': unittest.main()
