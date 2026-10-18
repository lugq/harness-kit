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

有代码的项目先读取源码、构建配置与测试，生成真实架构、技术约束和核心功能 Spec；模板仅规定结构，关键结论附源码依据。未知项具体列出，未运行验收不能标为通过。

真正没有代码的项目才复制以下基础框架：

```text
AGENTS.md
.harness/
├── index.md
├── verification.md
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

需要 Python 3.9+、Git 和仓库读取权限。默认通过 HTTPS 使用现有 Git 凭据；有 GitHub CLI 时也可复用已有登录，不改变全局 Git 配置。禁用交互提示并设置超时；也可用 `--repo git@github.com:lugq/harness-kit.git` 选择已配置的 SSH。私有仓库需先配置对应凭据，下载失败不会修改安装。

标准安装无需额外步骤：缺少版本基线时，从可信仓库 main 历史核验旧安装完整文件哈希，匹配后正常升级并建立基线。本地修改、额外文件或无法识别的安装会停止更新，不强制覆盖。

两个新版目录先暂存并校验，再在同一文件系统中替换，持久备份保留至替换完成。普通异常和可捕获中断会回滚；强制终止后，下次运行会提示未完成事务。确认没有更新进程运行后，给脚本加 `--recover` 恢复旧安装；恢复失败仍保留备份路径。双目录替换不是单次原子操作，恢复前不要调用两个 Skill。断电造成的磁盘损坏不在恢复保证内。

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

## 从代码生成 Spec 的质量标准

初始化采用“代码地图 → 实际主题 → 证据清单 → 具体契约 → 完成检查”。模板允许按代码边界调整；重要规则附源码或测试依据，接口写清签名、字段和失败边界。删除不适用章节与填空提示，确有缺口则列具体未确认事项。未经指定不读取旧知识资料，不要求安装额外分析工具。

方法参考 [Trellis Spec Bootstrap](https://github.com/mindfold-ai/Trellis/tree/main/.agents/skills/trellis-spec-bootstrap)，流程按 HarnessKit 范围独立整理。

## 文档模板与质量检查

Skill 内 templates/feature.md 和 templates/spec.md 分别约定功能闭环与技术契约内容；它们是写作骨架，不是直接复制的项目成品。跨边界数据需要字段、类型、默认值、转换和调用两端的完整对照。关键结论就近关联源码；检查既从功能清单查遗漏，也从文档反查实际代码。共同规则保留路径例外，执行记录集中在 verification.md。文件按主题命名，不加重复的 feature-/spec- 前缀。

## 维护验证

在仓库根目录执行 `python3 -m unittest discover -s tests -v`，覆盖无基线首次升级、本地修改保护、包校验、双目录失败恢复与中断残留恢复。两个 Skill 还需通过 skill-creator 的 quick_validate.py。已有知识目录默认只盘点；独立生成文档不代表授权切换原入口。
