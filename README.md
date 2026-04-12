<div align="center">

# ppt-lint

**配置驱动的 PowerPoint 格式检查与自动修复工具**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-28%2F28-brightgreen.svg)](tests/)

用 YAML 描述规范 → 自动检查 → 一键修复

[快速开始](#快速开始) · [规则配置](#规则配置) · [架构设计](#架构设计) · [开发指南](#开发指南)

</div>

---

## 特性

- 🎯 **配置驱动** — 用 YAML 声明式定义 PPT 格式规范，零代码
- ⚡ **快速脚本检查** — 字体、颜色、对齐、间距等预定义基元直接用 `python-pptx` 执行，无需 API
- 🤖 **AI 规则兜底** — 复杂/模糊规则（如"不要孤行文字"）通过 Claude API 编译为 Python 检查函数
- 💾 **编译缓存** — AI 规则只调用一次 API，编译结果持久化，后续运行零 token 消耗
- 🔧 **自动修复** — 大部分基元规则支持 `--fix` 一键修复
- 📊 **多格式报告** — 终端彩色输出、JSON 机器可读、HTML 自包含报告
- 🏗️ **领域驱动** — Domain 层纯 Python 无依赖，Infrastructure 层封装 `python-pptx`

## 快速开始

### 安装

```bash
# 推荐: uv
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 或使用 pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### 检查 PPT

```bash
# 生成示例规则文件
ppt-lint init

# 检查文件
ppt-lint check presentation.pptx --rules rules.yaml

# 检查并自动修复
ppt-lint check presentation.pptx --rules rules.yaml --fix

# 预览修复（不修改文件）
ppt-lint check presentation.pptx --rules rules.yaml --fix --dry-run
```

### 输出格式

```bash
# 终端彩色输出（默认）
ppt-lint check presentation.pptx --rules rules.yaml

# JSON 输出（CI/CD 友好）
ppt-lint check presentation.pptx --rules rules.yaml --output json

# HTML 报告
ppt-lint check presentation.pptx --rules rules.yaml --output html --report report.html
```

## 规则配置

规则文件使用 YAML 格式，分为**预定义基元**和 **AI 规则**两大类。

### 基元规则

覆盖 90% 的常见格式需求：

```yaml
meta:
  name: "导师组规范 v1"
  version: "1.0"

# ── 字体 ──────────────────────────────────────────
fonts:
  title:
    family: "微软雅黑"
    size_pt: 28
    bold: true
    color: "#1F2D3D"
  body:
    family: "微软雅黑"
    size_pt: 14
    bold: false
    color: "#333333"

# ── 颜色 ──────────────────────────────────────────
colors:
  allowed_text: ["#1F2D3D", "#333333", "#666666", "#FFFFFF"]
  allowed_background: ["#FFFFFF", "#F5F5F5"]
  accent: "#2B7FE1"

# ── 对齐 ──────────────────────────────────────────
alignment:
  title: "left"
  body: "left"

# ── 间距 ──────────────────────────────────────────
spacing:
  line_spacing: 1.2

# ── 页码 ──────────────────────────────────────────
slide_number:
  visible: true

# ── 图表 ──────────────────────────────────────────
charts:
  require_title: true
```

### AI 规则

基元搞不定的复杂规则，用自然语言描述：

```yaml
ai_rules:
  - id: "no_orphan_text"
    description: "每张 slide 的正文文字块不应该只有一行孤行，至少要有两行或者干脆没有"
    severity: warning

  - id: "consistent_bullet_style"
    description: "同一张 slide 内，所有 bullet point 的缩进层级和符号风格必须一致"
    severity: error

  - id: "figure_has_caption"
    description: "每张图片下方或上方必须有一个文字框作为图注，图注以'图X.'开头"
    severity: warning
```

> 使用 AI 规则需要设置 `ANTHROPIC_API_KEY` 环境变量。编译结果缓存在 `.ppt-lint-cache/`，规则不变则不消耗 token。

### 支持的基元规则

| 规则 | 检查内容 | 自动修复 |
|------|---------|:--------:|
| `fonts.*.family` | 字体名称 | ✅ |
| `fonts.*.size_pt` | 字号 | ✅ |
| `fonts.*.bold` | 粗细 | ✅ |
| `fonts.*.color` | 文字颜色 | ✅ |
| `colors.allowed_text` | 文字颜色白名单 | — |
| `colors.allowed_background` | 背景色白名单 | ✅ |
| `colors.accent` | 强调色限制 | — |
| `alignment.*` | 文本对齐 | ✅ |
| `spacing.line_spacing` | 行间距 | ✅ |
| `slide_number.visible` | 页码存在性 | — |
| `charts.require_title` | 图表标题 | — |
| `ai_rules` | 自然语言规则 | — |

## 架构设计

```
rules.yaml
    ↓
规则编译器 (compiler.py)
    ↓
┌──────────────────────────┐
│  脚本规则 (python-pptx)   │  ← 预定义基元，零 API 调用
│  AI 规则 (Claude 缓存)    │  ← 首次编译后本地执行
└──────────────────────────┘
    ↓
Lint 引擎 (engine.py)
    ↓
报告 (terminal / JSON / HTML)  →  --fix  →  自动修复
```

采用**领域驱动设计（DDD）**分层架构：

```
ppt-lint/
├── cli/                          # CLI 入口（click）
│   └── ppt_lint.py
├── internal/
│   ├── domain/                   # 领域层（纯 Python，零外部依赖）
│   │   ├── models.py             # LintIssue, RuleSet 等数据模型
│   │   ├── interfaces.py         # 抽象接口
│   │   └── rules.py              # 规则定义与匹配
│   └── infrastructure/           # 基础设施层
│       ├── compiler.py           # 规则编译器（YAML → 检查函数）
│       ├── engine.py             # Lint 引擎（扫描 + 执行）
│       ├── pptx_adapter.py       # python-pptx 操作封装
│       ├── reporter.py           # 多格式报告生成
│       └── ai_cache.py           # AI 规则编译缓存
├── tests/                        # 测试套件
└── rules.yaml                    # 示例规则文件
```

**核心设计决策：**

- **Domain 层零依赖** — 不 import `python-pptx`，可独立测试和复用
- **编译缓存** — AI 规则通过 Claude API 一次性编译为 Python 函数，持久化到 `.ppt-lint-cache/`
- **输出隔离** — `--output json` 时 stdout 只输出 JSON，dry-run 信息走 stderr
- **程序化测试 fixtures** — 测试 PPT 通过 `python-pptx` 代码生成，无需二进制文件

## 开发指南

### 环境搭建

```bash
git clone https://github.com/QiuYi111/ppt-lint.git
cd ppt-lint
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 测试

```bash
# 运行全部测试（28 tests）
pytest tests/ -v

# 带覆盖率
pytest tests/ -v --cov=. --cov-report=term-missing

# 创建测试用 PPT
python scripts/create_test_pptx.py bad.pptx --violations
python scripts/create_test_pptx.py good.pptx
```

### 代码质量

```bash
ruff check .          # Lint
ruff format .         # Format
make verify           # Lint + Test
```

### 添加新基元规则

1. 在 `internal/domain/rules.py` 添加规则定义
2. 在 `internal/infrastructure/pptx_adapter.py` 实现检查和修复逻辑
3. 在 `internal/infrastructure/compiler.py` 注册编译逻辑
4. 添加测试到 `tests/test_rules.py` 或 `tests/test_adapter.py`

### 添加新 AI 规则

只需在 `rules.yaml` 的 `ai_rules` 中添加描述，工具会自动调用 Claude 编译：

```yaml
ai_rules:
  - id: "my_new_rule"
    description: "描述你要检查的内容"
    severity: error
```

## Roadmap

- [x] 核心检查引擎 + CLI
- [x] 预定义基元规则（字体、颜色、对齐、间距、页码、图表）
- [x] 多格式报告（终端、JSON、HTML）
- [x] 自动修复 (`--fix`)
- [x] AI 规则编译 + 缓存
- [ ] 更多基元规则（内容区边距、页码位置、强调色检测）
- [ ] CI/CD 集成（GitHub Actions）
- [ ] VS Code 插件
- [ ] 更多 LLM 后端支持（OpenAI、本地模型）

## License

MIT

---

<div align="center">

**用规范替代人工检查，让 PPT 排版不再痛苦。**

</div>
