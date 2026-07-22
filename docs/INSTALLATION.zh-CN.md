# 安装说明

## 环境要求

- 支持本地技能的 Claude Code 或 OpenAI Codex
- 如需运行报告验证器，需 Python 3.10 或更高版本
- 不需要安装 Python 依赖，不需要 API key，也不需要第三方模型账号

## 从压缩包安装

解压前先检查压缩包内容：

```bash
unzip -l dist/evidence-research-report-claude.skill
unzip -l dist/evidence-research-report-codex.skill
```

安装其中一版或两版：

```bash
unzip dist/evidence-research-report-claude.skill -d ~/.claude/skills
unzip dist/evidence-research-report-codex.skill -d ~/.codex/skills
```

每个压缩包都只有一个名为 `evidence-research-report` 的顶层目录。安装后重启对应应用，让宿主重新发现技能。

## 从源码安装

```bash
cp -R claude/evidence-research-report ~/.claude/skills/
cp -R codex/evidence-research-report ~/.codex/skills/
```

如果目标目录已经存在，请先检查内容。直接替换会覆盖当地修改。

## 安装验证

检查清单文件并运行验证器测试：

```bash
test -f ~/.claude/skills/evidence-research-report/SKILL.md
test -f ~/.codex/skills/evidence-research-report/SKILL.md
python3 -m unittest discover -s tests -v
```

Codex 版的 `agents/openai.yaml` 提供显示信息并允许隐式调用；Claude Code 版不需要该文件。

## 更新

下载或拉取新版本，先检查差异，再只替换对应的技能目录。本项目没有自动更新机制，也不会在运行时下载可执行代码。

## 卸载

只删除实际安装的目录：

```bash
rm -r ~/.claude/skills/evidence-research-report
rm -r ~/.codex/skills/evidence-research-report
```
