#!/usr/bin/env python3
"""Update this installed skill from its GitHub repository."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

REPO = 'git@github.com:lugq/harness-init.git'
STATE = '.harness-install.json'

def files(root):
    return {str(p.relative_to(root)): p for p in root.rglob('*')
            if p.is_file() and '.git' not in p.relative_to(root).parts
            and '__pycache__' not in p.relative_to(root).parts
            and p.name != STATE}

def hashes(root):
    return {name: hashlib.sha256(p.read_bytes()).hexdigest()
            for name, p in files(root).items()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check without writing')
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1]
    if (target / '.git').exists():
        raise SystemExit('这是 Git 工作副本，请检查改动后使用 git pull --ff-only 更新。')
    state_path = target / STATE
    baseline = json.loads(state_path.read_text()) if state_path.exists() else None
    with tempfile.TemporaryDirectory(prefix='harness-update-') as tmp:
        source = Path(tmp) / 'source'
        subprocess.run(['git', 'clone', '--quiet', '--depth', '1', '--branch', 'main', REPO, str(source)], check=True)
        revision = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        incoming = hashes(source)
        current = hashes(target)
        if baseline:
            changed = [p for p, h in baseline['files'].items() if current.get(p) != h]
            collisions = [p for p in incoming if p in current and p not in baseline['files']]
            if changed or collisions:
                raise SystemExit('检测到本地修改或文件冲突，停止更新：' + ', '.join(sorted(set(changed + collisions))))
        elif current != incoming:
            raise SystemExit('缺少安装基线且文件与远端不同，无法判断本地修改。请先备份并由 Codex 核对后更新。')
        if args.check:
            print('远端版本：' + revision)
            print('可安全更新。' if current != incoming else '文件已是最新版本。')
            return
        backup = Path(tmp) / 'backup'
        shutil.copytree(target, backup)
        try:
            for name in (baseline or {'files': {}})['files']:
                if name not in incoming:
                    (target / name).unlink(missing_ok=True)
            for name, p in files(source).items():
                dest = target / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
            state_path.write_text(json.dumps({'commit': revision, 'files': incoming}, ensure_ascii=False, indent=2) + '\n')
        except Exception:
            for name in files(target):
                if name not in files(backup):
                    (target / name).unlink()
            shutil.copytree(backup, target, dirs_exist_ok=True)
            raise
        print('harness-init 已更新至 ' + revision)
        print('下次调用使用更新后的 Skill；项目文件未修改。')

if __name__ == '__main__':
    main()
