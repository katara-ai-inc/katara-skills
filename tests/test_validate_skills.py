"""Regression coverage for the offline skill-package validator."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

VALID = """---
name: katara
description: Connect to Katara and retrieve authorized evidence.
license: Apache-2.0
metadata:
  version: "0.1.0"
---
# Katara

Use live discovery.
"""


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "skills" / "katara" / "SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text(VALID, encoding="utf-8")
        for name in ("LICENSE", "NOTICE"):
            (self.root / name).write_text(name, encoding="utf-8")
            (self.skill.parent / name).write_text(name, encoding="utf-8")
        self.scenarios = self.root / "evals" / "scenarios.json"
        self.scenarios.parent.mkdir()
        self.case = {
            "id": "first-read", "skill": "katara", "prompt": "Find our policy",
            "context": "Connected with an authorized alias",
            "must": ["Use evidence"], "must_not": ["Invent a citation"],
        }
        self.scenarios.write_text(json.dumps([self.case]), encoding="utf-8")

    def rewrite(self, old, new):
        self.skill.write_text(VALID.replace(old, new), encoding="utf-8")

    def test_valid_repository(self):
        self.assertEqual(validator.validate_repository(self.root), ([], 1, 1))

    def test_missing_frontmatter(self):
        self.rewrite("---\nname:", "name:")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_missing_closing_delimiter(self):
        self.rewrite("---\n# Katara", "# Katara")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_non_mapping_frontmatter(self):
        self.skill.write_text("---\n- item\n---\nBody", encoding="utf-8")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_duplicate_keys(self):
        self.rewrite("name: katara", "name: katara\nname: replacement")
        self.assertIn("duplicate", " ".join(validator.validate_skill(self.skill)))

    def test_malformed_yaml(self):
        self.rewrite("name: katara", "name: [")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_invalid_name(self):
        for name in ("Katara", "-katara", "katara-", "katara--service", "x" * 65):
            with self.subTest(name=name):
                self.rewrite("name: katara", "name: " + name)
                self.assertTrue(validator.validate_skill(self.skill))

    def test_directory_mismatch(self):
        self.rewrite("name: katara", "name: another-skill")
        self.assertIn("directory", " ".join(validator.validate_skill(self.skill)))

    def test_description_bounds(self):
        for description in ('""', '"   "', "x" * 1025):
            with self.subTest(description=description[:12]):
                self.rewrite("Connect to Katara and retrieve authorized evidence.", description)
                self.assertTrue(validator.validate_skill(self.skill))

    def test_metadata_values_are_strings(self):
        self.rewrite('version: "0.1.0"', "version: 1")
        self.assertIn("metadata", " ".join(validator.validate_skill(self.skill)))

    def test_compatibility_bounds(self):
        self.rewrite("license: Apache-2.0", "license: Apache-2.0\ncompatibility: " + "x" * 501)
        self.assertIn("compatibility", " ".join(validator.validate_skill(self.skill)))

    def test_wrong_license(self):
        self.rewrite("Apache-2.0", "MIT")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_missing_standalone_license(self):
        (self.skill.parent / "LICENSE").unlink()
        self.assertIn("standalone", " ".join(validator.validate_skill(self.skill)))

    def test_empty_body(self):
        self.rewrite("# Katara\n\nUse live discovery.", "")
        self.assertTrue(validator.validate_skill(self.skill))

    def test_excessive_main_skill_length(self):
        self.skill.write_text(VALID + "\n" * 501, encoding="utf-8")
        self.assertIn("500", " ".join(validator.validate_skill(self.skill)))

    def test_existing_reference(self):
        ref = self.skill.parent / "references" / "guide.md"
        ref.parent.mkdir()
        ref.write_text("# Guide", encoding="utf-8")
        self.rewrite("Use live discovery.", "[Guide](references/guide.md)")
        self.assertEqual(validator.validate_links(self.skill, self.skill.parent), [])

    def test_missing_reference(self):
        self.rewrite("Use live discovery.", "[Guide](references/missing.md)")
        self.assertIn("missing link", " ".join(validator.validate_links(self.skill, self.skill.parent)))

    def test_skill_cannot_depend_on_repository_only_file(self):
        (self.root / "README.md").write_text("# Root", encoding="utf-8")
        self.rewrite("Use live discovery.", "[Guide](../../README.md)")
        self.assertIn("escapes", " ".join(validator.validate_links(self.skill, self.skill.parent)))

    def test_remote_and_fragment_links(self):
        self.rewrite("Use live discovery.", "[Site](https://katara.ai) [Email](mailto:support@katara.ai) [Here](#katara)")
        self.assertEqual(validator.validate_links(self.skill, self.skill.parent), [])

    def test_insecure_url_rejected(self):
        self.rewrite("Use live discovery.", "[Site](http://katara.ai)")
        self.assertTrue(validator.validate_links(self.skill, self.skill.parent))

    def test_symlink_escape_rejected(self):
        (self.skill.parent / "outside.md").symlink_to(self.root / "NOTICE")
        self.rewrite("Use live discovery.", "[Outside](outside.md)")
        self.assertIn("escapes", " ".join(validator.validate_links(self.skill, self.skill.parent)))

    def test_repository_requires_skills(self):
        self.skill.unlink()
        self.assertIn("no skills", " ".join(validator.validate_repository(self.root)[0]))

    def test_license_copy_must_match(self):
        (self.skill.parent / "LICENSE").write_text("different", encoding="utf-8")
        self.assertIn("must match", " ".join(validator.validate_repository(self.root)[0]))

    def test_duplicate_scenarios_rejected(self):
        self.scenarios.write_text(json.dumps([self.case, self.case]), encoding="utf-8")
        self.assertIn("duplicate", " ".join(validator.validate_scenarios(self.scenarios, {"katara"})))

    def test_unknown_skill_scenario_rejected(self):
        self.case["skill"] = "unknown"
        self.scenarios.write_text(json.dumps([self.case]), encoding="utf-8")
        self.assertTrue(validator.validate_scenarios(self.scenarios, {"katara"}))

    def test_malformed_scenarios_rejected(self):
        for data in ([], {}, [None], [{"id": "incomplete"}]):
            with self.subTest(data=data):
                self.scenarios.write_text(json.dumps(data), encoding="utf-8")
                self.assertTrue(validator.validate_scenarios(self.scenarios, {"katara"}))

    def test_evaluation_criteria_required(self):
        self.case["must"] = []
        self.scenarios.write_text(json.dumps([self.case]), encoding="utf-8")
        self.assertTrue(validator.validate_scenarios(self.scenarios, {"katara"}))


if __name__ == "__main__":
    unittest.main()
