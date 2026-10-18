#!/usr/bin/env python3
"""Read-only validation of scoped knowledge links and index registration."""
import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')


def local_target(root, base, target):
    parsed = urlsplit(target.strip('<>'))
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    path = (base/unquote(parsed.path)).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Missing or out-of-project link: '+target)
    return path


def check(root, indexes, documents):
    root = Path(root).resolve()
    def scoped(value):
        path = Path(value)
        if path.is_absolute():
            raise ValueError('Use project-relative paths')
        result = (root/path).resolve()
        if not result.is_relative_to(root) or not result.is_file():
            raise ValueError('Missing or out-of-project file: '+str(path))
        return result
    indexes = list(dict.fromkeys(map(scoped, indexes)))
    documents = list(dict.fromkeys(map(scoped, documents)))
    registrations = []
    for index in indexes:
        # Only data rows of a Markdown table can register a document.
        for line in index.read_text().splitlines():
            if not line.lstrip().startswith('|'):
                continue
            cells = line.strip().strip('|').split('|')
            for target in LINK.findall(cells[0]):
                path = local_target(root, index.parent, target)
                if path:
                    if len(cells) < 3 or not cells[1].strip() or not cells[2].strip():
                        raise ValueError('Index row needs purpose and reading condition')
                    registrations.append(path)
    for document in documents:
        if registrations.count(document) != 1:
            raise ValueError('Document must be registered exactly once: '+str(document))
    for file in set(indexes + documents):
        for target in LINK.findall(file.read_text()):
            local_target(root, file.parent, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--index', action='append', required=True)
    parser.add_argument('--document', action='append', required=True)
    args = parser.parse_args()
    try:
        check(args.root, args.index, args.document)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error)+'\n')
    print('Scoped knowledge links and index registration passed')


if __name__ == '__main__':
    main()
