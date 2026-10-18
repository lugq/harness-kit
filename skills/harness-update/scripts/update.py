#!/usr/bin/env python3
"""Safely update installed HarnessKit skills; never touch project files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = 'https://github.com/lugq/harness-kit.git'
NAMES = ('harness-init', 'harness-update', 'harness-spec')
STATE = '.harness-install.json'
TRANSACTION = '.harness-update-transaction'


def git(*args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
    env['GIT_SSH_COMMAND'] = 'ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes'
    command = ['git']
    if 'clone' in args and any(str(a).startswith('https://github.com/') for a in args) and shutil.which('gh'):
        # Reuse an existing GitHub CLI login without exposing tokens or changing Git config.
        command += ['-c', 'credential.helper=!gh auth git-credential']
    return subprocess.check_output([*command, *map(str, args)], env=env, timeout=120)


def hashes(root):
    if root.is_symlink():
        raise ValueError('Skill directory must not be a symlink: ' + str(root))
    result = {}
    for p in root.rglob('*'):
        if p.is_symlink():
            raise ValueError('不支持符号链接：' + str(p))
        if p.is_file() and p.name != STATE and '__pycache__' not in p.relative_to(root).parts:
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def validate(root, name):
    text = (root/'SKILL.md').read_text()
    front = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.S)
    if not front or not re.search(r'^name: ' + re.escape(name) + r'\s*$', front[1], re.M):
        raise ValueError('Skill 名称或 frontmatter 无效：' + name)
    if not re.search(r'^description: \S', front[1], re.M):
        raise ValueError('缺少 description：' + name)
    hashes(root)
    for doc in root.rglob('*.md'):
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)', doc.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            dest = (doc.parent/target.split('#')[0]).resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                raise ValueError('Skill 引用不存在或越界：' + str(doc) + ' → ' + target)
    if name == 'harness-update':
        compile((root/'scripts/update.py').read_text(), 'update.py', 'exec')
    elif name == 'harness-spec':
        for required in ('references/maintenance.md', 'templates/feature.md',
                         'templates/spec.md', 'scripts/check_docs.py'):
            if not (root/required).is_file():
                raise ValueError('缺少资源：' + required)
        compile((root/'scripts/check_docs.py').read_text(), 'check_docs.py', 'exec')
    else:
        for required in ('references/initialization.md', 'references/source-to-spec.md',
                         'templates/feature.md', 'templates/spec.md',
                         'scripts/validate_agents.py',
                         'assets/AGENTS.md', 'assets/.harness/index.md',
                         'assets/.harness/verification.md'):
            if not (root/required).is_file():
                raise ValueError('缺少资源：' + required)


def historical_match(source, name, current):
    """Recognize an unmodified standard-installer copy without trusting local metadata."""
    path = 'skills/' + name
    revisions = git('-C', source, 'log', '--format=%H', '--', path).decode().splitlines()
    for revision in revisions:
        tree = git('-C', source, 'ls-tree', '-rz', revision + ':' + path)
        candidate = {}
        for entry in tree.split(b'\0'):
            if not entry:
                continue
            meta, raw_path = entry.split(b'\t', 1)
            mode, kind, oid = meta.split()
            if kind != b'blob' or mode == b'120000':
                raise ValueError('历史包包含不支持的条目')
            candidate[raw_path.decode()] = hashlib.sha256(git('-C', source, 'cat-file', 'blob', oid.decode())).hexdigest()
        if candidate == current:
            return revision
    return None


def recover(parent):
    transaction = parent/TRANSACTION
    if not transaction.is_dir():
        raise ValueError('没有待恢复的更新')
    if (transaction/'committed').exists():
        # Both installs are complete. Partial backup cleanup must never roll one back.
        shutil.rmtree(transaction)
        return
    state_path = transaction/'transaction.json'
    absent = json.loads(state_path.read_text()).get('absent', []) if state_path.exists() else []
    # A backup exists only after the original directory was renamed successfully.
    for name in NAMES:
        backup, dst = transaction/'backup'/name, parent/name
        if backup.exists():
            if dst.exists():
                shutil.rmtree(dst)
            backup.rename(dst)
        elif name in absent and not (transaction/'new'/name).exists() and dst.exists():
            shutil.rmtree(dst)
    shutil.rmtree(transaction)


def update(source, parent, revision, check=False):
    transaction = parent/TRANSACTION
    if transaction.exists():
        raise ValueError('发现未完成事务，请先执行 --recover；备份：' + str(transaction))
    absent = []
    for name in NAMES:
        src, dst = source/'skills'/name, parent/name
        validate(src, name)
        if dst.is_symlink():
            raise ValueError('Skill directory must not be a symlink: ' + str(dst))
        if name == 'harness-spec' and not dst.exists():
            absent.append(name)
            continue
        if not dst.is_dir():
            raise ValueError('缺少已安装 Skill：' + name)
        current = hashes(dst)
        state = dst/STATE
        baseline = json.loads(state.read_text()) if state.exists() else None
        if baseline:
            if current != baseline.get('files'):
                raise ValueError('检测到本地修改或额外文件，停止更新：' + name)
        elif current != hashes(src) and not historical_match(source, name, current):
            raise ValueError('安装内容不匹配可信历史版本，停止更新：' + name)
    if check:
        print('远端版本：' + revision + '；Skills 可安全更新，缺少的 harness-spec 将新增（未写入）。')
        return
    transaction.mkdir()  # Also excludes concurrent updaters; do not auto-recover a live run.
    try:
        (transaction/'backup').mkdir()
        (transaction/'new').mkdir()
        (transaction/'transaction.json').write_text(json.dumps({'commit': revision, 'skills': NAMES, 'absent': absent}))
        for name in NAMES:
            stage = transaction/'new'/name
            shutil.copytree(source/'skills'/name, stage)
            validate(stage, name)
            (stage/STATE).write_text(json.dumps({'commit': revision, 'files': hashes(stage)}, indent=2)+'\n')
        for name in NAMES:
            if name not in absent:
                (parent/name).rename(transaction/'backup'/name)
            (transaction/'new'/name).rename(parent/name)
        (transaction/'committed').write_text(revision + '\n')
    except BaseException:
        try:
            recover(parent)
        except BaseException as error:
            raise RuntimeError('恢复失败，保留备份；请执行 --recover：' + str(transaction)) from error
        raise
    shutil.rmtree(transaction)
    print('HarnessKit Skills 已更新至 ' + revision + '；项目文件未修改。')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--recover', action='store_true')
    parser.add_argument('--repo', default=REPO, help='可信 Git 仓库 HTTPS/SSH 地址；默认官方仓库')
    args = parser.parse_args()
    parent = Path(__file__).resolve().parents[2]
    if (parent.parent/'.git').exists():
        raise ValueError('请在用户级安装中执行，不能更新开发副本')
    if args.recover:
        recover(parent)
        print('已完成事务恢复或已提交事务清理。')
        return
    if (parent/TRANSACTION).exists():
        raise ValueError('存在未完成事务；确认无更新进程运行后执行 --recover')
    with tempfile.TemporaryDirectory(prefix='harness-source-') as tmp:
        source = Path(tmp)/'repo'
        git('clone', '--quiet', '--single-branch', '--branch', 'main', args.repo, source)
        revision = git('-C', source, 'rev-parse', 'HEAD').decode().strip()
        update(source, parent, revision, args.check)


if __name__ == '__main__':
    try:
        main()
    except subprocess.SubprocessError as error:
        raise SystemExit('更新停止：' + str(error) + '\n请检查仓库读取权限、凭据或网络；可用 --repo 指定可信地址。')
    except (ValueError, OSError) as error:
        raise SystemExit('更新停止：' + str(error))
