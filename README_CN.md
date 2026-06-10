# Agent Prompt Optimizer (APO) — AI Agent 提示词优化器

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/deps-zero-brightgreen)]()
[![Type Hints](https://img.shields.io/badge/type%20hints-full-brightgreen)]()

**优化 AI Agent 的系统提示词，让它们更清晰、更安全、更高效。**

APO 是一款零依赖、纯 Python 的 CLI 工具。它分析系统提示词（System Prompt），输出可操作的优化报告。核心功能免费开源，高级功能 $9 一次性买断。

[English README](README.md)

---

## 安装

### 方式一：通过 pip 安装

```bash
pip install agent-prompt-optimizer
```

### 方式二：从源码安装

```bash
git clone https://github.com/iZhangDM/prompt-optimizer.git
cd prompt-optimizer
pip install -e .
```

### 方式三：直接运行（无需安装）

```bash
git clone https://github.com/iZhangDM/prompt-optimizer.git
cd prompt-optimizer
python apo.py optimize samples/bad_prompt.txt
```

**要求：** Python 3.9+。零外部依赖，支持 Linux、macOS、Windows (WSL)。

安装后验证：

```bash
apo --version
```

输出：

```
apo v1.0.0
```

---

## 快速上手

### 基本优化（Free 功能）

```bash
# 优化一个提示词文件
apo optimize prompt.txt

# 直接传入提示词文本
apo optimize --text "You are a helpful assistant..."

# 从标准输入读取
cat prompt.txt | apo optimize -

# 保存优化结果到文件
apo optimize prompt.txt -o optimized.txt

# 输出 JSON 格式（方便程序解析）
apo optimize prompt.txt --json

# 只运行单个分析模块
apo optimize prompt.txt --only structure
```

### 运行示例

仓库自带一个质量较差的示例提示词 `samples/bad_prompt.txt`：

```bash
apo optimize samples/bad_prompt.txt
```

输出示例：

```
============================================================
AGENT PROMPT OPTIMIZER — Analysis Report
============================================================
Prompt length: 200 words, 1121 chars

1. PROMPT STRUCTURE ANALYSIS
  Overall: 12/40

  ✓ Role Definition         (6/10)
    You are a helpful AI assistant. Please help the user with whatever...
  ✗ Output Format           (0/10)
  ✗ Tool Usage              (0/10)
  ✓ Constraints             (6/10)
    Don't do anything bad I guess. It's important to note that you should...

  Suggestions:
    • Add a clear output format specification section...
    • Add a clear tool usage instruction section...

2. LENGTH OPTIMIZATION
  Original:   200 words
  Optimized:  157 words
  Removed:    -43 words (21.5%)

3. CLARITY SCORE
  Overall: 46/100  Grade: F
  Below average — significant gaps
  Specificity:      12/30
  Actionability:    14/30
  Constraint Clarity: 20/40

4. ANTI-INJECTION HARDENING
  Risk Level: LOW  (0/100)
  No common injection patterns detected.

════════════════════════════════════════════
OPTIMIZED PROMPT
════════════════════════════════════════════
You are a helpful AI assistant. Help the user with whatever they need...
```

### Pro 功能（需要许可证）

```bash
# 高级重构改写
apo pro rewrite prompt.txt -o rewritten.txt

# 生成 A/B 测试变体（3 个策略不同的提示词）
apo pro ab-test prompt.txt -o variants.txt

# 针对特定模型优化
apo pro model gpt-4 prompt.txt -o gpt4-prompt.txt
apo pro model claude prompt.txt
apo pro model deepseek prompt.txt

# 查看支持的模型列表
apo pro model --list-models
```

### 许可证管理

```bash
# 检查当前许可证状态
apo license check

# 安装许可证密钥
apo license install <你的许可证密钥>
```

---

## Free vs Pro 功能对比

| 功能 | Free | Pro ($9) | 描述 |
|------|:----:|:--------:|------|
| **结构分析 (Structure Analyzer)** | ✅ | ✅ | 检查角色定义、输出格式、工具使用、约束边界 |
| **长度优化 (Length Optimizer)** | ✅ | ✅ | 80+ 冗余模式精简，去除废话但不失语义 |
| **清晰度评分 (Clarity Scorer)** | ✅ | ✅ | 从具体性、可操作性、约束清晰度三维打分 (0-100) |
| **防注入加固 (Anti-Injection)** | ✅ | ✅ | 检测 12 类注入漏洞，自动应用加固规则 |
| **高级改写 (Advanced Rewrite)** | ❌ | ✅ | 将提示词重新组织为逻辑清晰的章节结构 |
| **A/B 测试生成器** | ❌ | ✅ | 生成 3 个策略不同的提示词变体 + 测试指南 |
| **模型专项优化** | ❌ | ✅ | 针对 GPT-4、Claude、DeepSeek、Gemini、Llama、Mistral 定制 |

---

## 定价与购买

| 版本 | 价格 | 包含功能 |
|------|------|----------|
| **Free** | 免费 | 结构分析、长度优化、清晰度评分、防注入加固 |
| **Pro** | **$9**（一次性，终身有效） | 全部 Free 功能 + 高级改写 + A/B 测试生成 + 模型专项优化 + 优先支持 |

### 如何购买 Pro 许可证

发送邮件至 **2638884823@qq.com**，主题注明"APO Pro License"，我们会在 24 小时内将许可证密钥发送给你。

收到密钥后安装即可：

```bash
apo license install <你的许可证密钥>
```

---

## 常见问题 FAQ

### Q: APO 和其他提示词工具（如 PromptPerfect）有什么区别？
APO 专注 **Agent 系统提示词**（System Prompt），不是普通的聊天提示词。它会检查 Agent 特有的要素：工具调用说明、输出格式约束、注入防护等。此外，APO 是开源 CLI 工具，数据完全本地处理，不经过任何远程服务器。

### Q: 零依赖意味着什么？
APO 完全使用 Python 标准库，不依赖任何第三方包。安装即用，无需处理依赖冲突。

### Q: 支持哪些 Python 版本？
Python 3.9 及以上版本。

### Q: Pro 许可证可以在团队内共享吗？
许可证绑定邮箱，个人可在多台设备上使用。团队使用请联系我们获取团队价格。

### Q: 我的提示词会被上传到服务器吗？
不会。APO 完全在本地运行，所有分析都在你的机器上完成。你的提示词永远不会离开你的设备。

### Q: 支持 CI/CD 集成吗？
支持。APO 的 JSON 输出模式非常适合在 CI 流程中解析：

```bash
# 在 CI 中检查提示词质量
apo optimize system_prompt.txt --json | python -c "
import json, sys
data = json.load(sys.stdin)
if data['clarity']['overall_score'] < 60:
    print('提示词清晰度不达标!')
    exit(1)
"
```

### Q: 支持哪些模型？
Pro 版本支持以下模型的专项优化：
- **GPT-4**：结构化 Markdown，示例强调
- **Claude**：XML 分隔符，安全无害性框架
- **DeepSeek**：推理线索，双语支持
- **Gemini**：编号任务，安全声明
- **Llama**：原生 `<|start_header_id|>` 格式
- **Mistral**：简洁格式，工具强调

### Q: 可以优化中文提示词吗？
可以。APO 的分析逻辑是语言无关的（基于正则模式和文本结构），对中文和英文提示词都有效。不过长度优化模块的冗余模式库目前以英文为主，中文效果会稍弱一些。

---

## 许可证

Free 功能：MIT License。Pro 功能：专有许可。

详见 [LICENSE](LICENSE)。

---

**让每一个 Agent 提示词都经得起考验。**
