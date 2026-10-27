"""Builds kit/data.json for the NMI kit (kit/index.html) from the curriculum folder.

Reads, per subject folder in curriculum/:
  grade*/<N>units.md             the topics of a level (subjects, grades and levels come from the folders)
  bagrut_patterns.md             only the form sections of the level, the general rules and "how the tutor writes a question"
  grade*/examples/<N>units.md    the example bank (one Bagrut-style question per topic)
and kit/base_prompt.txt. A level whose topics do not all have an example is marked "experimental".

    python tools/build_kit.py            writes kit/data.json
    python tools/build_kit.py --check    exits 1 when kit/data.json is out of date (no write)
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / 'curriculum'
KIT = ROOT / 'kit'
OUTPUT = KIT / 'data.json'
BASE_PROMPT = KIT / 'base_prompt.txt'

TOPIC_HEADING = re.compile(r'^(#{3,4}) (m\d+-\d+-\d+) (.+?)\s*$')
HEBREW = re.compile(r'\s*\([^()]*[֐-׿][^()]*\)')
# the English name is the last thing of a title line, between square brackets: `#### m10-3-07 مسارات (מסלולים) [Paths]`
ENGLISH = re.compile(r'\s*\[([^\[\]]+)\]\s*$')
LEVEL_FILE = re.compile(r'^(\d+)units\.md$')
GRADE_FOLDER = re.compile(r'^grade(\d+)$')
GRADE_TITLE = re.compile(r'الصف ([^،\n]+)')
SUBJECT_TITLE = re.compile(r'^# ([^،\n]+)،')
SECTION_NOTES = ('تعليمات للمدرّس عن هذا الدليل', 'الامتحان')
SKIPPED_SECTIONS = ('المواضيع بالترتيب', 'نصائح تدريس من الوزارة')


def read(path):
    return path.read_text(encoding='utf-8').replace('\r\n', '\n')


def sections(text):
    """[(heading, body)] for the `## ` sections; a body runs to the next heading of level 1 or 2."""
    marks = [(m.start(), m.end(), m.group(1).strip()) for m in re.finditer(r'^## (.+)$', text, re.M)]
    stops = [m.start() for m in re.finditer(r'^#{1,2} ', text, re.M)]
    out = []
    for start, end, heading in marks:
        after = [stop for stop in stops if stop > start]
        out.append((heading, text[end:after[0] if after else len(text)].strip()))
    return out


def split_english(title):
    """(the title without its English name, the English name or None)"""
    found = ENGLISH.search(title)
    return (ENGLISH.sub('', title).strip(), found.group(1).strip()) if found else (title, None)


def parse_topics(text):
    """Topics of a level file: id, title, the group (cluster) heading above it, and the body text."""
    lines = text.split('\n')
    topics, group, group_full, group_en, current = [], None, None, None, None
    for line in lines:
        heading = re.match(r'^(#{2,4}) (.+?)\s*$', line)
        if heading:
            if current:
                topics.append(current)
                current = None
            match = TOPIC_HEADING.match(line)
            if match:
                full, english = split_english(match.group(3))  # `full` has no English name: the prompt is Arabic (with the Hebrew term)
                current = {'id': match.group(2), 'title': HEBREW.sub('', full).strip(), 'title_full': full, 'title_en': english, 'group': group,
                           'group_full': group_full, 'group_en': group_en, 'body': []}
            elif heading.group(1) == '###':
                text, group_en = split_english(heading.group(2))
                group = HEBREW.sub('', text).strip()
                group_full = text  # with the Hebrew term, for the pages in Hebrew and English
            elif heading.group(1) == '##' and heading.group(2) in SKIPPED_SECTIONS + SECTION_NOTES:
                group = group_full = group_en = None
            continue
        if current is not None:
            current['body'].append(line)
    if current:
        topics.append(current)
    for topic in topics:
        topic['text'] = '\n'.join(topic.pop('body')).strip()
    return topics


def parse_examples(path):
    """{topic id: example text} from an examples file (one `## <id> <title>` section per topic)."""
    found = {}
    if not path.is_file():
        return found
    for heading, body in sections(read(path)):
        match = re.match(r'^(m\d+-\d+-\d+)\b', heading)
        if match and body:
            found[match.group(1)] = body
    return found


def parse_patterns(path):
    """The Bagrut patterns split into the parts the kit mixes per level."""
    if not path.is_file():
        return None
    text = read(path)
    title = re.search(r'^# (.+)$', text, re.M).group(1).strip()
    patterns = {'title': title, 'forms': None, 'general': None, 'howto': None, 'levels': {}}
    for heading, body in sections(text):
        full = f'## {heading}\n\n{body}'
        units = re.match(r'^(\d) وحدات', heading)
        grade = re.search(r'الصف ([^:()]+?):', heading)
        if heading.startswith('أرقام الاستمارات'):
            patterns['forms'] = full
        elif heading.startswith('قواعد عامة'):
            patterns['general'] = full
        elif heading.startswith('كيف المدرّس'):
            patterns['howto'] = full
        elif units:
            patterns['levels'].setdefault(units.group(1), []).append({'grade': grade.group(1).strip() if grade else None, 'text': full})
    return patterns


def parse_level(path, examples):
    text = read(path)
    units = int(LEVEL_FILE.match(path.name).group(1))
    notes = []
    for heading, body in sections(text):
        if heading in SKIPPED_SECTIONS:
            continue
        notes.append(f'## {heading}\n\n{body}')
    topics = parse_topics(text)
    for topic in topics:
        topic['example'] = examples.get(topic['id'])
    experimental = not topics or any(topic['example'] is None for topic in topics)
    return {'units': units, 'title': re.search(r'^# (.+)$', text, re.M).group(1).strip(), 'notes': '\n\n'.join(notes),
            'experimental': experimental, 'topics': topics}


def subject_name(subject_dir):
    for path in sorted(subject_dir.glob('grade*/*units.md')):
        match = SUBJECT_TITLE.match(read(path))
        if match:
            return match.group(1).strip()
    return subject_dir.name


def build(curriculum=CURRICULUM, base_prompt=BASE_PROMPT):
    subjects = []
    for subject_dir in sorted(p for p in curriculum.iterdir() if p.is_dir()):
        grade_dirs = sorted((p for p in subject_dir.iterdir() if p.is_dir() and GRADE_FOLDER.match(p.name)),
                            key=lambda p: int(GRADE_FOLDER.match(p.name).group(1)))
        if not grade_dirs:
            continue
        grades = []
        for grade_dir in grade_dirs:
            levels = []
            for path in sorted(grade_dir.glob('*units.md'), key=lambda p: int(LEVEL_FILE.match(p.name).group(1)) if LEVEL_FILE.match(p.name) else 0):
                if LEVEL_FILE.match(path.name):
                    levels.append(parse_level(path, parse_examples(grade_dir / 'examples' / path.name)))
            if not levels:
                continue
            grade_number = int(GRADE_FOLDER.match(grade_dir.name).group(1))
            named = GRADE_TITLE.search(levels[0]['title'])
            grades.append({'id': grade_number, 'name': named.group(1).strip() if named else f'الصف {grade_number}', 'levels': levels})
        if grades:
            subjects.append({'id': subject_dir.name, 'name': subject_name(subject_dir), 'grades': grades,
                             'patterns': parse_patterns(subject_dir / 'bagrut_patterns.md')})
    return {'version': 1, 'base_prompt': read(base_prompt).strip(), 'subjects': subjects}


def render(data):
    return json.dumps(data, ensure_ascii=False, indent=1) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description='Build kit/data.json from the curriculum folder.')
    parser.add_argument('--check', action='store_true', help='fail if kit/data.json is out of date; write nothing')
    args = parser.parse_args(argv)
    text = render(build())
    if args.check:
        current = OUTPUT.read_text(encoding='utf-8') if OUTPUT.is_file() else ''
        if current != text:
            print('kit/data.json is out of date: run python tools/build_kit.py', file=sys.stderr)
            return 1
        print('kit/data.json is up to date')
        return 0
    OUTPUT.write_text(text, encoding='utf-8', newline='\n')
    levels = [(s['id'], g['id'], l['units'], l['experimental']) for s in build()['subjects'] for g in s['grades'] for l in g['levels']]
    print(f'wrote {OUTPUT.relative_to(ROOT)} ({len(text)} characters, {len(levels)} levels, '
          f'{sum(1 for l in levels if l[3])} experimental)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
