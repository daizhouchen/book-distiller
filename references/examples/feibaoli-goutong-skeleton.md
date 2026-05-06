# 示例 · 非暴力沟通 骨架（v2 加深版示范）

> **v2 加深版示范** —— 本文件已按 `references/deepening-protocol.md` 增量加深。v1 内容完整保留，文末 v2 增量段补全适用字段。本书是工具书，按 §4 适用性：学派论争 ❌不适用（工具书无学派之争，per §4.1）；版本变异 ❌不适用；作者立场 ✅强制；章节级 → 主题级降级（≥5 主题，per §4.3）；思想坐标 ✅四维。模型书的加深保持节制，不强塞。

基因：**模型(主) + 体验**

母题：**分离观察与评价**

记忆抓手：**把评价拆回观察**

## 预期骨架（distill.json 结构示意）

```yaml
meta:
  title: 非暴力沟通
  author: Marshall B. Rosenberg
  motif: 沟通失效的根源是评价混淆了观察——分开两者,沟通就回到平地
  motif_evidence:
    - 罗森堡开篇用"暴力就是对人的评价"定义框架
    - 书中 70% 的案例围绕"评价→冲突"到"观察→连接"的转变
    - 四步模型 OFNR 的第一步就是"Observation"
  genes: [model, experiential]
  source_mix:
    A: 0.5
    B: 0.2
    C: 0.2
    D: 0.1
  lens: balanced

memory_hook: 把评价拆回观察

overview_svg: |
  (SVG 四步流程：
    观察 → 感受 → 需要 → 请求
    每一步有"绕过去的陷阱" 显示为朱砂叉)

fact_matrix:
  dimensions:
    - 四步 [观察 / 感受 / 需要 / 请求]
    - 操作情境 [适用 / 边界 / 失效]
  cells:
    观察×适用: [日常对话 / 团队沟通 / 亲密关系]
    观察×边界: [法律纠纷场合 / 需要表态时]
    观察×失效: [PUA / 结构性暴力]
    # ...

modules:
  - title: 第一步 · 观察（Observation）
    gene: model
    facts_layer:
      # 罗森堡给出的正反例
      # 本书第几页第几章
      # 事实矩阵：具体对话 × 评价成分 × 纯观察版本
    mechanism_layer:
      single_dim_patterns:
        - 评价性词汇的典型结构（"总是/从不/懒/自私" 等）
        - 观察性描述的精确度（时间/行为/场景三要素）
      cross_dim_weaving: |
        观察不是冷静,是"把镜头对准事实本身"。
        这一步的难点在于：我们习惯在感知事实的同时就
        贴标签。把贴标签的动作延后,就是在给自己争取
        认知空间。
    viewpoint_layer:
      core_claim: 观察是全书的地基——其他三步都要建在这个地基上
      modern_transfer: 日常一天可以做 10 次"把评价拆回观察"的练习
      caveats: 绝对的"无评价"是不可能的,目标是减少评价,不是根除

  - title: 第二步 · 感受（Feeling）
    # 感受 vs 想法 的区分
    # 真感受（恐惧/悲伤/期待）vs 伪感受（觉得被/觉得不被）
    # 事实系统化：感受词库 × 具体身体信号

  - title: 第三步 · 需要（Need）
    # 需要 vs 策略
    # 人类共同的需要清单
    # 事实系统化：需要的层级

  - title: 第四步 · 请求（Request）
    # 请求 vs 命令
    # 可回应性 vs 开放性
    # 请求失败的典型模式

  - title: 适用情境 × 失效情境 矩阵
    # 专属模块：SVG 矩阵
    # 模型在哪些场景成立,哪些场景不适用

  - title: 实操剧本 · 伴侣吵架
    # 从暴力沟通版本 → 非暴力版本
    # 原文对照

  - title: 实操剧本 · 团队反馈
    # 上级对下级的情境
    # 权力不对等如何处理

  - title: 实操剧本 · PUA/霸凌情境的失效
    # 故意展示模型的边界
    # 如何识别"不适用时要退出而非继续"

  - title: 底层机制 · 模型背后的哲学
    # 罗森堡的预设世界观
    # 卢梭式的人性善 / 人本主义心理学
    # 为什么这个模型在"权力对等"时有效
    # 为什么在"结构性暴力"下无效

misreadings:
  - common_misread: 非暴力沟通是"说话技巧书"
    why_misread: 书名的误导 + 实用主义读者的需求
    actual: 它是一套"认知重构练习"——先改变看事物的方式,再改变说话

  - common_misread: "区分观察和评价"意味着不能评价
    why_misread: 字面理解
    actual: 罗森堡强调的是"感知时分开,表达时明确"——不是禁止评价

  - common_misread: 四步模型是万能沟通公式
    why_misread: 培训行业简化
    actual: 模型有明确的适用边界——权力对等、双方有意连接

blindspots:
  - limitation: 对"结构性暴力"的忽视
    evidence: 全书预设双方可以"好好谈",未充分讨论霸凌/PUA/阶级暴力情境
    boundary: 这些情境下单纯 NVC 不够,需要退出/边界/求助

  - limitation: 西方个体主义预设
    evidence: "我的感受" "我的需要" 话语结构,对集体文化有适应性问题
    boundary: 东方文化中的"我们"而非"我"的语境需要调整

  - limitation: 对冲突的"可解性"过度乐观
    evidence: 书中大部分案例都有"双方都愿意 NVC"的前提
    boundary: 现实中单方 NVC 常常面对"另一方不配合"

golden_quotes:
  - "暴力的根源在于人们忽视彼此的感受和需要,而将冲突归咎于对方"
  - "不带评论的观察是人类智力的最高形式"（引克里希那穆提）
  - "当我们专注于澄清观察、感受、需要和请求,而不评判他人时,爱的力量便会被激发"
  - （其他 3-5 条）

thought_coordinates:
  同题延伸:
    - 《少有人走的路》（派克）—— 相似的人本主义底座
    - 《刻意练习》—— 技能层面的补充
  对立视角:
    - 《影响力》（西奥迪尼）—— 另一种沟通观：如何合规地影响对方
    - 《反脆弱》—— 冲突有时是必要的,避免冲突有代价
  承继关系:
    - 卡尔·罗杰斯的人本主义心理学
    - 克里希那穆提的"纯粹观察"
  现代回响:
    - 家庭治疗领域的"情感聚焦疗法"
    - 职场"反馈文化"的兴起

toolbox:
  - 格式塔（图-底） —— 理解为什么观察需要"把标签做背景,把事实做前景"
  - 认知行为疗法 —— 与 NVC 的"想法-感受"区分有同构
  - 依恋理论 —— 解释为什么有人更难表达真实需要
  - 非对称权力理论 —— 为什么 NVC 在结构性不平等下失效
  - 萨提亚家庭治疗的一致性沟通 —— NVC 的亲戚模型
```

## 这份骨架的关键点

1. **模型型书的结构专属**：不是人物剖面，是模型步骤分解
2. **适用/失效矩阵是核心**：模型型书最重要的就是**边界清晰**
3. **实操剧本必备**：让读者看到落地后的样子
4. **诚实暴露边界**：为什么在 PUA 下不适用，必须说
5. **系统逻辑 = 模型的哲学底座**：人本主义预设的暴露

---

## v2 加深增量段（per `references/deepening-protocol.md`）

工具书的 v2 加深保持节制——不强塞学派与版本字段，把空间留给作者立场、主题级章节、思想坐标四维。

### v2.1 · `schools_of_interpretation`（per §2.1，工具书不适用）

```yaml
schools_of_interpretation:
  applicability_note: |
    工具书无学派之争，按 §4.1 不适用，留空。
    模型类工具书的"评价分歧"应放在 misreadings.evaluation_split 中处理。
  schools: []
```

### v2.2 · `version_variants`（per §2.2，工具书不适用）

```yaml
version_variants:
  applicability_note: |
    工具书单一版本，按 §4.2 不适用，留空。
    本书有中英文版差异，但属翻译细微差，不构成解读分歧，故不立项。
  variants: []
```

### v2.3 · `author_position_deconstruction`（per §2.3，所有书强制）

```yaml
author_position_deconstruction:
  class_position: 美式中产 / 临床心理学博士 / 受人本主义心理学训练的西方知识分子
  knowledge_boundary: 临床心理学、人本主义、调解实践精通；缺乏对结构性暴力、权力不对等情境的理论训练
  writing_motive_shadow: 把"沟通技术"普世化的强烈热忱 + 美国 1960-70 年代社会运动失败后转向个体修复的时代背景
  evidence:
    - facet: class
      anchor: 罗森堡的成长背景（底特律种族冲突的童年记忆）+ 后来的临床培训
      elaboration: 他对"暴力源于未被听见"有亲身体察，但他的方法论根基是个体心理咨询的诊室，不是结构性暴力的现场
    - facet: knowledge
      anchor: 全书引用主要来自卡尔·罗杰斯（人本主义）、克里希那穆提（精神导师）
      elaboration: 罗森堡的知识结构里几乎没有政治理论、社会学、女性主义、批判理论——这决定了他对"权力"问题的处理偏弱
    - facet: motive
      anchor: 全书反复强调"我们都有美好的内在""暴力是悲剧而非邪恶"
      elaboration: 这种"善意预设"是 NVC 的力量来源，也是它的边界——在面对结构性恶时，善意预设可能成为一种"道德绑架"
```

### v2.4 · `chapter_level_notes` → 主题级降级（per §2.4，工具书 ≥5 主题）

```yaml
chapter_level_notes:
  applicability_note: 本书 200 页左右，按 §4.3 降级为主题级 ≥5 主题（即 4 步法 + 边界主题）
  themes:
    - chapter: 主题一 · 观察（Observation）
      anchor_event: 罗森堡引克里希那穆提"不带评论的观察是人类智力的最高形式"
      interpretation: 观察是全书的基础步骤。难点在于人类习惯在"感知事实"的同时贴标签——把贴标签延后是给自己争取认知空间。罗森堡用大量"观察 vs 评价"对照例子（如"他从不打扫"= 评价；"他这周三天没打扫"= 观察）训练读者的辨认力。
    - chapter: 主题二 · 感受（Feeling）
      anchor_event: 真感受 vs 伪感受（"我觉得被忽视"是想法不是感受）
      interpretation: 第二步要求把"想法乔装成感受"的话剥离出来。"觉得被X"通常不是感受，而是判断+评价。真感受是身体可定位的（紧、酸、热、空），罗森堡建议读者建立"感受词库"，扩展可识别的真感受。
    - chapter: 主题三 · 需要（Need）
      anchor_event: 需要 vs 策略
      interpretation: 第三步把感受连接到普世需要（被看见、归属、自主、安全等）。罗森堡借马斯洛理论强调需要是普世的，但满足需要的策略可以多种多样。把"我要你做X"（策略）翻译为"我有Y需要"（需要）能打开协商空间。
    - chapter: 主题四 · 请求（Request）
      anchor_event: 请求 vs 命令
      interpretation: 第四步是落地动作。请求必须可回应（具体、可拒绝、有时间锚）。命令则不允许拒绝。罗森堡强调请求被拒绝时不要切换为命令——这是 NVC 与"沟通技巧书"的根本分野。
    - chapter: 主题五 · 模型的边界与失效情境
      anchor_event: 罗森堡承认 NVC 在"权力不对等""结构性暴力"下不充分
      interpretation: 这是工具书自我边界的诚实声明。NVC 预设双方都"愿意被听见"，在 PUA、霸凌、阶级压迫等情境下，单纯 NVC 不够，需要退出/边界/求助。理解模型的失效情境，比掌握模型本身更重要。
```

### v2.5 · 强化 `thought_coordinates`（四维各 ≥3）

```yaml
thought_coordinates:
  同题延伸:
    - referenced_work: 人性的弱点
      referenced_author: 戴尔·卡耐基
      position: 同为沟通方法论的经典，但走"如何赢得人心"的策略路径
      relation_to_book: 卡耐基从社交策略入手，罗森堡从内心觉察入手；两书构成"沟通学"两条路径
    - referenced_work: 沟通的艺术
      referenced_author: 罗纳德·阿德勒
      position: 大学传播学教材，覆盖更广的沟通理论
      relation_to_book: 阿德勒书是教科书式的全景，NVC 是单一方法论的深入；前者面广，后者刀深
    - referenced_work: 少有人走的路
      referenced_author: M·斯科特·派克
      position: 同样源于人本主义心理学，强调"对自我的诚实"
      relation_to_book: 派克和罗森堡共享卡尔·罗杰斯的理论根基，是同一精神谱系
  对立视角:
    - referenced_work: 影响力
      referenced_author: 罗伯特·西奥迪尼
      position: 沟通的"策略主义"——如何合规地影响对方
      relation_to_book: 西奥迪尼研究"如何让对方做我想做的事"，罗森堡研究"如何让双方真正连接"——根本目的不同
    - referenced_work: 博弈论经典（如《策略思维》）
      referenced_author: 托马斯·谢林等
      position: 把沟通当博弈
      relation_to_book: 博弈论假设双方都是策略行动者，NVC 假设双方都愿意诚实——前提截然相反
    - referenced_work: 反脆弱
      referenced_author: 塔勒布
      position: 冲突有时是必要的，避免冲突有代价
      relation_to_book: 塔勒布的"杠铃策略"在沟通领域的对应是"该硬时硬"，与 NVC 的"温和优先"形成张力
  承继关系:
    - referenced_work: 卡尔·罗杰斯《以人为中心的治疗》
      referenced_author: 卡尔·罗杰斯
      position: 人本主义心理学的奠基
      relation_to_book: 罗森堡是罗杰斯的直接继承者，NVC 是罗杰斯"无条件积极关注"在沟通领域的具体化
    - referenced_work: 克里希那穆提的"觉察"哲学
      referenced_author: 克里希那穆提
      position: "不带评判的观察"
      relation_to_book: 罗森堡明确引用克氏，把"觉察"概念落地为可操作的 4 步
    - referenced_work: 萨提亚家庭治疗的一致性沟通
      referenced_author: 弗吉尼亚·萨提亚
      position: 家庭治疗领域的近亲方法
      relation_to_book: 萨提亚的"一致性表达"与 NVC 的"诚实表达"高度同构，可视为同一传统的两个分支
  现代回响:
    - referenced_work: 教练学（Coaching）行业
      referenced_author: 国际教练联合会等
      position: 把"提问 + 倾听"作为核心方法
      relation_to_book: 现代教练学的核心方法（强力提问、积极倾听）与 NVC 高度兼容，是 NVC 在职场领域的延伸
    - referenced_work: 正念沟通（Mindful Communication）
      referenced_author: 卡巴金、Susan Gillis Chapman 等
      position: 把正念修行与沟通技术结合
      relation_to_book: 正念沟通是 NVC 与佛家正念修行的混合产物，扩展了 NVC 的精神维度
    - referenced_work: 情感聚焦疗法（EFT）
      referenced_author: 苏珊·约翰逊
      position: 家庭/伴侣治疗领域的当代主流
      relation_to_book: EFT 把"情感识别 + 互动循环"作为治疗核心，与 NVC 的"感受 + 需要"高度同构
```

以上为 v2 加深增量。原 v1 内容保留不动。工具书加深的克制原则：宁缺勿滥，不强塞学派 / 版本字段。
