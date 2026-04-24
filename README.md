# Book Distiller · 读书蒸馏

把一本书蒸馏成一张中文典雅风 HTML 网页——**事实支撑观点，揭示系统逻辑，事实陈述本身也要系统化**。

这是一个 [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills)，需要配合 Claude Code 使用。不是独立运行的工具。

---

## 目录

- [为什么做这个](#为什么做这个)
- [核心特征](#核心特征)
- [安装](#安装)
- [使用](#使用)
- [产出示例](#产出示例)
- [文件结构](#文件结构)
- [两道质量闸门](#两道质量闸门)
- [开发/扩展](#开发扩展)
- [已知限制](#已知限制)
- [FAQ](#faq)
- [许可](#许可)

---

## 为什么做这个

市面上的读书笔记有两种死法：

- **只有观点没有事实**——读者无法判断对错，拿不走任何东西
- **只有事实没有框架**——一堆碎片，三天后忘光

本 Skill 追求的是第三种路径：

```
穷尽式事实提取
    ↓
维度分类（按书的基因选坐标系）
    ↓
模式识别（单维度规律）
    ↓
跨维度交织（系统浮现）
    ↓
机制推演 → 观点落地
    ↓
典雅 HTML 呈现
```

**事实本身必须系统化**——零散的"好引用"不支撑论证，只有穷尽 + 分类 + 找模式 + 看交织之后浮现的结构，才算揭示了书的系统逻辑。

---

## 核心特征

### 1. 七基因组合模型

不用僵化分类。每本书拥有 2-4 种基因：

- **人物** · **叙事** · **论证** · **模型** · **史料** · **美学** · **体验**

每本书的骨架由基因组合动态拼装，独一无二：

| 书 | 基因组合 |
|---|---|
| 金瓶梅 | 人物(主) + 叙事 + 史料 |
| 遥远的救世主 | 论证(主) + 人物 + 叙事 |
| 乌合之众 | 论证(主) + 史料 |
| 人类简史 | 论证(主) + 史料 + 叙事 |
| 非暴力沟通 | 模型(主) + 体验 |
| 百年孤独 | 叙事(主) + 人物 + 美学 |
| 瓦尔登湖 | 美学(主) + 体验 + 论证 |

详见 [`references/genes.md`](references/genes.md)。

### 2. 事实系统化四步法 ⭐

零散事实不是证据，是罗列。必须经过：

1. **穷尽式提取**（不挑只收；含沉默性事实）
2. **维度分类**（进基因对应的坐标系）
3. **模式识别**（每个维度找规律，≥ 3 事实锚点）
4. **跨维度交织**（多维度互相转化 → 系统浮现）

详见 [`references/fact-systematization.md`](references/fact-systematization.md)。

### 3. 三重内容架构

每个模块按 **事实层 → 机制层 → 观点层** 三重展开——让结论自然从事实中浮现，不是从空论里跳出来。

### 4. 框架内化 · 二阶段写作法

- **第一阶段**：自由使用"马斯洛/博弈论/场域理论"等框架辅助思考
- **第二阶段**：把正文里所有框架名**全部删掉**，只保留思考的洞察

框架是手术刀，用完收进刀鞘。详见 [`references/frameworks-internalization.md`](references/frameworks-internalization.md)。

### 5. 学术诚实

- **误读陷阱**：主动揭示名著常被误读的方式
- **作者盲点**：诚实标注时代局限、知识边界
- **信源分级**：A/B/C/D 四级透明标注

### 6. 典雅风呈现

- 单文件 HTML，离线可读，无 CDN 依赖
- 三入口分层：速读（15min）/ 精读（1h）/ 深读（全本）
- 宋体为骨 + 墨色为神 + 朱砂点睛
- 内嵌水墨线条风 SVG

---

## 安装

### 先决条件

- **Claude Code** 已安装（[官方指南](https://docs.claude.com/en/docs/claude-code/quickstart)）
- **Python 3.7+**（用于渲染 HTML 和质量自检）
- **Git**（用于克隆 repo）

### 方式一：Symlink 安装（推荐）

把 repo 克隆到任意位置，然后在 Claude Code 的 skills 目录下建 symlink。这样 `git pull` 之后本地 Skill 自动更新。

```bash
# 1. 克隆到你喜欢的位置（这里放在 ~/repos）
mkdir -p ~/repos && cd ~/repos
git clone https://github.com/daizhouchen/book-distiller

# 2. 确保 skills 目录存在
mkdir -p ~/.claude/skills

# 3. 建 symlink
ln -s ~/repos/book-distiller ~/.claude/skills/book-distiller

# 4. 确认安装
ls -la ~/.claude/skills/book-distiller
# 应该看到一个指向 ~/repos/book-distiller 的箭头
```

### 方式二：直接克隆到 skills 目录

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/daizhouchen/book-distiller
```

用这种方式，要更新就要 `cd ~/.claude/skills/book-distiller && git pull`。

### 方式三：Git submodule（如果你已有自己的 dotfiles repo）

```bash
cd ~/your-dotfiles
git submodule add https://github.com/daizhouchen/book-distiller \
    .claude/skills/book-distiller
git submodule update --init --recursive
```

### 验证安装

**第一步**：检查文件就位：

```bash
ls ~/.claude/skills/book-distiller/
# 应该看到：SKILL.md, README.md, references/, scripts/, assets/, evals/
```

**第二步**：**重启 Claude Code 会话**（Skill 在会话启动时加载，已开的会话不会生效）。

**第三步**：新会话里发一句触发词确认：

> 用 book-distiller 测试一下

或：

> 帮我蒸馏《论语·学而篇》看看

如果 Claude 开始按九步流程执行（报告母题、基因检测、信源分级等），就说明 Skill 被正确触发。

**第四步（可选）**：跑一下脚本自测：

```bash
cd ~/.claude/skills/book-distiller
python3 scripts/quality_check.py   # 应打出 usage 提示不报错
python3 scripts/visual_check.py    # 同上
```

### 卸载

```bash
# Symlink 方式
rm ~/.claude/skills/book-distiller

# 直接克隆方式
rm -rf ~/.claude/skills/book-distiller
```

---

## 使用

### 最基本的用法

在 Claude Code 会话里说任何一句：

- "帮我蒸馏《金瓶梅》"
- "用 book-distiller 分析《乌合之众》"
- "我想吃透《遥远的救世主》"
- "给我出一份《人类简史》的读书笔记"
- "蒸馏一下《非暴力沟通》"

Claude 会自动加载 SKILL.md，按九步流程执行，最后产出：

```
~/workspace/<book-slug>/
├── distill.json          # 结构化中间产出
└── <book>.html           # 最终单文件 HTML
```

### 带原文一起喂给 Claude

如果你手里有原书电子版（PDF/EPUB/TXT），告诉 Claude 文件路径：

> 蒸馏这本书，原文在 /path/to/book.pdf

Claude 会优先用你的 A 级原文，置信度自然拉满。

### 指定视角（可选）

默认是全貌视角。想特定视角：

> 用 book-distiller 分析《遥远的救世主》，重点从商战视角看

Skill 会自动切到商业 lens，在产出开头透明标注。不影响全貌覆盖。

### 手动调用脚本（不经过 Claude）

也可以不经 Skill 路由，直接手动跑管线：

```bash
cd ~/.claude/skills/book-distiller

# 1. 查看抓取计划（帮你列出该去哪些源抓原文）
python3 scripts/fetch_sources.py "乌合之众" "勒庞"

# 2. 如果你手工产出了 distill.json，渲染 HTML
python3 scripts/render.py /path/to/distill.json /path/to/output.html

# 3. 内容层自检（密度/禁词/框架名）
python3 scripts/quality_check.py /path/to/distill.json

# 4. 视觉层自检（三模式差异化/SVG/板块）
python3 scripts/visual_check.py /path/to/output.html
```

---

## 产出示例

以《乌合之众》为例，产出一份包含：

- **信源标注**：A 级 55% / B 级 15% / C 级 5% / D 级 25%，置信度**中高**
- **一句话母题**：个体入群即失魂——理性让位于暗示
- **记忆抓手**：一千人只剩一颗脑袋
- **6 个主干模块**，每个按事实层 → 机制层 → 观点层三重展开
- **34 处原文锚点**（quote_pairs + 章节/年份定位）
- **3 条误读陷阱**：政治化误读 / "人民不可信"滥用 / 时代适用性错判
- **3 条作者盲点**：种族论滤镜 / 共情不足 / 实证方法的时代局限
- **8 条原文金句**
- **典雅风 HTML**：三入口（速读/精读/深读）+ 原文双栏对照 + 水墨 SVG

三模式差异化（由 `visual_check.py` 实测）：

| 模式 | 可见板块 | 中文字数 | 增量 |
|---|---|---|---|
| 速读 · 15min | 3 | 402 | 基线 |
| 精读 · 1h | 5 | 9261 | **23×** |
| 深读 · 全本 | 9 | 11155 | 1.2× |

---

## 文件结构

```
book-distiller/
├── SKILL.md                              # 主入口 · persona + 九步流程 + 两道闸门
├── README.md                             # 就是你现在看的这份
├── LICENSE                               # MIT
├── .gitignore
│
├── references/                           # Skill 加载时按需读取
│   ├── core-thesis.md                    # ⭐ 宪法：四句核心主旨
│   ├── fact-systematization.md           # ⭐ 事实系统化四步法
│   ├── genes.md                          # 七基因 + 坐标系表
│   ├── skeletons/                        # 主基因专属骨架
│   │   ├── character-heavy.md
│   │   ├── argument-heavy.md
│   │   ├── model-heavy.md
│   │   ├── narrative-heavy.md
│   │   └── aesthetic-heavy.md
│   ├── frameworks-internalization.md     # 二阶段写作法
│   ├── source-triangulation.md           # 信源分级 A/B/C/D
│   ├── misreading-and-blindspots.md      # 误读陷阱 + 作者盲点目录
│   ├── language-quality-checklist.md     # 禁词库 + 典雅风语言规范
│   ├── style-guide.md                    # 典雅风视觉（颜色/字体/排版）
│   ├── lens-calibration.md               # 视角自适应逻辑
│   └── examples/                         # 三本典型书的骨架示例
│       ├── jinpingmei-skeleton.md
│       ├── yuanyuan-jiushizhu-skeleton.md
│       └── feibaoli-goutong-skeleton.md
│
├── assets/
│   └── template.html                     # 典雅风单文件 HTML 模板
│
├── scripts/
│   ├── fetch_sources.py                  # 多源抓取 + 信源分级计划
│   ├── render.py                         # distill.json → HTML（含 SVG 归一化）
│   ├── quality_check.py                  # 闸门一：内容层自检
│   └── visual_check.py                   # 闸门二：视觉层自检
│
└── evals/
    └── evals.json                        # 五本测试书单
```

---

## 两道质量闸门

### 闸门一 · 内容层（渲染前）

```bash
python3 scripts/quality_check.py distill.json
```

检查：
- 结构完整性（schema 齐全）
- 信源透明度
- 事实锚点密度
- 禁词扫描（网感词 / 营销体 / 作者腔 / 总结废话 / 学术造作 / PUA 腔）
- 正文框架名禁用（工具箱除外；历史人物姓名允许）
- 误读 ≥ 2、盲点 ≥ 2、金句 ≥ 5、记忆抓手 1
- 三层结构对齐

### 闸门二 · 视觉层（渲染后）

```bash
python3 scripts/visual_check.py book.html
```

检查：
- **三模式差异化**：精读 ≥ 速读 × 1.3 且 深读 ≥ 精读 × 1.2
- SVG 尺寸合规（无固定 width/height，必有 viewBox）
- 9 大板块齐全
- 三层结构对齐（facts/mech/view 数量相等）
- 原文对照 ≥ 6 组，他山之石 ≥ 2 处

**两道闸门都通过**才算合格。数字绿灯不代表真的好——这是本 Skill 从早期 Bug 学到的纪律。

---

## 开发/扩展

### 改骨架 / 改 persona

- `SKILL.md` 开头是 persona 和核心主旨——改这个影响最大
- `references/skeletons/*.md` 是主基因骨架——改这个影响特定类型书的产出结构
- `references/language-quality-checklist.md` 是禁词库——改这个影响语感

### 改视觉风格

- `assets/template.html` 是单文件 HTML 模板——CSS 全在里面
- 配色改 `:root` 里的 CSS 变量
- 字体改 `font-family` 栈
- 布局改 `--text-w`（正文宽）和 `--figure-w`（图宽）

### 加新的测试书

编辑 `evals/evals.json` 添加新 eval case，格式参见现有条目。

### 改质量闸门

- `scripts/quality_check.py` 的 `BANNED_*` 列表管禁词
- `scripts/visual_check.py` 的阈值（1.3× / 1.2×）管三模式差异要求
- `scripts/render.py` 的 `normalize_svg` 管 SVG 归一化

### 改造完自测

```bash
# 用 workspace 下已有的 distill.json 做回归
python3 scripts/render.py ~/workspace/wuhe-zhizhong/distill.json /tmp/test.html
python3 scripts/quality_check.py ~/workspace/wuhe-zhizhong/distill.json
python3 scripts/visual_check.py /tmp/test.html
```

---

## 已知限制

1. **依赖模型对书的了解**：冷门书（销量低、无学术讨论）会降级为 D 级为主的产出，置信度低
2. **不绕 paywall**：现代书原文获取全靠用户上传或公开渠道；碰到 DRM 保护就降级为"二手资料"模式
3. **中文优先**：虽能处理外文书，但产出是中文典雅风；不支持其他语言的典雅风呈现
4. **单文件 HTML**：为了离线可读的承诺，不用任何外部库 / CDN，所以高级交互（比如 3D 关系图）做不到
5. **9 步流程耗时**：一本书完整蒸馏需要数分钟到十几分钟（模型思考 + 信源抓取）

---

## FAQ

### Q: 我没有原书电子版，Skill 还能用吗？

A: 可以。Skill 会按优先级尝试：公开渠道原文 → 请求你上传 → WebSearch 拼凑二手资料 + 模型自身知识。最差情况下会在产出开头**明确标注**"基于二手资料，置信度中/低"，让你知道这份报告的局限。

### Q: 为什么正文里见不到"马斯洛"这种框架名？

A: 这是**二阶段写作法**的纪律——框架是思考工具，用来帮助作者拆解问题，但不是用来充论证本身。如果想看我用了哪些框架，展开文末的「思考工具箱」。详见 `references/frameworks-internalization.md`。

### Q: "事实系统化"和普通读书笔记的"摘抄+点评"有什么区别？

A: 摘抄+点评是**线性的**——你挑了 10 个觉得好的引用，逐条评论。事实系统化是**结构的**——穷尽所有相关事实 → 按维度分类 → 每个维度找规律 → 多维度交织看系统。产出里你会看到一张**事实矩阵**——那是普通笔记没有的东西。

### Q: 产出质量取决于什么？

A: 三个主要因素：
1. **原文可达性**（A 级信源占比）——没原文再好的方法论也是巧妇难为无米之炊
2. **书本身的"可蒸馏性"**——有系统逻辑的书（如金瓶梅、遥远的救世主）产出密度高；纯鸡汤书产出容易显空
3. **Claude 模型版本**——Opus 比 Sonnet 更能处理复杂推导；Haiku 做密度验证可以，产出不建议

### Q: 能改成英文产出吗？

A: 目前不能。典雅风（宋体 + 汉字章节号 + 楷体引用）深度绑定中文视觉习惯。如果你要英文读书笔记，这个 Skill 不是最佳选择。

### Q: 我想给这个 Skill 提改进建议 / 报 Bug

A: 欢迎提 Issue 或 PR：https://github.com/daizhouchen/book-distiller/issues

---

## 许可

MIT License — 详见 [LICENSE](LICENSE)。

---

## 核心信条（再强调一遍）

> **不能空有观点。**
> **事实支撑观点。**
> **揭示系统逻辑。**
> **事实陈述本身也要系统化。**

记住这四句就够了。
