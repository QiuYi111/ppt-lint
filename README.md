# ppt-lint

配置驱动的 PowerPoint 格式检查与自动修复工具。

用户用 YAML + 自然语言描述规范，工具自动将规则编译为 `python-pptx` 检查器，输出 lint 报告后一键 fix。

## 安装

```bash
# 创建虚拟环境
uv venv && source .venv/bin/activate

# 安装（开发模式）
uv pip install -e ".[dev]"
```

## 使用

```bash
# 检查 PPT 文件
ppt-lint check presentation.pptx --rules rules.yaml

# 检查并自动修复
ppt-lint check presentation.pptx --rules rules.yaml --fix

# 预览修复（不修改文件）
ppt-lint check presentation.pptx --rules rules.yaml --fix --dry-run

# JSON 输出
ppt-lint check presentation.pptx --rules rules.yaml --output json

# HTML 报告
ppt-lint check presentation.pptx --rules rules.yaml --output html --report report.html

# 生成示例规则文件
ppt-lint init
```

## 规则配置 (rules.yaml)

```yaml
meta:
  name: "导师组规范 v1"
  version: "1.0"

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

colors:
  allowed_text: ["#1F2D3D", "#333333", "#666666", "#FFFFFF"]
  allowed_background: ["#FFFFFF", "#F5F5F5"]
  accent: "#2B7FE1"

alignment:
  title: "left"
  body: "left"

spacing:
  line_spacing: 1.2

slide_number:
  visible: true

charts:
  require_title: true

# AI 规则（需要 ANTHROPIC_API_KEY）
ai_rules:
  - id: "no_orphan_text"
    description: "每张 slide 的正文文字块不应该只有一行孤行"
    severity: warning
```

## 支持的规则

| 规则 | 检查内容 | 自动修复 |
|------|---------|---------|
| `fonts.*` | 字体名称、字号、粗细、颜色 | ✅ |
| `colors.allowed_text` | 文字颜色白名单 | — |
| `colors.allowed_background` | 背景色白名单 | ✅ |
| `alignment.*` | 文本对齐方式 | ✅ |
| `spacing.line_spacing` | 行间距 | ✅ |
| `slide_number.visible` | 页码是否存在 | — |
| `charts.require_title` | 图表标题 | — |
| `ai_rules` | 自然语言描述的复杂规则 | — |

## 架构

```
rules.yaml → 编译器 (compiler.py) → 检查器 (script/AI) → 引擎 (engine.py) → 报告 → 修复
```

- **Domain 层** (`internal/domain/`): 纯 Python，无 python-pptx 依赖
- **Infrastructure 层** (`internal/infrastructure/`): python-pptx 操作、编译、引擎、报告
- **CLI** (`cli/`): click 命令行接口

## 测试

```bash
# 运行全部测试
pytest tests/ -v

# 代码检查
ruff check .
```

## AI 规则

设置 `ANTHROPIC_API_KEY` 环境变量后，AI 规则会通过 Claude API 编译为 Python 函数，结果缓存在 `.ppt-lint-cache/` 目录。后续运行不再消耗 token，除非规则描述变更。
