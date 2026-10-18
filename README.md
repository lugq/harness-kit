# HarnessKit

使用随 Skill 分发的规范和模板，为项目创建或合并 AGENTS.md 与 knowledge 知识入口。

GitHub 仓库是版本来源。[Codex Harness 工程实践 Page](https://chatgpt.com/space/page_bd948ce9c828819197f84cee0c3dde33) 仅作为阅读映射。运行时使用当前安装版本，不读取 Page，无需 Pages 工具或权限。

## 安装

仓库目前为私有，安装环境需要有仓库读取权限。在 Codex 中发送：

```text
使用 $skill-installer，从 GitHub 仓库 lugq/harness-kit 安装 Skill。
Skill 位于仓库根目录，分支 main，安装名称 harness-kit。
```

安装后下一轮输入 `$harness-kit` 检查是否可用；未显示时重新打开会话或重启客户端。

也可手动安装。以下 macOS / Linux 命令需要 Git 与有私有仓库读取权限的 GitHub SSH 凭据：

```bash
mkdir -p ~/.agents/skills
git clone git@github.com:lugq/harness-kit.git ~/.agents/skills/harness-kit
```

Windows 可克隆到用户目录下 `.agents/skills/harness-kit`。目录已存在时先检查，不直接覆盖。安装会在运行环境保存 Skill 副本，GitHub 不会自动将个人 Skill 同步至其他机器或云端任务。

## 使用

在 Codex 中打开目标项目，发送：

```text
使用 $harness-kit init 初始化当前项目。
保留已有 AGENTS.md、知识文档和未提交修改，完成后报告创建、修改和复用的文件。
```

空项目直接复制完整内置模板，不重新生成：

```text
项目根目录/
├── AGENTS.md
└── knowledge/
    └── index.md
```

已有项目只检查目录和目标文件是否存在；已有记忆、规范及其他文档保持原样，不主动读取、引用、迁移或修改。新知识依据代码、构建配置和验证证据建立，其他资料仅在用户明确指定时参考。AGENTS.md 等适用项目指令仍须遵循。已有知识目标发生冲突时，先确认合并授权或新目录，不自动沿用旧知识。重复执行不重复追加。架构框架、开发规范和功能与决策指南默认创建；具体功能 Spec 与决策记录按需创建，未知事实保留待确认。不会生成业务代码、安装依赖或自动提交推送。

## 文件结构

```text
harness-kit/
├── SKILL.md
├── agents/openai.yaml
├── references/initialization.md   # 初始化规范
├── assets/AGENTS.md              # 项目指令模板
├── assets/knowledge/index.md     # 带查询表格的知识索引及完整框架
└── README.md
```

## 维护和更新

修改仓库中的规范或模板，经校验后提交，并同步 Page 与文件浏览示例。Page 是人工同步的阅读映射，不是自动同步编辑器；在 Page 提出修改时，需要明确同步到仓库及安装副本。

手动克隆安装可在检查本地改动后更新：

```bash
git -C ~/.agents/skills/harness-kit status --short
git -C ~/.agents/skills/harness-kit pull --ff-only
```

存在改动时先合并差异，不强制重置。通过安装器安装的副本，让 Codex 检查后更新，不假定安装器会覆盖现有目录。

更新安装副本后，下次初始化采用新版本。已初始化项目独立维护，不自动覆盖；需要明确提出迁移或合并请求。

## 常见问题

- 找不到 Skill：核对安装位置，重新打开会话或重启客户端。
- 私有仓库下载失败：检查安装环境的 GitHub 身份与仓库权限，不要把令牌粘贴到聊天或提交到仓库。
- 无法访问 Page：不影响初始化，规范与模板均已包含在 Skill 中。
- 云端任务不可用：需在云端运行环境提供 Skill，本机安装不会自动同步。

已进行 Skill 格式校验及模板一致性检查，尚未在其他项目完整试运行。

## 更新命令

在 Codex 中发送：

```text
$harness-kit update
```

该命令更新 Skill 自身，不修改项目中的 AGENTS.md 或 knowledge。需要 Git 和具有私有仓库读取权限的 GitHub SSH 凭据；不会要求你在聊天里提供令牌。

更新脚本先拉取 main 到临时目录，再核对安装基线。有本地修改或文件冲突时停止；缺少基线的旧安装若与远端不同，也会停止并要求核对，不强制覆盖。更新失败会尝试恢复备份。下次调用使用新版本，必要时重新打开会话。

仅检查可请求 Codex 执行 `scripts/update.py --check`。这是 Skill 内的命令路由，不是系统独立命令。Git 克隆安装会检查本地修改、远端和分支，再执行快进更新。
