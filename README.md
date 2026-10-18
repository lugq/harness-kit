# HarnessKit

为编程 Agent 提供可复用的项目指令与知识框架。仓库包含两个独立 Skill，可在 Codex 的 `$` 菜单分别选择。

| Skill | 用途 |
| --- | --- |
| `$harness-init` | 初始化项目 AGENTS.md 与完整 .harness 框架 |
| `$harness-update` | 更新本机安装的两个 Skill，不修改项目文件 |

## 安装

仓库目前为私有，安装环境需要有 GitHub 仓库读取权限。在 Codex 中发送：

```text
使用 $skill-installer，从 lugq/harness-kit 的 main 分支安装以下两个 Skill：
skills/harness-init
skills/harness-update
```

安装后下一轮输入 `$harness-`，应看到 Harness Init 和 Harness Update 两个入口。若未出现，重新打开会话或重启客户端。安装会在执行环境保存文件，不会自动同步到其他机器或云端。

## 使用

打开目标项目后发送：

```text
$harness-init 初始化当前项目，保留已有内容与未提交改动。
```

空项目直接复制内置六份文件：

```text
AGENTS.md
.harness/
├── index.md
├── architecture.md
├── specs/development.md
├── features/README.md
└── decisions/README.md
```

已有记忆、规范及其他文档保持原样，不主动读取、引用、迁移或修改；新知识以代码、构建配置和验证证据为依据，其他资料仅在用户明确指定时参考。适用 AGENTS.md 仍须遵循。同名知识目录冲突时先确认处理方式。初始化不生成业务代码、不安装依赖、不自动提交推送。

## 更新

```text
$harness-update
```

需要 Git 和仓库读取权限。更新脚本检查两个安装目录的基线；本地修改或额外文件会阻止更新。初次安装未建立基线时，文件必须与远端完全一致才允许更新。更新前备份，普通写入异常时恢复；中断或断电不保证自动恢复。

仅检查可请求执行更新脚本并加 `--check`。更新仅作用于 Skills，不覆盖已初始化项目。GitHub 更新不会自动生效，需显式调用更新。

## 结构与维护

```text
skills/
├── harness-init/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/initialization.md
│   └── assets/
└── harness-update/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── scripts/update.py
```

规范和模板随仓库版本分发，运行不依赖在线 Page。[Page](https://chatgpt.com/space/page_bd948ce9c828819197f84cee0c3dde33) 仅为阅读映射，修改仓库后人工同步。

旧版单入口 harness-kit 安装需先核对本地改动，再迁移为两个独立目录并移出旧入口，避免重复菜单。缺少安装基线且存在差异时，不强制覆盖。
