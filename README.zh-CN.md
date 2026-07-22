# 证据优先研究报告技能

[English](README.md)

这是一个适用于 Claude Code 与 OpenAI Codex 的轻量研究技能。目标是在只使用可查证来源的前提下，产出可供决策的报告，同时避免小问题演变成无上限、耗时数小时的研究任务。

## 能做什么

- 将请求路由为不调研、快速、标准或深度四种模式。
- 搜索结果只用于发现候选来源；引用前必须打开并阅读原始页面。
- 区分第一方声明、权威记录、独立报道与推论。
- 必答问题已有证据、连续两次搜索无新增重要证据，或达到已声明预算时停止。
- 拒绝没有证据的最高级断言，并明确写出会影响决策的资料缺口。
- 提供确定性验证器，检查引用编号、参考资料 URL 与未解决标记。
- 不需要 API key、第三方模型、运行时安装依赖或读取 shell 启动文件。

## 仓库结构

```text
claude/evidence-research-report/   Claude Code 版
codex/evidence-research-report/    OpenAI Codex 版
dist/                              可安装的 .skill 压缩包
docs/                              中英文说明
tests/                             确定性验证器测试
```

两版共用证据政策、报告结构、深度模式规则、评测案例与验证器。只有宿主平台的工具表述和元数据不同。

## 快速安装

下载 `dist/` 中对应的压缩包，检查内容后解压到用户技能目录：

```bash
# Claude Code
unzip dist/evidence-research-report-claude.skill -d ~/.claude/skills

# OpenAI Codex
unzip dist/evidence-research-report-codex.skill -d ~/.codex/skills
```

安装后重启对应应用。源码安装、校验、更新与卸载方式见[安装说明](docs/INSTALLATION.zh-CN.md)。

## 示例提示词

```text
只确认供应商 A 的官方文档是否提供交易监控 API，300 字以内回答。

比较三家供应商公开记录中的制裁筛查能力，供采购决策使用。

深度比较三个司法管辖区的现行监管要求，并给出完整证据链。

这份报告已经完成核实，只排版，不调研，也不要修改任何主张。
```

技能默认输出简体中文；产品名与技术术语保留原文。用户可以通过明确指令覆盖语言与格式。

## 证据与成本控制

| 模式 | 典型用途 | 默认限制 |
|---|---|---|
| 不调研 | 排版、翻译或整理已核实材料 | 不搜索，不新增主张 |
| 快速 | 一个窄问题或短报告 | 最多 2 个搜索批次；通常阅读 2–4 个最强页面 |
| 标准 | 供应商尽调、2–5 个对象比较、正式报告 | 先做 2–3 个搜索批次；通常保留 6–12 个有效来源 |
| 深度 | 用户明确要求详尽研究，或同意跨司法管辖区升级 | 最多 4–6 个搜索批次；通常保留 12–25 个有效来源 |

这些数字是上限和常见区间，不是来源配额。是否完成由来源质量与主张覆盖决定。

## 验证

在任一已安装技能目录中执行：

```bash
python3 scripts/validate_report.py /path/to/report.md
```

验证器只检查机械规则。`PASS` 不代表来源在语义上支持主张；智能体仍必须逐项核对所有重要主张。

运行仓库测试：

```bash
python3 -m unittest discover -s tests -v
```

## 完整文档

- [安装说明](docs/INSTALLATION.zh-CN.md) / [Installation](docs/INSTALLATION.md)
- [使用说明](docs/USAGE.zh-CN.md) / [Usage](docs/USAGE.md)
- [方法说明](docs/METHODOLOGY.zh-CN.md) / [Methodology](docs/METHODOLOGY.md)
- [安全说明](SECURITY.zh-CN.md) / [Security](SECURITY.md)

## 隐私与来源边界

本仓库是去识别化的通用公开版，不包含组织名称、内部部门称谓、本机路径、凭证、报告正文或私有来源清单。评测提示词只使用虚构占位符。

## 许可证

[MIT](LICENSE)
