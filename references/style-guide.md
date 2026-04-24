# 典雅风视觉规范

## 主旨

**典雅风** = 文人书房 + 现代呼吸 + 离线自足

- 文人书房：宋体为骨，墨色为神，朱砂点睛
- 现代呼吸：大量留白，层次清晰，不堆砌
- 离线自足：单文件 HTML，字体回退栈，无 CDN 依赖

## 色彩体系

```
墨（主色）         #1a1a1a  — 正文
淡墨              #4a4a4a  — 次要文字/批注
宣（底色）         #f9f5ec  — 页面背景
次白              #fcfaf4  — 卡片/引用块背景
朱砂（强调色）     #8b3a3a  — 章节号、关键字、引导符
浅朱              #c26d6d  — 次要强调、分隔线
松石（冷点缀，慎用）#5b7a6a  — 对比色
淡金（暖点缀，慎用）#b89b66  — 对比色

背景渐层参考      linear-gradient(180deg, #f9f5ec 0%, #f5efe3 100%)
```

**节制使用原则**：朱砂只用于**最需要读者注意**的地方（章节号、关键词、引导符）。不要滥用。

## 字体栈

```css
/* 正文（宋体衬线） */
font-family:
  "Noto Serif SC",
  "Source Han Serif SC",
  "Songti SC",
  "方正书宋",
  "宋体",
  STSong,
  SimSun,
  serif;

/* 批注 / 引用原文（楷体） */
font-family:
  "Kaiti SC",
  "KaiTi",
  "STKaiti",
  "楷体",
  serif;

/* 数字/英文（衬线） */
font-family: "Crimson Pro", "Georgia", "Times New Roman", serif;
```

**不用无衬线字体做正文**。无衬线字体显得现代/科技风，破坏典雅感。
导航、按钮、表格头等辅助区可用 `system-ui, -apple-system` 系无衬线。

## 排版参数

### 基础

```css
:root {
  --body-font-size: 17px;
  --body-line-height: 1.85;
  --paragraph-spacing: 1.2em;
  --section-spacing: 4em;
  --max-reading-width: 36em;  /* 中文最佳阅读行宽 */
}

body {
  font-size: var(--body-font-size);
  line-height: var(--body-line-height);
  color: #1a1a1a;
  background: #f9f5ec;
  padding: 6em 2em 8em;   /* 上 6em 下 8em 呼吸 */
}

article {
  max-width: var(--max-reading-width);
  margin: 0 auto;
}

p + p {
  margin-top: var(--paragraph-spacing);
}
```

### 标题层级

```css
h1.book-title {
  font-size: 64px;
  text-align: center;
  margin: 3em 0 1em;
  letter-spacing: 0.2em;
  font-weight: normal;       /* 典雅风的标题不加粗 */
}

h2.chapter {                 /* 章：壹 贰 叁 */
  font-size: 48px;
  text-align: center;
  margin: 3em 0;
  letter-spacing: 0.15em;
  font-weight: normal;
  color: #8b3a3a;
}

h2.chapter::before {
  content: "";
  display: block;
  width: 2em;
  height: 1px;
  background: #c26d6d;
  margin: 0 auto 1em;
}

h2.chapter::after {
  content: "";
  display: block;
  width: 2em;
  height: 1px;
  background: #c26d6d;
  margin: 1em auto 0;
}

h3.section {                 /* 节：一 二 三 */
  font-size: 28px;
  margin: 2em 0 1em;
  font-weight: normal;
  border-left: 3px solid #8b3a3a;
  padding-left: 0.8em;
}

h4.subsection {              /* 小节 */
  font-size: 20px;
  margin: 1.5em 0 0.8em;
  font-weight: 600;
}
```

### 引用块

**原文引用（楷体）**：

```css
.quote-original {
  font-family: "Kaiti SC", "KaiTi", serif;
  background: #fcfaf4;
  padding: 1.2em 2em;
  border-left: 3px solid #8b3a3a;
  margin: 1.5em 0;
  font-size: 15px;
  color: #4a4a4a;
  line-height: 2.0;
}

.quote-original::before {
  content: "【原】";
  font-family: serif;
  color: #8b3a3a;
  font-weight: 600;
  margin-right: 0.5em;
}
```

**解读分析**：

```css
.analysis::before {
  content: "【析】";
  color: #8b3a3a;
  font-weight: 600;
  margin-right: 0.5em;
}
```

### 双栏对照（原文 vs 解读）

```css
.quote-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2em;
  margin: 2em 0;
  align-items: start;
}

@media (max-width: 720px) {
  .quote-pair {
    grid-template-columns: 1fr;
  }
}
```

### 侧栏批注

```css
.side-note {
  font-family: "Kaiti SC", serif;
  font-size: 14px;
  color: #8b3a3a;
  float: right;
  width: 8em;
  margin: 0 -10em 1em 1em;
  padding: 0.5em 0;
  border-left: 1px solid #c26d6d;
  padding-left: 0.8em;
  writing-mode: horizontal-tb;   /* 横排小批；竖排太难控 */
  line-height: 1.6;
}
```

在大屏幕上浮右展示；小屏幕隐藏或转为行内引用。

### SVG 全貌图

```css
.overview-svg, .fact-matrix-svg {
  display: block;
  margin: 4em auto;
  max-width: 100%;
  height: auto;
}

/* 水墨线条风 SVG 用这套颜色：*/
/* 线：#1a1a1a 细 1px；辅线 #8b3a3a 1px */
/* 填充：透明 或 #fcfaf4 */
/* 文字：宋体 14px 直接在 SVG 里 */
```

### 章节编号（汉字数字）

```
壹 贰 叁 肆 伍 陆 柒 捌 玖 拾
```

或：

```
一 二 三 四 五 六 七 八 九 十
```

不用阿拉伯数字 1 2 3（除非在数据/表格/年代里）。

## 三入口布局

```
┌──────────────────────────────────────────────┐
│  [📖 速读 · 15min] [📘 精读 · 1h] [📚 深读]    │
├──────────────────────────────────────────────┤
│                                              │
│  ( 根据选择显示不同密度的内容 )                 │
│                                              │
└──────────────────────────────────────────────┘

速读：只显示 meta + motif + overview_svg + memory_hook + golden_quotes
精读：上 + modules 的三重结构（浓缩版）
深读：上 + quote_pairs + external_counterpoints + misreadings + blindspots + thought_coordinates + toolbox
```

切换靠 CSS 类控制 display。不用 JS 框架，原生 JS 几行实现。

## SVG 水墨风的具体画法

### 原则

- **线条黑细**（stroke-width 1px，黑 #1a1a1a）
- **填充透明或淡宣**（fill: none 或 #fcfaf4）
- **朱砂点睛**（只用于中心/关键节点 #8b3a3a）
- **字体用 SVG 内宋体**（font-family: "Songti SC", serif）
- **构图留白**（SVG 宽 800，图形实际占 60%）

### 全貌图常见形式

**三角循环**（适合系统逻辑）：
```
       节点A
        / \
       /   \
      ↓     ↑
   节点B ← 节点C
```

**树形**（适合论证/分类）：
```
        主命题
       /  |  \
      子1 子2 子3
```

**时间轴**（适合叙事/史料）：
```
  ─────●─────●─────●─────●─────
       节点A 节点B 节点C 节点D
```

**矩阵**（适合人物/维度交叉）：
```
      维度1 | 维度2 | 维度3
   ╔════════╪════════╪════════╗
行1║  事实  │  事实  │  事实  ║
行2║  事实  │  事实  │  事实  ║
   ╚════════╧════════╧════════╝
```

## 排版的"呼吸"

### 章节之间

```
[正文最后一段]

     ━━━━━

    【 贰 】

[下一章正文]
```

用 `━━━━━` 或者朱砂分隔符做视觉呼吸。不用实线 hr。

### 段落内部

长段落之间可以放一行空白或一个居中的"·"：

```
[长段落1]

          ·

[长段落2]
```

## 视觉禁忌

- ❌ 渐变背景、背景图片（除非极简水墨）
- ❌ 阴影/立体按钮
- ❌ 动画（除了 tab 切换的轻度 fade）
- ❌ 图标 emoji 混入正文
- ❌ 彩色 tag/badge
- ❌ 网格线密集的表格（用空白分隔）
- ❌ 圆角 > 4px（典雅风偏直角）
- ❌ 霓虹色/对比强的色块

## 可访问性

- 对比度至少 4.5:1（墨 #1a1a1a on 宣 #f9f5ec 够）
- 标题有语义层级（h1 → h2 → h3）
- 图有 alt
- 响应式：36em 版心 + 720px 断点
