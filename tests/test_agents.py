import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/harness-init'
spec = importlib.util.spec_from_file_location('agents_validator', SKILL/'scripts/validate_agents.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class AgentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.before = Path(self.tmp.name)/'before.md'
        self.after = Path(self.tmp.name)/'AGENTS.md'
        self.template = (SKILL/'assets/AGENTS.md').read_bytes()
        self.body = self.template.split(b'\n', 1)[1]

    def test_new_exact_template(self):
        self.after.write_bytes(self.template)
        v.validate(self.after)

    def test_new_paraphrase_or_extra_rule_rejected(self):
        self.after.write_bytes(self.template+b'\n- Temporary execution rule\n')
        with self.assertRaises(ValueError):
            v.validate(self.after)

    def test_existing_preserved_with_template_additions(self):
        original = b'# Existing project\n\n- Keep custom user policy.\n'
        self.before.write_bytes(original)
        self.after.write_bytes(original+b'\n'+self.body)
        v.validate(self.after, self.before)
        self.assertTrue(self.after.read_bytes().startswith(original))

    def test_existing_without_final_newline(self):
        original = b'# Existing project'
        self.before.write_bytes(original)
        self.after.write_bytes(original+b'\n'+self.body)
        v.validate(self.after, self.before)

    def test_preserved_entry_mode_unchanged(self):
        self.before.write_bytes(b'# Project\r\nCustom rules\r\n')
        self.after.write_bytes(self.before.read_bytes())
        v.validate(self.after, self.before)

    def test_existing_rule_rewrite_rejected(self):
        self.before.write_bytes(b'# Project\n- Keep custom policy.\n')
        self.after.write_bytes(b'# Project\n'+self.body)
        with self.assertRaises(ValueError):
            v.validate(self.after, self.before)

    def test_transient_rule_rejected_in_merge(self):
        self.before.write_bytes(b'# Project\n')
        self.after.write_bytes(self.before.read_bytes()+self.body+b'\n- Do not read legacy memory this run.\n')
        with self.assertRaises(ValueError):
            v.validate(self.after, self.before)

    def test_explicit_custom_path_only(self):
        self.after.write_bytes(self.template.replace(b'.harness/index.md', b'.harness-generated/index.md'))
        v.validate(self.after, knowledge_dir='.harness-generated')
        with self.assertRaises(ValueError):
            v.validate(self.after)

    def test_unsafe_directory_rejected(self):
        self.after.write_bytes(self.template)
        for directory in ('../outside', '/tmp/outside', ''):
            with self.assertRaises(ValueError):
                v.validate(self.after, knowledge_dir=directory)

    def test_duplicate_added_template_rules_rejected(self):
        self.before.write_bytes(b'# Project\n')
        self.after.write_bytes(self.before.read_bytes()+self.body+self.body)
        with self.assertRaises(ValueError):
            v.validate(self.after, self.before)


if __name__ == '__main__':
    unittest.main()
