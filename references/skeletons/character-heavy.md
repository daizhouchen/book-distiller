# 骨架 · 人物基因主导（v2.1 加深版）

适用于以人物为核心的书：金瓶梅、红楼梦、乔布斯传、曾国藩传、百年孤独（兼）、活着（兼）等。

> 本骨架在 v1/v2 基础上按 `references/deepening-protocol.md` v2.1 增量加深。所有新增/强化条款都标注 `(per §N.M)`。v1/v2 字段全部保留——v2.1 是**累加加密度**而不是替换。
>
> **v2.1 主要变化**：模块数 8-10 → **10-12**；单模块字数 ≥2200 → **≥4500**（人物重模块 ≥6000）；每模块原文锚点 ≥3 → **≥6**，单条 ≥100 字；推导链 ≥3 → **≥4** 步；外部反例 ≥1 → **≥2**；新增 3 个专题字段（场景细读 / 人物小传 / 诗词专题）。

## 模块数（per §1.1）

**10-12 个核心模块**（人物为主基因的经典/巨著取上限 12，含 3 个新专题独立成模块）。本骨架以红楼梦/金瓶梅档（巨著人物书）为参考刻度，定 **12 个**为标刻。

## 模块顺序（v2.1）

1. 卷首 · 开篇 + 母题 + 记忆抓手 + 适用性判定
2. 全貌地图（SVG）
3. 人物剖面 × N
4. 关系拓扑（SVG）
5. **场景细读**（per §2.6 ⭐ v2.1 新，人物书 STRICT ≥5 条；巨著 ≥8）
6. **人物小传 dossier**（per §2.7 ⭐ v2.1 新，人物书 STRICT ≥5 人；巨著 ≥10）
7. **诗词曲赋专题**（per §2.8 ⭐ v2.1 新，含诗词的人物书 STRICT ≥3；现代传记可空）
8. 关键节点 · 推导链
9. 底层机制 · 系统逻辑
10. **学派论争**（per §2.1，人物型经典强制 ≥3 派）
11. **版本/钞本差异**（per §2.2，古典强制 ≥5 处）
12. **作者立场解构**（per §2.3，所有书强制）
13. **章节级覆盖**（per §2.4，长书 ≥12 回，每条 ≥600 字；中等 ≥8 主题）
14. 误读陷阱（≥6，per §1.5）
15. 时代的茧 · 作者盲点（≥6，per §1.6）
16. 金句精选（≥12，per §1.7）
17. **思想坐标 · 四维强化**（每维 ≥4，per §1.9-1.12）
18. 思考工具箱（折叠）

> 模块 14-18 为辅助/收尾区，统计模块数时按主章节计入 12 个。卷首+全貌+剖面+关系+场景+人物 dossier+诗词+节点+机制+学派+版本+作者解构 = 12 主模块（章节级/章节级以下都能并入主结构）。

## 新字段适用性（v2.1）

| 新字段 | 适用性 | 数量要求 |
|------|------|---------|
| `scene_dissections`（§2.6） | **STRICT** | ≥5 条（巨著 ≥8）；每条 ≥1000 字 |
| `character_dossiers`（§2.7） | **STRICT** | ≥5 人（巨著 ≥10 人）；每条 ≥600 字 |
| `poetics_dossiers`（§2.8） | **STRICT IF 含诗词曲赋**（如红楼/金瓶/史记列传赞）；现代传记 OPTIONAL | 含则 ≥3 篇；每条 ≥600 字 |

## 单模块共同硬下限（v2.1 全面提档）

每个核心模块的占位文本与最终产物都要满足：

- **字数 ≥ 4500 字**（per §1.2 v2.1；人物剖面/场景细读模块 ≥6000 字）
- **原文锚点（quote_pairs）≥ 6 组**（per §1.4 v2.1），每组双栏：原文 + 解读
- **每条原文锚点 original ≥ 100 字**（per §1.4b v2.1；巨著场景类锚点 ≥150 字）
- **每条 quote_pairs.analysis ≥ 80 字**（per §3）
- **外部反例 external_counterpoints ≥ 2**（per §1.13 v2.1）
- **viewpoint_layer 含 derivation_chain ≥ 4 步**（per §1.14 / §3 v2.1），每步显式 type=fact|mechanism|analogy|counterfact|synthesis|claim

## 各模块内容要求

### 1 · 卷首

- 一句话母题（≤ 30 字）
- 记忆抓手（metaphor，≤ 15 字）
- 信源构成比例 + 置信度
- 本次视角（lens 标注）
- v2.1 增量：**applicability_map** 显式列出 §4.1-§4.6 六条适用性判定（学派/版本/章节级/场景细读/人物小传/诗词专题），每条标 strict | downgrade | not_applicable + 一句话理由

### 2 · 全貌地图

- 内嵌 SVG，中心是母题词
- 周围放主要人物节点
- 线连接显示关系类型（姻亲/主仆/利害）
- 水墨线条风
- v2.1 增量：作为可视化类型 1（per §1.17 v2.1，至少 3 种 SVG）

### 3 · 人物剖面 × N

每个核心人物 ≥ **6000 字**（per §1.2 v2.1，"人物重模块 ≥6000"），按**三重结构**展开：

**事实层**（系统化的行为证据）：
- 关系域矩阵（情/钱/权/家庭/社交/信仰 × 时间）
- 每域 ≥ 5 个事实锚点，并入 fact_matrix 总 cells ≥ **20**（per §1.8 v2.1）
- 可视化为小型矩阵 SVG

**机制层**（从事实中浮现的规律）：
- 单域规律：这个人在 X 维度上的演化（递增/递减/循环/突变）
- 跨域交织：A 域和 B 域如何互相驱动
- 底层动力：为什么这样？

**观点层**（从机制得出的判断）：
- core_claim 一句话
- **derivation_chain ≥ 4 步**（per §3 v2.1），禁止"事实跳到结论"
  - step 1: fact 类——援引事实层证据
  - step 2: mechanism 类——揭示该事实背后的机制
  - step 3: analogy 或 counterfact 类——用第二条事实/类比/反事实闭环
  - step 4: synthesis 或 claim 类——综合得出最终判断
- modern_transfer：现代人能从他身上看到什么
- caveats：本判断的边界

**原文对照（quote_pairs）≥ 6 组双栏**（per §1.4 v2.1），每条 original ≥100 字
**外部视角对照 external_counterpoints ≥ 2**（per §1.13 v2.1）

### 4 · 关系拓扑

- 完整 SVG（节点=人物，边=关系）
- 至少标出三种关系类型
- 可显示关系的时间演化（多图）
- v2.1 增量：作为可视化类型 2 满足 §1.17（≥3 种）

### 5 · 场景细读 ⭐ v2.1 新增（per §2.6）

**适用性**：人物为主的小说/史书 **STRICT** ≥5 条；巨著（红楼/金瓶/源氏/百年孤独）≥8 条。

**硬下限**（适用时）：
- scene_dissections ≥ 5 条（巨著 ≥8）
- 每条**五层拆解**：blocking / language / sensorium / subtext / structural_function（详见 `references/scene-dissection-protocol.md`）
- 每条 original_text_excerpt ≥ 300 字
- key_close_reads ≥ 3 条，每条 reading ≥ 80 字
- echoes（与全书呼应）≥ 3 处
- 每条总字数 ≥ 1000 字
- 渲染为深读独占模块

### 6 · 人物小传 dossier ⭐ v2.1 新增（per §2.7）

**适用性**：人物为核心承载，**STRICT** ≥5 人（巨著 ≥10 人）。

**硬下限**：
- character_dossiers ≥ 5 人（巨著 ≥10）
- 每条 8 个子字段：name / tier(primary|secondary|minor_but_pivotal) / appearance_arc(≥150 字) / core_paradox(≤30 字) / key_scenes(≥3 条) / language_signature(≥80 字) / fate_pattern(≥150 字) / reading_through_lens(≥150 字)
- 详见 `references/character-dossier-protocol.md`
- 每条总字数 ≥ 600
- 渲染为深读独占模块

### 7 · 诗词曲赋专题 ⭐ v2.1 新增（per §2.8）

**适用性**：含诗词曲赋的人物书 **STRICT** ≥3 篇（红楼梦/金瓶梅/西游记/儒林外史/史记列传赞均触发）；现代传记 OPTIONAL，可空。

**硬下限**（适用时）：
- poetics_dossiers ≥ 3 篇
- 每条 8 个子字段：title / locus / speaker_or_voice / full_or_excerpt(≥150 字) / form_analysis(≥150 字) / content_analysis(≥200 字) / intertextual_anchors(≥2) / fate_foreshadowing(≥80 字)
- 详见 `references/poetics-dossier-protocol.md`
- 每条总字数 ≥ 600
- 渲染为深读独占模块

### 8 · 关键节点 · 推导链

- 选 3-5 个决定性事件
- 每个走"偶然因 + 必然因 + 蝴蝶效应"
- 每个事件 quote_pairs ≥ 6（per §1.4 v2.1）
- viewpoint_layer.derivation_chain ≥ 4 步（per §3 v2.1）

### 9 · 底层机制 · 系统逻辑

⭐ **整篇核心**，不可省略。

- 把各人物的行为规律汇总
- 找出跨人物的共同结构
- 画出"系统逻辑图"（SVG）
- 该模块的 derivation_chain 要把"个体规律 → 跨人物结构 → 全书系统 → 母题指向"显式串起来 ≥4 步（per §3 v2.1）
- 字数 ≥ 4500，quote_pairs ≥ 6（per §1.2/§1.4 v2.1）

### 10 · 学派论争（per §2.1）

**适用性**：strict for character-heavy 古典/经典（红楼/金瓶/水浒/三国/西游；堂吉诃德/源氏/追忆似水年华；任何 1900 年前还在被解读争论的人物书）。现代传记 → 降级到 misreadings.evaluation_split。

**硬下限**（适用时）：
- schools_of_interpretation ≥ 3 派（per §2.1）
- 每派含 school / core_position / key_figures / evidence_anchors / our_judgment
- 本模块字数 ≥ 4500（per §1.2 v2.1），quote_pairs ≥ 6（per §1.4 v2.1）
- 渲染为深读独占模块

### 11 · 版本/钞本差异（per §2.2）

**适用性**：strict for character-heavy 古典（红楼脂本 vs 程高本；史记不同钞本；莎翁四开 vs 对开）。现代传记可降级"修订版差异"或留空。

**硬下限**（适用时）：
- version_variants ≥ 5 处对照（per §2.2）
- 每处含 version_a / version_b / diff_locus / diff_content / interpretive_significance
- 本模块字数 ≥ 4500，quote_pairs ≥ 6（每组对照本身就是天然的双栏锚点）
- 渲染为深读独占模块

### 12 · 作者立场解构（per §2.3）

**适用性**：**所有书强制**——人物型尤其重要，因为作者塑造人物时的阶级/性别/知识立场决定哪些被照亮、哪些被遮蔽。

**硬下限**：
- author_position_deconstruction 含 class_position / knowledge_boundary / writing_motive_shadow（各 ≤30 字）
- evidence ≥ 3 条（per §2.3），每条标 facet=class|knowledge|motive，附 anchor + elaboration
- 本模块字数 ≥ 4500，quote_pairs ≥ 6
- 渲染为精读+深读可见

### 13 · 章节级覆盖（per §2.4 v2.1）

**适用性**：strict for character-heavy 长书（>30 万字，≥12 回）；中等长度书 ≥8 主题；短传记降"代表片段选粹" ≥5。

**硬下限**（适用时）：
- chapter_level_notes ≥ 12 回目（长书）/ ≥8 主题（中等）
- **每条 interpretation ≥600 字**（per §2.4 v2.1）——章节级是巨著之所以厚的核心承载
- 每条含 chapter / anchor_event / interpretation / cross_link
- 本模块总字数因此天然 ≥ 7200（12×600）；不必强求 4500 单一段落
- 渲染为深读独占模块

### 14 · 误读陷阱

**≥ 6 条**（per §1.5 v2.1）。

### 15 · 时代的茧 · 作者盲点

**≥ 6 条**（per §1.6 v2.1）。

### 16 · 金句精选

**≥ 12 条**（per §1.7 v2.1），原文直引，不改写，带章节定位。

### 17 · 思想坐标 · 四维强化（per §1.9-1.12 v2.1）

四维各 ≥ **4** 条，每条结构化（referenced_work / referenced_author / position / relation_to_book）：

- **同题延伸 ≥ 4**（per §1.9 v2.1）
- **对立视角 ≥ 4**（per §1.10 v2.1）
- **承继关系 ≥ 4**（per §1.11 v2.1）
- **现代回响 ≥ 4**（per §1.12 v2.1）

### 18 · 思考工具箱（折叠）

列本文思考时用过的框架，每个附"本文如何用"一句话。

## 总体密度要求（v2.1 全面提档）

- 总字数：≥ **20000**（深读 / 精读 ≥ 1.35×，per §1.16）
- distill.json 体积 ≥ **120KB**（巨著 ≥ 200KB，per §1.15 v2.1）
- 原文锚点总数 ≥ **50**（巨著 ≥ 80，per §1.3 v2.1）
- 单条原文锚点 ≥ 100 字（巨著场景类 ≥150 字，per §1.4b v2.1）
- 事实矩阵 cells ≥ **20**，每个带具体锚点（per §1.8 v2.1）
- 推导链：每模块 viewpoint_layer 显式 ≥ **4 步**（per §3 v2.1）
- SVG 图：≥ **3 种类型**（per §1.17 v2.1，矩阵 + 关系拓扑 + 时间轴/系统逻辑图任一）
- scene_dissections ≥5（巨著 ≥8），每条 ≥1000 字
- character_dossiers ≥5（巨著 ≥10），每条 ≥600 字
- poetics_dossiers（适用时）≥3 篇，每条 ≥600 字

## 禁忌（v2.1 强化）

- 不要把人物剖面写成"性格描写" → 必须有事实+机制+观点三重，且观点层有显式 derivation_chain ≥4 步
- 不要只写主角，忽略次要但关键的人（金瓶梅的应伯爵、韩道国；红楼的赵姨娘、贾环）—— v2.1 character_dossiers 必须含 minor_but_pivotal 层级
- 不要在模块里点名框架（留工具箱）
- 不要把场景细读模块当"摘抄+一两句解读"——必须 5 层全拆 + ≥1000 字（per §2.6）
- 不要把人物小传写成"人物简介百科条目"——core_paradox / language_signature / reading_through_lens 是灵魂字段，不可省（per §2.7）
- 不要把诗词专题当"诗作翻译"——形式分析 + 化用考据 + 命运预告三件套必须齐全（per §2.8）
- 不要把学派/版本/章节级模块留空当"豁免"——只有 §4 适用性规则明确说不适用才留空
- 不要让 derivation_chain 跳步或只走 3 步（事实直接跳结论 = quality_check 红，per §7）
- 不要让单条 quote_pairs.original 短于 100 字——锚点不是关键字搜索结果，是让读者看到上下文的小段落（per §1.4b）
