# 示例 · 金瓶梅 骨架（v2 加深版示范）

> **v2 加深版示范** —— 本文件已按 `references/deepening-protocol.md` 增量加深。v1 内容完整保留，文末 v2 增量段补全 5 个新字段。金瓶梅是古典名著，按 §4 适用性，5 个字段除"章节级"为长书强制外，其他三项（学派 / 版本 / 作者立场）均触发。

基因：**人物(主) + 叙事 + 史料**

母题：**欲望的自噬循环**

记忆抓手：**一条吞吃自己尾巴的蛇**

## 预期骨架（distill.json 结构示意）

```yaml
meta:
  title: 金瓶梅
  author: 兰陵笑笑生（托名）
  motif: 欲望的自噬循环——追逐越多，被吞噬越深
  motif_evidence:
    - 西门庆 33 岁暴毙，死因直接指向纵欲（第 79 回）
    - 全书出现"银子"一词 800+ 次，每次追金之后必有一次追情
    - 从官哥死到李瓶儿亡，再到西门庆死，形成"获得即失去"链条
  genes: [character, narrative, historical]
  source_mix:
    A: 0.55
    B: 0.25
    C: 0.15
    D: 0.05
  lens: balanced

memory_hook: 欲望是吞食自尾的蛇

overview_svg: |
  (SVG 显示三角循环：情欲 → 钱欲 → 权欲，中间有一条蛇咬尾)

fact_matrix:
  dimensions:
    - 关系域 [情 / 钱 / 权 / 家庭 / 社交]
    - 时间阶段 [前 30 回 / 中 40 回 / 后 30 回]
  cells:
    情×前: [与金莲勾搭(1-6回) / 娶瓶儿(17-19回) / 占有式猛烈]
    情×中: [家妾群的消费化(27回葡萄架 / 33回玉箫) / 物化]
    情×后: [宋惠莲(22-26)/王六儿(37+)/如意儿(51+) 日益麻木]
    钱×前: [典当铺起家(第1回回忆) / 生药铺 / 花子虚家产吞并]
    钱×中: [缎铺开张(第45回) / 西门庆做了提刑千户后收钱无忌]
    钱×后: [资金空转,看似富有实则透支]
    权×前: [巴结县官 / 买通差役]
    权×中: [拜蔡京为义父(30回) / 做了千户(30回末)]
    权×后: [参与更高层政治 / 但未真正进阶]
    家庭×前: [吴月娘偏宠→李瓶儿进门争宠]
    家庭×中: [官哥出生(30回)到夭折(59回) / 金莲的伏笔]
    家庭×后: [孙雪娥被卖 / 家族离心]
    社交×前: [十兄弟结拜 / 应伯爵登场]
    社交×中: [十兄弟变酒肉帮闲]
    社交×后: [西门庆死后作鸟兽散]

modules:
  - title: 西门庆 · 欲望的三面体
    gene: character
    facts_layer:
      # 按情/钱/权/家/社交系统化
    mechanism_layer:
      single_dim_patterns:
        - 情：占有 → 消费 → 麻木（递减规律）
        - 钱：积累 → 投资 → 空转（边际效用递减）
        - 权：买通 → 攀附 → 停滞（天花板）
      cross_dim_weaving: |
        情欲驱动钱欲消耗，钱欲消耗驱动权欲保护，
        权欲保护又放大情欲空间——三位一体，自我闭环。
        但闭环不是稳定结构，而是螺旋下坠：
        每一轮都比上一轮需要更大的剂量。
    viewpoint_layer:
      core_claim: 西门庆不是道德反面人物，是一个被自己的欲望系统驱动的能动者
      modern_transfer: 他今天可能是某个财富新贵：早期雄心，中期豪奢，后期空洞，最终在自我消耗中倒下
      caveats: 不是所有追求物质的人都会走到这一步——他的特殊性在于"没有任何外部拉扯"

  - title: 潘金莲 · 一个被系统压成凶器的人
    # 略

  - title: 李瓶儿 · 柔性能否活下来的实验
    # 略

  - title: 吴月娘 · 正统视角的缺席
    # 略

  - title: 应伯爵与十兄弟 · 帮闲经济学
    # 略

  - title: 关键节点 · 官哥之死
    # 详细推导

  - title: 关键节点 · 李瓶儿病亡
    # 详细推导

  - title: 关键节点 · 西门庆暴毙
    # 详细推导

  - title: 底层机制 · 欲望的自噬循环
    # 系统逻辑总章
    # 包含完整的 SVG 三角图

misreadings:
  - common_misread: 金瓶梅是"黄书"，主要价值在性描写
    why_misread: 古代禁书+明清道学家定性+现代通俗读物营销
    actual: 性描写占比不足 15%，全书核心是商人家族的经济行为与人际结构
  - common_misread: 金瓶梅是"谴责小说"，讽刺封建腐朽
    why_misread: 鲁迅《中国小说史略》定位影响
    actual: 作者的态度比"讽刺"更复杂，有同情也有迷恋
  - common_misread: 金瓶梅是"市民文学的崛起"，讴歌世俗
    why_misread: 新派文学评论的浪漫化
    actual: 作者对世俗的描摹精细,但对世俗的毁灭性一面同样精细,不是单向讴歌

blindspots:
  - limitation: 对经济崛起的商人阶层为何没能形成独立政治力量,缺乏结构性分析
    evidence: 西门庆死后财富迅速散失,作者用"因果报应"解释,未进一步追问制度原因
    boundary: 读者需要补读何炳棣等学者对明代商业史的研究
  - limitation: 作者对女性人物的处置有道学家惯性
    evidence: 潘金莲/李瓶儿等女性的结局普遍"应得",体现了作者对女性能动性的半克制
    boundary: 现代读者可补读关于明代女性史的学术研究

golden_quotes:
  - 富贵必因奸巧得，功名全仗邓通成——【回前诗，资本逻辑的自白】
  - 西门庆笑道："咱闻那佛祖西天，也止不过要黄金铺地……"——【第 57 回，他对佛的唯一定义是金色】
  - （其他 5-8 条）

thought_coordinates:
  同题延伸:
    - 红楼梦（从欲望到幻灭的另一种版本）
    - 儒林外史（士人的同类机制）
  对立视角:
    - 《明代社会经济史》（何炳棣）—— 给出制度层解释
  承继关系:
    - 影响了《红楼梦》《儒林外史》《海上花列传》
  现代回响:
    - 《繁花》（金宇澄）的上海商业精神背景

toolbox:
  - 边际效用递减 —— 用来看情欲消费的累进麻木
  - 社会交换论 —— 理解十兄弟的帮闲经济
  - 布迪厄场域 —— 西门庆在官场上永远是场外人
  - 防御机制（升华失败） —— 他无法把欲望升华,只能原路反噬自己
  - 韦伯的新教伦理反面 —— 没有经过信仰规训的资本是如何自毁的
```

## 这份骨架的关键点

1. **母题驱动**：所有内容服务于"欲望的自噬循环"
2. **事实系统化**：关系域 × 时间阶段矩阵全填
3. **三重结构**：每个人物/节点都有事实+机制+观点
4. **系统逻辑显性**：底层机制章节有完整 SVG
5. **诚实**：误读陷阱 3 条、作者盲点 2 条
6. **框架内化**：toolbox 在最后才出现框架名

这是"该书应有的骨架"，不是最终输出。最终 HTML 由 render.py 根据完整 distill.json 生成。

---

## v2 加深增量段（per `references/deepening-protocol.md`）

以下为 v1 骨架之上的累加内容，仅补全 v2 5 个新字段。schema 字段名严格对齐 §2.1-§2.5。

### v2.1 · `schools_of_interpretation`（per §2.1，金瓶梅强制 ≥3 派）

```yaml
schools_of_interpretation:
  - school: 金瓶脂评派（张评派为代表）
    core_position: 以张竹坡评批为正解，全书是世情小说的范本而非淫书
    key_figures: [张竹坡（清初评点家）, 文龙（晚清续评者）]
    evidence_anchors:
      - source: 张竹坡《批评第一奇书金瓶梅》总论
        summary: 张氏明示金瓶梅是"史公之笔"，揭出经济、世情、人性的全息标本
      - source: 张评本各回回评
        summary: 张氏对每回的细读建立了金瓶梅作为"世情第一书"的解读框架
    our_judgment: 部分采纳——张竹坡的"世情说"奠定了正解地基，但其道学家立场对女性的处置仍带评价偏见

  - school: 文学派（鲁迅至当代文学批评一脉）
    core_position: 金瓶梅是中国白话小说从神怪英雄走向世情写实的关键转折
    key_figures: [鲁迅（《中国小说史略》）, 郑振铎, 吴晗, 刘辉]
    evidence_anchors:
      - source: 鲁迅《中国小说史略》"明之人情小说"
        summary: 鲁迅定位金瓶梅为"人情小说"开山之作，强调其文学史地位
      - source: 吴晗《金瓶梅的著作时代及其社会背景》
        summary: 把金瓶梅放在明代中后期社会经济史框架中重读
    our_judgment: 采纳——文学派把金瓶从"禁书 / 淫书"标签中解放出来，是当代正典化的主力

  - school: 历史派（社会经济史解读）
    core_position: 金瓶梅是明代中后期商业资本萌芽的史料标本
    key_figures: [何炳棣, 黄仁宇, 韩书瑞, 卜正民]
    evidence_anchors:
      - source: 何炳棣《明代商业史》相关章节
        summary: 西门庆的商业行为（生药铺、典当铺、缎铺）是明代地方商人崛起的典型
      - source: 黄仁宇《十六世纪明代中国之财政与税收》
        summary: 西门庆与官府的金钱往来反映明代后期财政腐败结构
    our_judgment: 采纳——历史派为金瓶梅提供了不可替代的制度背景，本骨架的"作者盲点"模块直接受此派启发
```

### v2.2 · `version_variants`（per §2.2，金瓶梅强制 ≥5 处）

```yaml
version_variants:
  - version_a: 词话本（万历刻本《金瓶梅词话》）
    version_b: 崇祯本（《新刻绣像批评金瓶梅》）
    diff_locus: 第 1 回开篇
    diff_content: 词话本以"景阳冈武松打虎"开场（沿袭水浒），崇祯本删去武松打虎、改以"西门庆热结十兄弟"开篇
    interpretive_significance: 崇祯本的删改让金瓶梅从"水浒外传"独立为"市井家族小说"，叙事重心从英雄转到世情

  - version_a: 词话本
    version_b: 崇祯本
    diff_locus: 全书韵文（词曲）的处理
    diff_content: 词话本保留大量曲牌、韵文（来源于明代曲词风格），崇祯本大量删除韵文、节奏更紧凑
    interpretive_significance: 词话本保留了明代说书曲词传统，崇祯本是"小说化"的进一步推进；二者代表两种艺术取向

  - version_a: 崇祯本
    version_b: 张评本（张竹坡批评第一奇书本）
    diff_locus: 全书章回回目与文字润饰
    diff_content: 张评本在崇祯本基础上做了大量文字润色与回目改造，更"文人化"
    interpretive_significance: 张评本是清代文人重塑金瓶梅的产物，影响最大但离作者原貌最远

  - version_a: 词话本
    version_b: 张评本
    diff_locus: 第 79 回西门庆死前细节
    diff_content: 词话本对西门庆纵欲过度致死的过程描写更直白、医学细节更多；张评本进行了一定程度的删改与雅化
    interpretive_significance: 不同版本对"性—死"因果链的处理体现各自的道德立场

  - version_a: 词话本
    version_b: 崇祯本
    diff_locus: 第 100 回结尾普静度脱孝哥
    diff_content: 词话本结尾的因果报应叙述更详尽（孝哥即西门庆托生）；崇祯本对此简化处理
    interpretive_significance: 词话本结尾的"佛家转生说"是作者命运观的明示；崇祯本的简化弱化了这一哲学维度

  - version_a: 词话本
    version_b: 崇祯本
    diff_locus: 性描写的密度与显隐
    diff_content: 词话本的性描写更密集、更直白；崇祯本进行了删节，但保留主要情节
    interpretive_significance: 这是版本史上最受关注的差异，反映明清之间道德标准的变迁
```

### v2.3 · `author_position_deconstruction`（per §2.3，所有书强制）

```yaml
author_position_deconstruction:
  class_position: 受过良好教育的失意文人 / 与商业世界保持观察距离
  knowledge_boundary: 精通明代市井细节、商业流程、官场潜规则；缺乏制度史的结构性视野
  writing_motive_shadow: 既迷恋世俗的精微肌理，又预设了"恶有恶报"的道学结局
  evidence:
    - facet: class
      anchor: 全书对商业账目、家用开支、当铺典质等细节的精准把握
      elaboration: 作者必然有过深度接触商业世界的经历，但叙述视角始终保持文人的"观察者"位置
    - facet: knowledge
      anchor: 第 30 回西门庆攀附蔡京、第 70 回林太太情节
      elaboration: 作者对官场潜规则的把握极细，但缺乏对帝制结构的批判性追问，只能用"因果报应"收尾
    - facet: motive
      anchor: 全书结局的因果报应安排（第 100 回普静度脱）
      elaboration: 作者对世俗的描摹精微，但又用佛家因果给世俗贴上"必败"标签，这种张力正是兰陵笑笑生的双重位置
```

### v2.4 · `chapter_level_notes`（per §2.4，金瓶梅 100 回 >30 万字，强制 ≥8 回）

```yaml
chapter_level_notes:
  - chapter: 第 1 回 · 西门庆热结十兄弟（崇祯本起首）
    anchor_event: 十兄弟结拜，奠定西门庆的社交底盘
    interpretation: 第 1 回为整部书定下"商业 + 江湖 + 官场"三重交织的世情底色。十兄弟看似义气，实为"帮闲经济"的雏形；其中应伯爵作为帮闲首领的位置贯穿全书，与西门庆的兴衰同步。
    cross_link: 与第 79 回西门庆死后十兄弟"作鸟兽散"形成完整闭环
  - chapter: 第 6 回 · 何九叔送殡 武大郎之死
    anchor_event: 武大郎被毒杀，西门庆与潘金莲奸情结成
    interpretation: 此回是西门庆道德下行的起点。毒杀武大郎是全书因果链的源头，作者特意让何九叔保留骨头作物证——为日后武松归来报仇埋下种子。
    cross_link: 与第 87 回武松杀嫂呼应
  - chapter: 第 13-14 回 · 李瓶儿过墙
    anchor_event: 李瓶儿背着花子虚与西门庆勾结，并将丈夫的财产带过门
    interpretation: 此回演示"金钱与情欲交织"的核心机制。李瓶儿的过墙不仅是情感选择，更是财产转移；花子虚的死与西门庆吞并花家产业是同一动作。
    cross_link: 与第 17 回娶瓶儿、第 62 回瓶儿病亡构成"瓶儿之线"
  - chapter: 第 27 回 · 葡萄架下
    anchor_event: 西门庆与潘金莲的著名性场景
    interpretation: 第 27 回是性描写最浓烈的一回，但其文学功能不是"色"，而是"权力 + 占有 + 物化"的展演。葡萄架场景的奢侈布置（绫罗绸缎、金银器物）暗示性已被资本化。
    cross_link: 与第 79 回西门庆精尽人亡形成因果
  - chapter: 第 30 回 · 西门庆做了千户
    anchor_event: 西门庆通过攀附蔡京获得提刑千户官位
    interpretation: 此回是西门庆社会地位的顶峰。商人通过送礼获得官职——这是明代后期"商→官"通道的具体化。但官位也意味着新的费用与责任，盛极转衰由此酝酿。
    cross_link: 与第 1 回十兄弟、第 79 回死亡构成弧线
  - chapter: 第 59 回 · 官哥之死
    anchor_event: 西门庆唯一的儿子官哥被潘金莲驯养的猫吓死
    interpretation: 官哥之死是家庭崩塌的预兆。作者通过"猫"这一日常细节完成因果链——潘金莲的嫉妒不直接出手，而是借猫之力间接致死。这是金瓶梅最精微的"非线性因果"叙事。
    cross_link: 与第 62 回瓶儿病亡（直接由官哥死引发）紧密相连
  - chapter: 第 62 回 · 李瓶儿病亡
    anchor_event: 瓶儿因官哥之死悲痛过度，加之内血崩之症，死于西门庆面前
    interpretation: 瓶儿之死是西门庆情感生命的第一次重创，也是全书最长的死亡场景。作者用极细腻的笔墨写西门庆的真情——这是他作为"恶人"也有人性的复杂性证明。
    cross_link: 与第 79 回西门庆自己之死遥相呼应
  - chapter: 第 79 回 · 西门庆暴毙
    anchor_event: 西门庆纵欲过度，精尽人亡
    interpretation: 第 79 回是全书命运链条的总爆发。西门庆 33 岁暴毙，死时家中尚在收账、铺面尚在营业——"鲜花着锦"瞬间转为"烈火烹油"。作者用"死"给"欲望自噬循环"画下句号。
    cross_link: 与第 1 回起家、第 100 回普静度脱形成全书三段式
```

### v2.5 · 强化 `thought_coordinates`（per §2.5 / §1.9-1.12，四维各 ≥3）

```yaml
thought_coordinates:
  同题延伸:
    - referenced_work: 红楼梦
      referenced_author: 曹雪芹
      position: 从欲望到幻灭的另一种版本，把"家族崩塌"母题诗意化
      relation_to_book: 红楼明确继承金瓶的家族崩塌叙事，脂砚斋说曹雪芹"深得金瓶壸奥"
    - referenced_work: 儒林外史
      referenced_author: 吴敬梓
      position: 士人世界的同类崩塌机制
      relation_to_book: 金瓶写商人，儒林写士人，两书同为明清世情的两面镜子
    - referenced_work: 海上花列传
      referenced_author: 韩邦庆
      position: 妓院世界的世情书写
      relation_to_book: 海上花在叙事密度、人物群像、世情精微上直接师承金瓶
  对立视角:
    - referenced_work: 明代社会经济史
      referenced_author: 何炳棣
      position: 给出制度层、结构性的解释
      relation_to_book: 金瓶用因果报应解释贾府败落，制度史视角则用商人阶层政治通道阻塞解释
    - referenced_work: 三国演义
      referenced_author: 罗贯中
      position: 英雄史诗叙事，与金瓶世情叙事形成对极
      relation_to_book: 三国造英雄、金瓶解英雄；两书代表中国白话小说的两个方向
    - referenced_work: 西游记
      referenced_author: 吴承恩
      position: 修行叙事，与金瓶纵欲叙事相反
      relation_to_book: 西游用"克欲"通向解脱，金瓶展示"纵欲"通向毁灭
  承继关系:
    - referenced_work: 水浒传
      referenced_author: 施耐庵
      position: 金瓶的直接母本（武松潘金莲段是水浒外传）
      relation_to_book: 金瓶从水浒第 24-26 回扩展而来，但走向了完全不同的方向
    - referenced_work: 三言二拍
      referenced_author: 冯梦龙、凌濛初
      position: 同期世情小说传统
      relation_to_book: 金瓶与三言二拍共同构成明代后期市井文学的高峰
    - referenced_work: 红楼梦 / 儒林外史 / 海上花
      referenced_author: 曹雪芹 / 吴敬梓 / 韩邦庆
      position: 后来者
      relation_to_book: 三部书都不同程度继承金瓶的世情叙事方法
  现代回响:
    - referenced_work: 繁花
      referenced_author: 金宇澄
      position: 上海商业精神的当代书写
      relation_to_book: 繁花的世情密度、人物群像方法直接接续金瓶传统
    - referenced_work: 尤利西斯（西方对照）
      referenced_author: James Joyce
      position: 西方世情主义高峰
      relation_to_book: 与金瓶同样追求"日常细节的精微书写"，可作为东西方世情写作的对照
    - referenced_work: 当代电视剧《新水浒传》《金瓶梅 96 版》等改编
      referenced_author: 多位导演
      position: 影视改编对原著的现代诠释
      relation_to_book: 改编多偏向情色化处理，未能传达原著的世情深度——这本身就是一个误读现象
```

以上为 v2 加深增量。原 v1 内容（modules / misreadings / blindspots / golden_quotes / toolbox）保留不动。distill.json 在加深时将以上 5 个字段并入。
