---
name: harness-update
description: 从 lugq/harness-kit 更新已安装的 harness-init 与 harness-update。用于更新 HarnessKit Skills；不初始化或更新项目知识文件。
---

# Harness 更新

执行 `python3 <本 Skill 绝对目录>/scripts/update.py`，同时更新同一用户级 Skill 目录中的 harness-init 和 harness-update。可加 `--check` 仅检查。

需要 Git 和该仓库读取权限。脚本验证安装基线；有本地修改、额外文件、缺失基线或认证失败时停止，报告原因，不强制覆盖。缺少基线但文件与远端完全相同时，可安全建立基线。不要执行项目初始化或修改项目 AGENTS.md 与 knowledge/。

更新后报告远端版本和结果，下一轮使用新内容。此 Skill 不提供系统终端命令。
