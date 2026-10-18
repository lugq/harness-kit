---
name: harness-update
description: 从 lugq/harness-kit 更新已安装的 harness-init 与 harness-update。用于更新 HarnessKit Skills；不初始化或更新项目知识文件。
---

# Harness 更新

执行 `python3 <本 Skill 绝对目录>/scripts/update.py`，同时更新同一用户级 Skill 目录中的 harness-init 和 harness-update。可加 `--check` 仅检查。

需要 Python 3.9+、Git 和该仓库读取权限。脚本验证安装基线；有本地修改、额外文件、无法核验的安装或认证失败时停止，报告原因，不强制覆盖。缺少基线时核验可信 main 历史中的完整文件哈希，匹配旧版即可升级并建立基线。默认 HTTPS 使用现有凭据，也可复用 GitHub CLI 已有登录；可用 --repo 指定可信 SSH/HTTPS 仓库，不改变全局 Git 凭据配置。

脚本先校验暂存包，再替换两个目录。失败时回滚；有未完成事务时停止，确认无其他更新进程后使用 --recover 恢复。恢复失败保留备份并报告路径，不能删除恢复材料或强行继续。不要执行项目初始化或修改项目 AGENTS.md 与 .harness/。

更新后报告远端版本和结果，下一轮使用新内容。此 Skill 不提供系统终端命令。
