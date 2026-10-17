"""Validate skill metadata, resources, eval fixtures and unchanged backend bytes."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import sys
import subprocess

# The bundled validator reads with the process default encoding. Windows may
# default to Hebrew cp1255; use UTF-8 for bilingual Markdown without editing it.
if __name__ == "__main__" and not sys.flags.utf8_mode:
    raise SystemExit(subprocess.call([sys.executable, "-X", "utf8", "-B", __file__]))

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".cache/python-tools"))
try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML tooling is missing from .cache/python-tools; see docs/SKILLS_SETUP.md.")


def validate():
    errors = []
    skills = sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))
    official_validator = Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
    validator = runpy.run_path(str(official_validator))["validate_skill"] if official_validator.exists() else None
    names = set()
    for file in skills:
        text = file.read_text(encoding="utf-8")
        try:
            metadata = yaml.safe_load(text.split("---", 2)[1])
            name, description = metadata["name"], metadata["description"]
            assert name == file.parent.name and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
            assert isinstance(description, str) and 0 < len(description) <= 1024
            assert name not in names
            names.add(name)
        except (ValueError, IndexError, KeyError, TypeError, AssertionError, yaml.YAMLError) as error:
            errors.append(f"{file.relative_to(ROOT)}: metadata invalid ({type(error).__name__})")
        if validator:
            valid, message = validator(file.parent)
            if not valid:
                errors.append(f"{file.parent.name}: {message}")
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        for reference in re.findall(r"\]\(([^)]+)\)", prose):
            if "://" in reference or reference.startswith("#"):
                continue
            target = (file.parent / reference.split("#")[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f"{file.parent.name}: broken/out-of-project reference {reference}")
    assert len(skills) == 12, f"Expected 12 skills, found {len(skills)}"
    manifest = ROOT / "docs/skill-sources.json"
    if manifest.exists():
        for skill in json.loads(manifest.read_text(encoding="utf-8")):
            for item in skill["files"]:
                file = ROOT / ".agents/skills" / skill["name"] / item["path"]
                if hashlib.sha256(file.read_bytes()).hexdigest() != item["installed_sha256"]:
                    errors.append(f"Installed Skill differs from reviewed manifest: {file.relative_to(ROOT)}")
    cases = json.loads((ROOT / "tests/evals/tutor_cases.json").read_text(encoding="utf-8"))
    assert len({case['id'] for case in cases}) == len(cases)
    for case in cases:
        assert case['language'] in {'ar', 'en'}
        assert case['intent'] in {'question', 'answer', 'hint', 'confusion', 'ambiguous'}
        assert isinstance(case['is_attempt'], bool)
        assert case['enrolled_grade'] in {9, 10, 11, 12}
        assert case['evaluation_status'] in {'unevaluated', 'pass', 'fail'}
        if case['evaluation_status'] != 'unevaluated':
            assert case.get('observed_reply') and case.get('rubric_evidence')
        assert isinstance(case['provenance'], str) and case['provenance']
        if case['intent'] != 'answer':
            assert case['is_attempt'] is False
    baseline = ROOT / ".cache/backend-baseline.json"
    change_record = ROOT / "docs/backend-integration-changes.json"
    authorized = json.loads(change_record.read_text(encoding="utf-8")) if change_record.exists() else {}
    accepted_changes = []
    if baseline.exists():
        for relative, expected in json.loads(baseline.read_text(encoding="utf-8")).items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                record = authorized.get(relative, {})
                if record.get("previous_sha256") == expected and record.get("authorized_sha256") == actual:
                    accepted_changes.append(relative)
                else:
                    errors.append(f"Backend changed without a matching reviewed integration record: {relative}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(skills)} unique Skills; metadata and links valid; {len(cases)} evaluation cases valid.")
    if accepted_changes:
        print("PASS: recorded integration changes match: " + ", ".join(accepted_changes) + "; other baseline files unchanged.")
    else:
        print("PASS: backend source hashes unchanged." if baseline.exists() else "Backend hash baseline unavailable; use Git diff.")
    print("Official quick_validate: " + ("passed for every Skill" if validator else "unavailable; local YAML checks used"))
    print("Discovery location verified structurally. Open Codex in NMI and use /skills on the next turn.")


if __name__ == "__main__":
    validate()
