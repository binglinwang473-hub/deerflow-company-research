# 求职者公司调研智能体（基于 DeerFlow 二次开发）

输入「公司名 + 目标岗位」，智能体自动联网搜索、阅读原文，生成一份**带引用来源的中文求职调研报告**：公司概况、核心业务、近期动态、文化与员工评价、岗位分析与技术/产品栈、可能的面试题（带答题思路）、反问面试官的问题、准备建议。

示例：`reports/字节跳动_AI产品经理_2026-10-14.md`（27 个引用来源）

## 上游 vs 我加的

| 部分 | 来源 | 说明 |
|---|---|---|
| `upstream/` | [bytedance/deer-flow](https://github.com/bytedance/deer-flow)（MIT，commit `a5e7175`） | 原样 clone，**未修改任何文件**。智能体框架、工具调用循环、DuckDuckGo 搜索、Readability 正文提取、DeepSeek 模型适配都来自上游 |
| `extension/skills/job-seeker-company-research/SKILL.md` | 我写的 | 调研流程 + 报告模板 + 约束（禁止编造、标注个人评价、工具调用预算） |
| `extension/jobseeker_ext/direct_fetch.py` | 我写的 | 免费的网页抓取工具，替换上游默认的 Jina Reader |
| `extension/config.yaml` | 由上游 `config.example.yaml` 复制后修改 | 只改了 4 处，都带 `[jobseeker-ext]` 注释或在 models 段：接入 DeepSeek、换抓取工具、搜索结果 5→8、递归上限 100→200 |
| `extension/scripts/run_research.py` | 我写的 | 命令行入口，用上游的嵌入式客户端 `DeerFlowClient` 运行 |
| `extension/UPSTREAM_LICENSE_DeerFlow_MIT.txt` | 上游 | 保留原作者 MIT 许可声明 |

## 运行

```bash
cd upstream/backend && uv sync            # 按上游 README 安装后端依赖（Python 3.12+）
uv run python ../../extension/scripts/run_research.py 字节跳动 AI产品经理
```
密钥从 `/workspace/ai-job-radar/.env` 的 `LLM_API_KEY` 读取（可用 `KEY_ENV_FILE` 改路径），只放进进程环境变量 `DEEPSEEK_API_KEY`，不打印、不写进任何文件。一次运行约 3~4 分钟，DeepSeek 费用约几毛钱人民币。

## 设计取舍

1. **不改上游，用“技能 + 配置 + 插件工具”扩展**：DeerFlow 本身就是靠 Skill（Markdown 写的工作流说明）扩展能力的。我把调研流程写成 Skill，通过配置注入，上游升级时直接 `git pull` 就行，不会冲突。
2. **用嵌入式客户端而不是网页界面**：DeerFlow 的完整版要起网关、前端、nginx，对“一条命令出报告”太重。上游提供了 `DeerFlowClient`，在进程内就能跑同一套智能体。
3. **零付费 API Key**：搜索用上游自带的 DuckDuckGo（ddgs，免 Key）。上游默认的网页抓取 Jina Reader 在我的运行环境里被拒（匿名访问报 401「网络信誉差」），所以自己写了 `direct_fetch`：用 httpx 直接抓页面，再复用上游的 Readability 提取正文，同样免 Key。
4. **防幻觉**：Skill 要求关键数字尽量双来源、查不到就写“未找到”、每条事实带 `[n]` 引用，员工评价必须标注是个人观点。
5. **防失控**：第一次运行时模型反复搜索，触发了 100 步递归上限。我在 Skill 里加了工具预算（搜索 ≤12 次、抓取 ≤6 次，失败不重试），同时把上限调到 200，之后就能稳定出报告了。

## 面试可聊的点

- DeerFlow 的架构：主智能体 + 工具 + Skill + 沙箱，以及 Skill 和 Prompt 有什么区别
- 为什么选择不改上游源码：方便升级、责任边界清楚
- 真实踩过的坑：Jina 401 → 自己写抓取工具；智能体陷入循环 → 设工具预算；中文站点（脉脉、牛客）反爬，所以报告里中文员工评价偏少
- 怎么评估报告质量：引用是否可点开、数字是否交叉核对、章节是否齐全；下一步可以做自动化评测
- 成本：单份报告约十几次工具调用，用 DeepSeek 几毛钱

## 简历写法（如实）

> **求职者公司调研智能体**（个人项目）：基于字节开源的 DeerFlow 智能体框架二次开发，设计「公司+岗位」调研 Skill 与报告模板，接入 DeepSeek 大模型，并自研免费网页抓取工具替换被限流的 Jina Reader；通过工具调用预算解决智能体死循环问题。约 3 分钟生成带 20+ 条引用来源的中文求职调研报告（含面试题与反问清单）。

## 已知局限

- DuckDuckGo 对中文站点覆盖一般，脉脉、看准网、牛客面经经常搜不到或者抓取被拦
- 部分财务数字来自媒体引述知情人士，报告里已标注，需要自行核实
- 报告是 AI 生成的，投递或面试前请点开引用核对一遍
