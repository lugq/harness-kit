#!/usr/bin/env python3
"""Read-only structural audit. Content and source semantics require human review."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)')


def audit(root, knowledge_dir='.harness'):
    root = Path(root).resolve()
    relative = Path(knowledge_dir)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Knowledge directory must be project-relative')
    knowledge = root/relative
    # Do not follow symlinks in any knowledge-directory component.
    cursor = root
    for part in relative.parts:
        cursor = cursor/part
        if cursor.is_symlink():
            raise ValueError('Knowledge directory is a symlink')
    if not knowledge.is_dir():
        raise ValueError('Knowledge directory does not exist')
    findings = []
    texts = {}
    def report(level, code, path, line, detail):
        findings.append(dict(level=level, code=code, file=str(path.relative_to(root)), line=line, detail=detail))
    for path in sorted(knowledge.rglob('*')):
        if path.is_symlink():
            report('error', 'symlink', path, 1, 'Not followed')
        elif path.is_file() and path.suffix == '.md':
            try:
                texts[path] = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError) as error:
                report('error', 'unreadable', path, 1, str(error))
    entry = knowledge/'index.md'
    if entry not in texts:
        report('error', 'missing_index', entry, 1, 'Missing readable index.md')
    registrations = {}
    for path, text in texts.items():
        fenced = None
        targets = []
        for number, line in enumerate(text.splitlines(), 1):
            fence = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
            if fence:
                marker = fence[1]
                if fenced is None:
                    fenced = marker
                elif marker[0] == fenced[0] and len(marker) >= len(fenced):
                    fenced = None
                continue
            if fenced:
                continue
            if re.search(r'\bTODO\b|placeholder|待填写', line, re.I):
                report('review', 'possible_placeholder', path, number, 'May be legitimate planning or an evidence gap')
            if re.search(r'^\s*\[[^\]]+\]:|\]\[[^\]]*\]|<a\b', line):
                report('review', 'manual_link_check', path, number, 'Reference/HTML links are not parsed')
            for match in LINK.finditer(line):
                target = match[1].strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                destination = path.parent/unquote(parsed.path)
                resolved = destination.resolve()
                if not resolved.is_relative_to(root):
                    report('error', 'outside_project', path, number, target)
                    continue
                cursor = root
                symlink = False
                for part in destination.relative_to(root).parts:
                    cursor = cursor/part
                    if cursor.is_symlink():
                        symlink = True
                        break
                if symlink:
                    report('error', 'symlink_link', path, number, target)
                    continue
                if not resolved.exists():
                    report('error', 'broken_link', path, number, target)
                if path.name == 'index.md' and line.lstrip().startswith('|'):
                    cells = line.strip().strip('|').split('|')
                    if match[0] in cells[0] and resolved.is_relative_to(knowledge) and resolved.suffix == '.md':
                        targets.append(resolved)
                        if len(cells) < 3 or not cells[1].strip() or not cells[2].strip():
                            report('error', 'incomplete_index_row', path, number, target)
        if path.name == 'index.md':
            registrations[path] = targets
            for target, count in Counter(targets).items():
                if count > 1:
                    report('error', 'duplicate_registration', path, 1, str(target.relative_to(root)))
    reachable = {entry} if entry in texts else set()
    pending = list(reachable)
    while pending:
        for target in registrations.get(pending.pop(), []):
            if target in texts and target not in reachable:
                reachable.add(target)
                pending.append(target)
    for path in texts:
        if path not in reachable:
            report('error', 'unreachable_document', path, 1, 'Not reachable through index tables')
    return dict(knowledge_dir=relative.as_posix(), documents=len(texts), findings=findings,
                limitations=['Content placement, source consistency and anchors require manual review',
                             'External, reference-style and complex Markdown links are not fully checked'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--knowledge-dir', default='.harness')
    args = parser.parse_args()
    try:
        result = audit(args.root, args.knowledge_dir)
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any(f['level'] == 'error' for f in result['findings']))


if __name__ == '__main__':
    raise SystemExit(main())
