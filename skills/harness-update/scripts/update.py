#!/usr/bin/env python3
"""Update the two installed HarnessKit skills, preserving local edits."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

REPO = 'git@github.com:lugq/harness-kit.git'
NAMES = ('harness-init', 'harness-update')
STATE = '.harness-install.json'

def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()
            and p.name != STATE and '__pycache__' not in p.relative_to(root).parts}

def update(source, parent, revision, check=False):
    for name in NAMES:
        src, dst = source/'skills'/name, parent/name
        if not (src/'SKILL.md').is_file() or not dst.is_dir():
            raise SystemExit('缺少 Skill，先安装两个入口：' + name)
        incoming, current = hashes(src), hashes(dst)
        state = dst/STATE
        baseline = json.loads(state.read_text()) if state.exists() else None
        if baseline and current != baseline['files']:
            raise SystemExit('检测到本地修改或额外文件，停止更新：' + name)
        if not baseline and current != incoming:
            raise SystemExit('缺少安装基线且内容不同，停止更新：' + name)
    if check:
        print('远端版本：' + revision + '；两个 Skill 均可安全更新。')
        return
    with tempfile.TemporaryDirectory(prefix='harness-backup-') as tmp:
        backup = Path(tmp)
        for name in NAMES:
            shutil.copytree(parent/name, backup/name)
        try:
            for name in NAMES:
                dst = parent/name
                shutil.rmtree(dst)
                shutil.copytree(source/'skills'/name, dst)
                (dst/STATE).write_text(json.dumps({'commit': revision, 'files': hashes(dst)}, ensure_ascii=False, indent=2)+'\n')
        except Exception:
            for name in NAMES:
                if (parent/name).exists():
                    shutil.rmtree(parent/name)
                shutil.copytree(backup/name, parent/name)
            raise
    print('两个 Skill 已更新至 ' + revision + '；项目文件未修改。')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    parent = Path(__file__).resolve().parents[2]
    if (parent.parent/'.git').exists():
        raise SystemExit('当前为仓库开发副本，请在用户级安装中执行更新。')
    with tempfile.TemporaryDirectory(prefix='harness-source-') as tmp:
        source = Path(tmp)/'repo'
        subprocess.run(['git','clone','--quiet','--depth','1','--branch','main',REPO,str(source)],check=True)
        revision = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        update(source,parent,revision,args.check)

if __name__ == '__main__':
    main()
