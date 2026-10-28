#!/usr/bin/env python3
"""Validate template-only additions without rewriting project instructions."""
import argparse
from collections import Counter
import difflib
from pathlib import Path, PurePosixPath


def validate(after, original=None, knowledge_dir='.harness'):
    directory = PurePosixPath(knowledge_dir)
    if directory.is_absolute() or '..' in directory.parts or not directory.parts or '\\' in knowledge_dir or '\n' in knowledge_dir or '\r' in knowledge_dir:
        raise ValueError('Knowledge directory must be a project-relative path')
    template = (Path(__file__).resolve().parents[1]/'assets/AGENTS.md').read_bytes()
    template = template.replace(b'.harness/index.md', (directory.as_posix()+'/index.md').encode())
    current = Path(after).read_bytes()
    if original is None:
        if current != template:
            raise ValueError('New AGENTS.md must match the complete template exactly')
        return
    before = Path(original).read_bytes()
    if before and not before.endswith((b'\n', b'\r')) and current.startswith(before+b'\n'):
        # Appending a separator leaves all original bytes intact.
        before += b'\n'
    old_lines, new_lines = before.splitlines(keepends=True), current.splitlines(keepends=True)
    allowed = Counter(line.rstrip(b'\r\n') for line in template.splitlines(keepends=True) if line.strip())
    # Existing document owns its title; appending another H1 is not a merge.
    allowed.pop(template.splitlines()[0], None)
    additions = Counter()
    added_positions = []
    for tag, i, j, a, b in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag in ('delete', 'replace'):
            raise ValueError('Existing AGENTS.md content or line endings were changed')
        if tag == 'insert':
            for line in new_lines[a:b]:
                if line.rstrip(b'\r\n'):
                    additions[line.rstrip(b'\r\n')] += 1
            added_positions.extend(k for k in range(a, b) if new_lines[k].strip())
    if additions - allowed:
        raise ValueError('Added text is outside the template or repeats template rules')
    if added_positions:
        start = b'<!-- harness-kit:project-rules:start -->'
        end = b'<!-- harness-kit:project-rules:end -->'
        lines = [line.rstrip(b'\r\n') for line in new_lines]
        if lines.count(start) != 1 or lines.count(end) != 1:
            raise ValueError('Template additions require exactly one start/end marker pair')
        lower, upper = lines.index(start), lines.index(end)
        if lower >= upper or any(not lower <= k <= upper for k in added_positions):
            raise ValueError('Template additions must be within the project-rules markers')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('after', type=Path)
    parser.add_argument('--original', type=Path)
    parser.add_argument('--knowledge-dir', default='.harness')
    args = parser.parse_args()
    try:
        validate(args.after, args.original, args.knowledge_dir)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error)+'\n')
    print('AGENTS.md template validation passed')


if __name__ == '__main__':
    main()
