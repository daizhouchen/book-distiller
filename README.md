# Book Distiller · 读书蒸馏

把一本书蒸馏成一张中文典雅风 HTML 网页——**事实支撑观点，揭示系统逻辑，事实陈述本身也要系统化**。

这是一个 [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills)，不是一个独立工具。

## 核心理念

大多数读书笔记有两种死法：
- **只有观点没有事实**——读者无法判断对错，拿不走
- **只有事实没有框架**——一堆碎片，三天后忘光

本 Skill 追求第三条路：

```
穷尽式事实提取
    ↓
维度分类（按书的基因）
    ↓
模式识别（单维度规律）
    ↓
跨维度交织（系统浮现）
    ↓
机制推演 → 观点落地
    ↓
典雅 HTML 呈现
```

## 五大特征

### 1. 七基因组合模型

不是僵化的分类，而是每本书拥有 2-4 种基因：
- **人物** / **叙事** / **论证** / **模型** / **史料** / **美学** / **体验**

每本书的骨架由基因组合动态拼装，独一无二。

### 2. 事实系统化四步法

零散事实不支撑观点。必须：穷尽 → 分类 → 识模式 → 看交织。详见 `references/fact-systematization.md`。

### 3. 三重内容架构

每个模块按 **事实层 → 机制层 → 观点层** 三重展开——自下而上让结论自然浮现。

### 4. 框架内化（二阶段写作法）

- 第一阶段：允许使用"马斯洛/博弈论/场域理论"等框架名帮助思考
- 第二阶段：把框架名**全部删掉**，只保留导出的洞察

框架是手术刀，用完收进刀鞘。详见 `references/frameworks-internalization.md`。

### 5. 学术诚实

- **误读陷阱**：主动揭示名著常见的误读
- **作者盲点**：诚实标注作者的时代局限、知识边界
- **信源分级**：A/B/C/D 四级，透明标注信源构成与置信度

## 使用方法

### 作为 Skill 安装

1. 把 `book-distiller/` 目录放到 Claude Code 的 skills 目录下
2. 重启 Claude Code，Skill 会自动被发现
3. 对话中触发："帮我蒸馏《XXX》" / "用 book-distiller 分析《XXX》"

### 手动调用脚本

```bash
# 抓取信源（生成抓取计划）
python3 scripts/fetch_sources.py "书名" "作者"

# 渲染 distill.json → HTML
python3 scripts/render.py workspace/book/distill.json workspace/book/book.html

# 质量检查
python3 scripts/quality_check.py workspace/book/distill.json
```

## 文件结构

```
book-distiller/
├── SKILL.md                              # 主入口：persona + 九步流程
├── references/
│   ├── core-thesis.md                    # 核心宪法
│   ├── fact-systematization.md           # ⭐ 事实系统化四步法
│   ├── genes.md                          # 七基因 + 坐标系
│   ├── skeletons/                        # 五种主基因的骨架模板
│   │   ├── character-heavy.md
│   │   ├── argument-heavy.md
│   │   ├── model-heavy.md
│   │   ├── narrative-heavy.md
│   │   └── aesthetic-heavy.md
│   ├── frameworks-internalization.md     # 二阶段写作法
│   ├── source-triangulation.md           # 信源分级
│   ├── misreading-and-blindspots.md      # 误读+盲点目录
│   ├── language-quality-checklist.md     # 语感禁词库
│   ├── style-guide.md                    # 典雅风视觉规范
│   ├── lens-calibration.md               # 视角自适应
│   └── examples/                         # 三本典型书的骨架示例
│       ├── jinpingmei-skeleton.md
│       ├── yuanyuan-jiushizhu-skeleton.md
│       └── feibaoli-goutong-skeleton.md
├── assets/
│   └── template.html                     # 典雅风单文件模板
├── scripts/
│   ├── fetch_sources.py                  # 多源抓取 + 信源分级
│   ├── render.py                         # distill.json → HTML
│   └── quality_check.py                  # 密度+禁词+框架名自检
├── evals/
│   └── evals.json                        # 测试用书单
└── README.md
```

## 产出示例

以《乌合之众》为例，产出包含：

- **信源标注**：A 级 55% / B 级 15% / C 级 5% / D 级 25%，置信度"中高"
- **母题一句话**：个体入群即失魂——理性让位于暗示
- **记忆抓手**：一千人只剩一颗脑袋
- **6 个主干模块**，每个模块三层结构齐全
- **34 处原文锚点**（quote_pairs + 章节标记）
- **3 条误读陷阱**：政治化误读、"人民不可信"的滥用、时代适用性误判
- **3 条作者盲点**：种族论滤镜、共情不足、实证方法的时代局限
- **8 条原文金句**
- **典雅风 HTML**：三入口分层（速读/精读/深读）+ 原文双栏对照 + 内嵌水墨 SVG

## 核心原则（写在最前也写在最后）

> **不能空有观点。**
> **事实支撑观点。**
> **揭示系统逻辑。**
> **事实陈述本身也要系统化。**

## 许可

MIT License
