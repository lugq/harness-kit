import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/harness-spec'
spec = importlib.util.spec_from_file_location('docs_check', SKILL/'scripts/check_docs.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class SpecTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'.harness/features').mkdir(parents=True)
        (self.root/'src').mkdir()
        (self.root/'src/export.py').write_text('def export(value):\n    if not value: raise ValueError("empty")\n    return value.upper()\n')
        self.document = '.harness/features/export.md'
        (self.root/self.document).write_text('# Export\n\n[Source](../../src/export.py)\n')
        self.index = '.harness/index.md'
        self.row = '| [Export](features/export.md) | Export contract | Editing export |\n'
        (self.root/self.index).write_text('| Document | Purpose | Read when |\n| --- | --- | --- |\n'+self.row)

    def check(self):
        v.check(self.root, [self.index], [self.document])

    def test_registered_document_source_link_passes_read_only(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.check()
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_unregistered_document_fails(self):
        (self.root/self.index).write_text('# Index\n')
        with self.assertRaises(ValueError): self.check()

    def test_duplicate_registration_fails(self):
        with (self.root/self.index).open('a') as f: f.write(self.row)
        with self.assertRaises(ValueError): self.check()

    def test_missing_source_link_fails(self):
        (self.root/'src/export.py').unlink()
        with self.assertRaises(ValueError): self.check()

    def test_empty_purpose_fails(self):
        (self.root/self.index).write_text('| [Export](features/export.md) | | Editing export |\n')
        with self.assertRaises(ValueError): self.check()

    def test_outside_project_fails(self):
        (self.root/self.document).write_text('[Outside](../../../outside.md)\n')
        with self.assertRaises(ValueError): self.check()

    def test_custom_knowledge_directory(self):
        (self.root/'.harness').rename(self.root/'.custom')
        v.check(self.root, ['.custom/index.md'], ['.custom/features/export.md'])

    def test_distributed_templates_match_initialization(self):
        for name in ('feature.md', 'spec.md'):
            self.assertEqual((SKILL/'templates'/name).read_bytes(), (ROOT/'skills/harness-init/templates'/name).read_bytes())


if __name__ == '__main__': unittest.main()
