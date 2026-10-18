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
    for tag, i, j, a, b in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag in ('delete', 'replace'):
            raise ValueError('Existing AGENTS.md content or line endings were changed')
        if tag == 'insert':
            for line in new_lines[a:b]:
                if line.rstrip(b'\r\n'):
                    additions[line.rstrip(b'\r\n')] += 1
    if additions - allowed:
        raise ValueError('Added text is outside the template or repeats template rules')


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
