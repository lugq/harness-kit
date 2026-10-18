# harness-init

依据 [Codex Harness 工程实践 Page](https://chatgpt.com/space/page_bd948ce9c828819197f84cee0c3dde33) 的最新初始化规范，为项目创建或合并 `AGENTS.md` 与知识入口。

规范和模板在 Page 中维护；本仓库只保存 Skill 的执行流程，不复制第二份规范。

## 使用前提

- Codex 所在环境能够读取目标项目并写入文件。
- 当前环境提供可读取该 Page 的工具，且当前账号有访问权限。仅能在浏览器打开链接，不代表 Codex 已具备 Page 读取工具。
- 仓库目前为私有，安装时使用的 GitHub 身份需要拥有仓库读取权限。

安装 Skill 不会自动连接 Pages、授予 Page 权限或实现跨设备同步。无法读取最新规范时，Skill 会停止写入；也可以由你明确提供本次采用的最新规范正文。

## 安装

### 推荐：让 Codex 安装

在具备 Skill 安装能力的 Codex 聊天中发送：

```text
使用 $skill-installer，从 GitHub 仓库 lugq/harness-init 安装 Skill。
Skill 位于仓库根目录，分支 main，安装名称 harness-init。
```

私有仓库需要安装环境已有可用的 Git 凭据或适当的 GitHub 授权。不要把访问令牌粘贴到聊天或写进本仓库。

安装完成后，在下一轮输入 `$harness-init` 检查是否可用；若未显示，重新打开会话或重启客户端。

### 可选：手动安装到个人目录

下面是 macOS / Linux 的示例。需已安装 Git，并配置具有该私有仓库读取权限的 GitHub SSH 凭据：

```bash
mkdir -p ~/.agents/skills
git clone git@github.com:lugq/harness-init.git ~/.agents/skills/harness-init
```

如果目标目录已存在，先检查它是已有安装还是其他内容，不要直接覆盖。Windows 用户可将仓库克隆到用户目录下的 `.agents/skills/harness-init`。

这会在执行安装的机器上保存一份 Skill。GitHub 是版本维护来源，不是 Codex 自动加载的云端个人 Skill 存储。如果不希望安装到本机，可继续在目标项目聊天中直接引用 Page 的“项目初始化规范”。

## 使用

在 Codex 中打开目标项目，并确保当前聊天绑定的是该项目，再发送：

```text
使用 $harness-init，按配置 Page 的最新“项目初始化规范”初始化当前项目。
保留已有 AGENTS.md、知识文档和未提交修改，完成后报告创建、修改和复用的文件。
```

按当前 Page 规范，空项目默认结果为：

```text
项目根目录/
├── AGENTS.md
└── knowledge/
    └── index.md
```

实际输出以执行时读取的 Page 为准。功能 Spec、架构和决策文档根据真实需求按需创建，不复制教学示例充当项目事实。

已有项目会先检查原有规则与知识系统，再补充缺失项。重复执行不重复追加；冲突无法消解时会询问。初始化不会生成业务代码、安装依赖，也不会自动提交或推送。

## 更新

- **规范或模板调整**：修改 Page，下次执行读取最新版，无需为此更新 Skill。
- **Skill 执行流程调整**：更新 GitHub 仓库，并更新安装副本。
- **已初始化项目**：不会随 Page 更新自动改变，需要明确提出比较与合并请求。

手动克隆安装的用户，可在安装目录检查本地改动后执行：

```bash
git -C ~/.agents/skills/harness-init status --short
git -C ~/.agents/skills/harness-init pull --ff-only
```

如果存在本地修改或更新失败，先处理差异，不要强制重置。通过安装器安装的副本，先让 Codex 检查现有安装并更新；不要假定安装器会覆盖已有目录。

## 常见问题

| 情况 | 处理方式 |
| --- | --- |
| 找不到 `$harness-init` | 检查安装位置与 Skill 文件，重新打开会话；必要时重启客户端 |
| 私有仓库下载失败 | 检查安装环境的 GitHub 身份和仓库读取权限 |
| 能读取仓库，但不能读取 Page | 两者是独立权限；启用可用的 Page 连接，或明确提供本次采用的最新规范正文 |
| 在云端任务中找不到本机 Skill | 本机安装不等于云端安装；需要在目标运行环境另行提供 Skill 及 Page 读取能力 |

## 仓库结构

```text
harness-init/
├── SKILL.md          # 触发说明与执行流程
├── agents/
│   └── openai.yaml   # 显示名称和调用提示
└── README.md         # 安装与使用说明
```

参考：[官方 Skill 文档](https://learn.chatgpt.com/docs/build-skills)。

当前已完成 Skill 格式校验；尚未在其他项目进行完整初始化试运行。
