#!/usr/bin/env python3
"""
quality_check.py — 对 distill.json / 生成的 HTML 做质量检查

使用：
    python scripts/quality_check.py <distill.json>
    python scripts/quality_check.py <distill.json> <rendered.html>
    python scripts/quality_check.py --legacy <distill.json>     # v1 阈值（向后兼容）

检查项（见 SKILL.md 步骤 8 + deepening-protocol §1-§3 v2.1）：
- v1 硬红线：结构完整性 / 禁词 / 框架名 / 三层结构（始终强制）
- v2 加深版警告：v2 协议下的中间档加深检查（保留作 v2.0 产物的对照基线）
- v2.1 加深版警告：v2.1 协议下的全面提档（模块数 ≥10 / 单模块 ≥4500 字 /
  quote_pairs ≥50 / 单 quote.original ≥100 字 / 推导链 ≥4 步 / 误读盲点 ≥6 /
  金句 ≥12 / 事实矩阵 cells ≥20 / 思想坐标四维各 ≥4 / 外部反例 ≥2 等）
- v2.1 适用性提示：scene_dissections / character_dossiers / poetics_dossiers
  三个新字段按 §4.4-§4.6 适用性触发（缺失 warn 不 fail）
"""

import json
import re
import sys
from pathlib import Path


# ─── v1 阈值（保留作向后兼容） ────────────────────────
V1_MIN_QUOTE_PAIRS = 6
V1_MIN_MISREADINGS = 2
V1_MIN_BLINDSPOTS = 2
V1_MIN_GOLDEN_QUOTES = 5
V1_MIN_MODULES = 6

# ─── v2.0 加深版阈值（保留作 v2.0 产物对照基线） ────────
V2_MIN_QUOTE_PAIRS = 30             # §1.3 v2 列
V2_MIN_MISREADINGS = 5              # §1.5 v2 列
V2_MIN_BLINDSPOTS = 5               # §1.6 v2 列
V2_MIN_GOLDEN_QUOTES = 8            # §1.7 v2 列
V2_MIN_MODULES = 8                  # §1.1 v2 列
V2_MIN_MODULE_CHARS = 2200          # §1.2 v2 列
V2_MIN_FACT_MATRIX_CELLS = 16       # §1.8 v2 列
V2_MIN_THOUGHT_COORD_PER_DIM = 3    # §1.9-1.12 v2 列
V2_MIN_PER_MODULE_QUOTE_PAIRS = 3   # §1.4 v2 列
V2_MIN_DERIVATION_CHAIN_STEPS = 3   # §1.14 v2 列
V2_MIN_EXTERNAL_COUNTERPOINTS = 1   # §1.13 v2 列
V2_MIN_CHAPTER_NOTES = 8            # §2.4 v2 列

# ─── v2.1 加深版阈值（CONSTANTS · 见 deepening-protocol §1 v2.1 列） ────
MIN_QUOTE_PAIRS = 50                # §1.3 总锚点（巨著 ≥80）
MIN_MISREADINGS = 6                 # §1.5
MIN_BLINDSPOTS = 6                  # §1.6
MIN_GOLDEN_QUOTES = 12              # §1.7
MIN_MODULES = 10                    # §1.1（10-12）
MIN_MODULE_CHARS = 4500             # §1.2 单模块正文字数（人物/场景重模块 ≥6000）
MIN_FACT_MATRIX_CELLS = 20          # §1.8
MIN_THOUGHT_COORD_PER_DIM = 4       # §1.9-1.12
MIN_PER_MODULE_QUOTE_PAIRS = 6      # §1.4
MIN_QUOTE_ORIGINAL_CHARS = 100      # §1.4b 单条 quote.original 中文字数
MIN_DERIVATION_CHAIN_STEPS = 4      # §1.14 / §3
MIN_EXTERNAL_COUNTERPOINTS = 2      # §1.13
MIN_AUTHOR_POS_EVIDENCE = 3         # §2.3
MIN_SCHOOLS = 3                     # §2.1（适用性 warn）
MIN_VERSION_VARIANTS = 5            # §2.2（适用性 warn）
MIN_CHAPTER_NOTES = 12              # §2.4 v2.1 列（长书）
MIN_CHAPTER_INTERPRETATION_CHARS = 600   # §2.4 v2.1 单条 interpretation

# ─── §2.6 / §2.7 / §2.8 新字段阈值（v2.1） ───────────────
MIN_SCENE_DISSECTIONS = 5                 # §1.19（小说类强制；降级 ≥2）
MIN_SCENE_DISSECTIONS_DOWNGRADE = 2       # §4.4 降级（思想史/社科）
MIN_SCENE_DISSECTION_CHARS = 1000         # §2.6 单条 ≥1000 字

MIN_CHARACTER_DOSSIERS = 5                # §1.20（人物书强制）
MIN_CHARACTER_DOSSIERS_GIANT = 10         # §5.1 巨著
MIN_CHARACTER_DOSSIER_CHARS = 600         # §2.7 单条 ≥600 字

MIN_POETICS_DOSSIERS = 3                  # §1.21（含诗词书强制）
MIN_POETICS_DOSSIER_CHARS = 600           # §2.8 单条 ≥600 字

THOUGHT_COORD_DIMS = ["同题延伸", "对立视角", "承继关系", "现代回响"]

# 字段名到统计字段子集的映射（计字数时遍历这些子字段）
SCENE_DISSECTION_FIELDS = (
    "original_text_excerpt",
    "dissection_layers",
    "key_close_reads",
    "echoes",
)
CHARACTER_DOSSIER_FIELDS = (
    "appearance_arc",
    "key_scenes",
    "language_signature",
    "fate_pattern",
    "reading_through_lens",
)
POETICS_DOSSIER_FIELDS = (
    "full_or_excerpt",
    "form_analysis",
    "content_analysis",
    "intertextual_anchors",
    "fate_foreshadowing",
)


# ─── 禁词库 ──────────────────────────────────────────────
BANNED_NET_SLANG = [
    "干货", "硬核", "破防", "内卷", "躺平", "润了", "emo 了",
    "yyds", "绝绝子", "栓Q", "栓 Q", "打工人", "社畜",
    "打 call", "真的会谢", "绝了", "一整个震惊住", "麻了",
    "上班人", "家人们", "家人们谁懂啊",
]

BANNED_MARKETING = [
    "震惊！", "震惊!", "震惊!!",
    "你不知道的",
    "一篇讲透",
    "深度好文",
    "干货满满",
    "建议收藏",
    "看完这篇就够了",
    "不看后悔",
    "全网最",
    "吐血推荐",
    "必看",
    "最全", "最详细", "最通俗",
]

BANNED_AUTHOR_TONE = [
    "笔者认为", "笔者以为", "笔者指出", "在此笔者",
    "本文认为",
    "不难看出", "不难发现",
    "显而易见",
    "众所周知",
]

BANNED_SUMMARY_WASTE = [
    "综上所述",
    "由此可见",
    "归根结底",
    "总而言之",
    "从以上分析可以看出",
    "从上面的分析",
    "总的来说",
]

BANNED_ACADEMIC_POSE = [
    "存在论层面",
    "本质上来说",
    "某种程度上来说",
    "在一定意义上",
    "在某种意义上",
]

BANNED_CORPORATE = [
    "赋能", "抓手", "闭环", "底层逻辑", "顶层设计",
    "颗粒度", "对齐", "拉通", "打透",
    # 注："心智"不列入——它是"mental"的标准中译，严肃心理学语境必需
]

# ─── 框架名（正文禁出现，工具箱除外）───────────────────
# 规则：只禁"抽象框架/理论名"，不禁"历史人物姓名"——
# 因为谈承继关系（如"勒庞承继自塔尔德/弗洛伊德后继"）时
# 必须能提人名。
FRAMEWORK_NAMES = [
    "需求层次",         # 马斯洛 OK（人名），"需求层次理论" 禁
    "依恋理论",
    "防御机制",
    "认知失调",
    "五因素", "OCEAN",
    "沟通分析 TA", "TA 状态",
    "场域理论",
    "拟剧论",
    "符号互动",
    "社会交换论",
    "理想类型",
    "博弈论",
    "囚徒困境",
    "边际效用",
    "公地悲剧",
    "信息不对称",
    "交易成本",
    "英雄之旅",
    "三幕结构",
    "陌生化",
    "贝叶斯",
    "二阶思维",
    "反脆弱",
    "锚定效应",
    "可得性偏差",
    "幸存者偏差",
    "现象学还原",
    "辩证法",
    "功利主义",
    "义务论",
    "德性伦理",
]


def check_distill_schema(d, legacy=False):
    """检查 distill.json 结构完整性（v1 硬红线 · 始终强制）。"""
    required_top = ["meta", "modules"]
    errors = []
    for k in required_top:
        if k not in d:
            errors.append(f"缺失顶层字段: {k}")

    meta = d.get("meta", {})
    required_meta = ["title", "motif", "genes", "source_mix"]
    for k in required_meta:
        if k not in meta:
            errors.append(f"meta 缺少字段: {k}")

    motif = meta.get("motif", "")
    if len(motif) > 30:
        errors.append(f"母题过长（{len(motif)} 字），应 ≤ 30")

    if not d.get("modules"):
        errors.append("modules 为空")

    # v1 硬下限（始终强制——这就是 v1 的"硬红线"含义）
    if "misreadings" not in d or len(d.get("misreadings", [])) < V1_MIN_MISREADINGS:
        errors.append(f"误读陷阱不足 {V1_MIN_MISREADINGS} 条")

    if "blindspots" not in d or len(d.get("blindspots", [])) < V1_MIN_BLINDSPOTS:
        errors.append(f"作者盲点不足 {V1_MIN_BLINDSPOTS} 条")

    if "golden_quotes" not in d or len(d.get("golden_quotes", [])) < V1_MIN_GOLDEN_QUOTES:
        errors.append(f"金句不足 {V1_MIN_GOLDEN_QUOTES} 条")

    if not d.get("memory_hook"):
        errors.append("缺少 memory_hook（记忆抓手）")

    if not d.get("overview_svg"):
        errors.append("缺少 overview_svg（全貌地图）")

    return errors


def extract_all_text(d):
    """从 distill.json 提取所有正文文本（不含 toolbox）。"""
    parts = []

    def add(x):
        if isinstance(x, str):
            parts.append(x)
        elif isinstance(x, list):
            for i in x:
                add(i)
        elif isinstance(x, dict):
            for v in x.values():
                add(v)

    for k, v in d.items():
        if k == "toolbox":
            continue  # 工具箱允许出现框架名
        add(v)

    return "\n".join(parts)


def count_char_in(text, patterns):
    """count occurrences of any pattern (string match)."""
    hits = []
    for p in patterns:
        count = text.count(p)
        if count > 0:
            hits.append((p, count))
    return hits


ANCHOR_PATTERNS = [
    r"第[一二三四五六七八九十百零〇\d]+[章回卷部节]",
    r"第[一二三四五六七八九十百零〇\d]+[页頁]",
    r"第[一二三四五六七八九十百零〇\d]+卷第[一二三四五六七八九十百零〇\d]+章",
    r"Ch(?:apter|\.)[\s\d]+",
    r"p\.[\s\d]+",
    r"pp\.[\s\d]+",
    r"\d{4}\s*年",  # 年份锚点
]


def count_facts_anchors(d):
    """事实锚点估算：
    - quote_pairs（强锚点，权重 1.0）
    - facts_layer 里带章节/页码/年份定位的事实（权重 0.5）
    """
    count = 0
    for m in d.get("modules", []):
        count += len(m.get("quote_pairs", []))

    # 扫描 facts_layer / mechanism_layer 里的锚点文字
    soft_count = 0
    for m in d.get("modules", []):
        blob = json.dumps(m.get("facts_layer", {}), ensure_ascii=False)
        blob += json.dumps(m.get("mechanism_layer", {}), ensure_ascii=False)
        for pat in ANCHOR_PATTERNS:
            soft_count += len(re.findall(pat, blob))

    return count + int(soft_count * 0.5)


def count_quote_pairs_total(d):
    """quote_pairs 纯总数（不含锚点软计数）— §1.3 用。"""
    return sum(len(m.get("quote_pairs", [])) for m in d.get("modules", []))


def count_chars_text(text):
    """估算中文字数（非空白非标点字符）。"""
    cleaned = re.sub(r"[\s\W\d]+", "", text, flags=re.UNICODE)
    # 保留中文和字母
    return len(cleaned)


def count_module_chars(module):
    """单模块正文字数估算（facts_layer + mechanism_layer + viewpoint_layer）— §1.2。"""
    parts = []

    def add(x):
        if isinstance(x, str):
            parts.append(x)
        elif isinstance(x, list):
            for i in x:
                add(i)
        elif isinstance(x, dict):
            for v in x.values():
                add(v)

    for layer in ("facts_layer", "mechanism_layer", "viewpoint_layer"):
        add(module.get(layer, {}))

    return count_chars_text("\n".join(parts))


def count_fact_matrix_cells(d):
    """事实矩阵 cells 总数 — §1.8。
    支持顶层 fact_matrix 或模块内 fact_matrix。结构允许 cells / rows×cols / list。
    """
    total = 0

    def cells_in(fm):
        if not fm:
            return 0
        if isinstance(fm, list):
            return len(fm)
        if isinstance(fm, dict):
            if "cells" in fm and isinstance(fm["cells"], list):
                return len(fm["cells"])
            # rows × cols 估算
            rows = fm.get("rows") or fm.get("行")
            cols = fm.get("cols") or fm.get("列") or fm.get("columns")
            if isinstance(rows, list) and isinstance(cols, list):
                return len(rows) * len(cols)
            # 兜底：所有 list-typed 子字段总长
            return sum(len(v) for v in fm.values() if isinstance(v, list))
        return 0

    total += cells_in(d.get("fact_matrix"))
    for m in d.get("modules", []):
        total += cells_in(m.get("fact_matrix"))
    return total


def count_dossier_chars(dossier, fields):
    """统计 dossier-style entry 在 fields 列出的子字段上的 CJK 字符总和。

    用于 §2.6 scene_dissections / §2.7 character_dossiers / §2.8 poetics_dossiers
    的"单条体量"校验。值可以是 str / list / dict——都会递归累加。
    """
    if not isinstance(dossier, dict):
        return 0
    parts = []

    def add(x):
        if isinstance(x, str):
            parts.append(x)
        elif isinstance(x, list):
            for i in x:
                add(i)
        elif isinstance(x, dict):
            for v in x.values():
                add(v)

    for f in fields:
        add(dossier.get(f))

    return count_chars_text("\n".join(parts))


def check_v2_deepening(d):
    """v2.0 加深版检查 — 用 v2.0 协议的中间档阈值（保留作 v2.0 产物对照基线）。

    返回 warnings 列表（labeled "[v2 加深版]"）。
    """
    warnings = []
    label = "[v2 加深版]"

    modules = d.get("modules", [])

    if len(modules) < V2_MIN_MODULES:
        warnings.append(f"{label} 模块数 {len(modules)} < {V2_MIN_MODULES}（§1.1 v2）")

    qp_total = count_quote_pairs_total(d)
    if qp_total < V2_MIN_QUOTE_PAIRS:
        warnings.append(f"{label} 原文锚点 quote_pairs 总数 {qp_total} < {V2_MIN_QUOTE_PAIRS}（§1.3 v2）")

    n_mis = len(d.get("misreadings", []))
    if n_mis < V2_MIN_MISREADINGS:
        warnings.append(f"{label} 误读陷阱 {n_mis} < {V2_MIN_MISREADINGS}（§1.5 v2）")
    n_blind = len(d.get("blindspots", []))
    if n_blind < V2_MIN_BLINDSPOTS:
        warnings.append(f"{label} 作者盲点 {n_blind} < {V2_MIN_BLINDSPOTS}（§1.6 v2）")
    n_gold = len(d.get("golden_quotes", []))
    if n_gold < V2_MIN_GOLDEN_QUOTES:
        warnings.append(f"{label} 金句 {n_gold} < {V2_MIN_GOLDEN_QUOTES}（§1.7 v2）")

    cells = count_fact_matrix_cells(d)
    if cells < V2_MIN_FACT_MATRIX_CELLS:
        warnings.append(f"{label} 事实矩阵 cells {cells} < {V2_MIN_FACT_MATRIX_CELLS}（§1.8 v2）")

    tc = d.get("thought_coordinates")
    if not tc:
        warnings.append(f"{label} 缺少 thought_coordinates（§1.9-1.12 v2，需四维各 ≥ {V2_MIN_THOUGHT_COORD_PER_DIM}）")
    else:
        for dim in THOUGHT_COORD_DIMS:
            entries = tc.get(dim, [])
            if not isinstance(entries, list) or len(entries) < V2_MIN_THOUGHT_COORD_PER_DIM:
                warnings.append(
                    f"{label} thought_coordinates.{dim} = {len(entries) if isinstance(entries, list) else 0} "
                    f"< {V2_MIN_THOUGHT_COORD_PER_DIM}（§1.9-1.12 v2）"
                )

    apd = d.get("author_position_deconstruction")
    if not apd:
        warnings.append(f"{label} 缺少 author_position_deconstruction（§2.3，evidence ≥ {MIN_AUTHOR_POS_EVIDENCE}）")
    else:
        ev = apd.get("evidence", [])
        if not isinstance(ev, list) or len(ev) < MIN_AUTHOR_POS_EVIDENCE:
            warnings.append(
                f"{label} author_position_deconstruction.evidence = "
                f"{len(ev) if isinstance(ev, list) else 0} < {MIN_AUTHOR_POS_EVIDENCE}（§2.3）"
            )

    for i, m in enumerate(modules):
        title = m.get("title", "?")
        prefix = f"{label} 模块 {i+1}「{title}」"

        mc = count_module_chars(m)
        if mc < V2_MIN_MODULE_CHARS:
            warnings.append(f"{prefix} 正文字数 {mc} < {V2_MIN_MODULE_CHARS}（§1.2 v2）")

        n_qp = len(m.get("quote_pairs", []))
        if n_qp < V2_MIN_PER_MODULE_QUOTE_PAIRS:
            warnings.append(f"{prefix} quote_pairs {n_qp} < {V2_MIN_PER_MODULE_QUOTE_PAIRS}（§1.4 v2）")

        ec = m.get("external_counterpoints", [])
        if not isinstance(ec, list) or len(ec) < V2_MIN_EXTERNAL_COUNTERPOINTS:
            warnings.append(
                f"{prefix} external_counterpoints {len(ec) if isinstance(ec, list) else 0} "
                f"< {V2_MIN_EXTERNAL_COUNTERPOINTS}（§1.13 v2）"
            )

        vl = m.get("viewpoint_layer", {}) or {}
        dc = vl.get("derivation_chain")
        if not dc:
            warnings.append(f"{prefix} viewpoint_layer.derivation_chain 缺失（§3，需 ≥ {V2_MIN_DERIVATION_CHAIN_STEPS} 步）")
        elif not isinstance(dc, list) or len(dc) < V2_MIN_DERIVATION_CHAIN_STEPS:
            warnings.append(
                f"{prefix} derivation_chain 步数 {len(dc) if isinstance(dc, list) else 0} "
                f"< {V2_MIN_DERIVATION_CHAIN_STEPS}（§3 v2）"
            )

    return warnings


def check_v21_deepening(d):
    """v2.1 加深版检查 — 阈值全部按 v2.1 列。返回 warnings 列表。

    包含：§1 v2.1 阈值升级 + §1.4b（quote.original ≥100 字）
    + §3（推导链 ≥4 步）+ §2.4 v2.1（chapter interpretation ≥600 字）。
    """
    warnings = []
    label = "[v2.1 加深版]"

    modules = d.get("modules", [])

    # §1.1 模块数
    if len(modules) < MIN_MODULES:
        warnings.append(f"{label} 模块数 {len(modules)} < {MIN_MODULES}（§1.1 v2.1，10-12）")

    # §1.3 quote_pairs 总数
    qp_total = count_quote_pairs_total(d)
    if qp_total < MIN_QUOTE_PAIRS:
        warnings.append(f"{label} 原文锚点 quote_pairs 总数 {qp_total} < {MIN_QUOTE_PAIRS}（§1.3 v2.1，巨著 ≥80）")

    # §1.5 §1.6 §1.7
    n_mis = len(d.get("misreadings", []))
    if n_mis < MIN_MISREADINGS:
        warnings.append(f"{label} 误读陷阱 {n_mis} < {MIN_MISREADINGS}（§1.5 v2.1）")
    n_blind = len(d.get("blindspots", []))
    if n_blind < MIN_BLINDSPOTS:
        warnings.append(f"{label} 作者盲点 {n_blind} < {MIN_BLINDSPOTS}（§1.6 v2.1）")
    n_gold = len(d.get("golden_quotes", []))
    if n_gold < MIN_GOLDEN_QUOTES:
        warnings.append(f"{label} 金句 {n_gold} < {MIN_GOLDEN_QUOTES}（§1.7 v2.1）")

    # §1.8 事实矩阵 cells
    cells = count_fact_matrix_cells(d)
    if cells < MIN_FACT_MATRIX_CELLS:
        warnings.append(f"{label} 事实矩阵 cells {cells} < {MIN_FACT_MATRIX_CELLS}（§1.8 v2.1）")

    # §1.9-1.12 思想坐标四维
    tc = d.get("thought_coordinates")
    if not tc:
        warnings.append(f"{label} 缺少 thought_coordinates（§1.9-1.12 v2.1，四维各 ≥ {MIN_THOUGHT_COORD_PER_DIM}）")
    else:
        for dim in THOUGHT_COORD_DIMS:
            entries = tc.get(dim, [])
            if not isinstance(entries, list) or len(entries) < MIN_THOUGHT_COORD_PER_DIM:
                warnings.append(
                    f"{label} thought_coordinates.{dim} = {len(entries) if isinstance(entries, list) else 0} "
                    f"< {MIN_THOUGHT_COORD_PER_DIM}（§1.9-1.12 v2.1）"
                )

    # §2.3 author_position_deconstruction（强度同 v2 但仍属 v2.1 主干）
    apd = d.get("author_position_deconstruction")
    if not apd:
        warnings.append(f"{label} 缺少 author_position_deconstruction（§2.3，evidence ≥ {MIN_AUTHOR_POS_EVIDENCE}）")
    else:
        ev = apd.get("evidence", [])
        if not isinstance(ev, list) or len(ev) < MIN_AUTHOR_POS_EVIDENCE:
            warnings.append(
                f"{label} author_position_deconstruction.evidence = "
                f"{len(ev) if isinstance(ev, list) else 0} < {MIN_AUTHOR_POS_EVIDENCE}（§2.3）"
            )

    # §2.4 v2.1 章节级 interpretation ≥600 字
    cln = d.get("chapter_level_notes")
    if isinstance(cln, list) and cln:
        for j, cn in enumerate(cln):
            if not isinstance(cn, dict):
                continue
            interp = cn.get("interpretation", "") or ""
            ic = count_chars_text(interp) if isinstance(interp, str) else 0
            if ic < MIN_CHAPTER_INTERPRETATION_CHARS:
                ch = cn.get("chapter", f"#{j+1}")
                warnings.append(
                    f"{label} chapter_level_notes[{ch}] interpretation 字数 {ic} "
                    f"< {MIN_CHAPTER_INTERPRETATION_CHARS}（§2.4 v2.1）"
                )

    # §1.2 §1.4 §1.4b §1.13 §1.14 — 逐模块检查
    for i, m in enumerate(modules):
        title = m.get("title", "?")
        prefix = f"{label} 模块 {i+1}「{title}」"

        # §1.2 单模块字数
        mc = count_module_chars(m)
        if mc < MIN_MODULE_CHARS:
            warnings.append(f"{prefix} 正文字数 {mc} < {MIN_MODULE_CHARS}（§1.2 v2.1，人物/场景重模块 ≥6000）")

        # §1.4 单模块 quote_pairs
        qps = m.get("quote_pairs", []) or []
        n_qp = len(qps)
        if n_qp < MIN_PER_MODULE_QUOTE_PAIRS:
            warnings.append(f"{prefix} quote_pairs {n_qp} < {MIN_PER_MODULE_QUOTE_PAIRS}（§1.4 v2.1）")

        # §1.4b 单条 quote.original ≥100 字
        for k, qp in enumerate(qps):
            if not isinstance(qp, dict):
                continue
            orig = qp.get("original", "") or ""
            oc = count_chars_text(orig) if isinstance(orig, str) else 0
            if oc < MIN_QUOTE_ORIGINAL_CHARS:
                warnings.append(
                    f"{prefix} quote_pairs[{k}].original 字数 {oc} "
                    f"< {MIN_QUOTE_ORIGINAL_CHARS}（§1.4b v2.1）"
                )

        # §1.13 external_counterpoints
        ec = m.get("external_counterpoints", [])
        if not isinstance(ec, list) or len(ec) < MIN_EXTERNAL_COUNTERPOINTS:
            warnings.append(
                f"{prefix} external_counterpoints {len(ec) if isinstance(ec, list) else 0} "
                f"< {MIN_EXTERNAL_COUNTERPOINTS}（§1.13 v2.1）"
            )

        # §1.14 / §3 推导链 ≥4 步
        vl = m.get("viewpoint_layer", {}) or {}
        dc = vl.get("derivation_chain")
        if not dc:
            warnings.append(f"{prefix} viewpoint_layer.derivation_chain 缺失（§3 v2.1，需 ≥ {MIN_DERIVATION_CHAIN_STEPS} 步）")
        elif not isinstance(dc, list) or len(dc) < MIN_DERIVATION_CHAIN_STEPS:
            warnings.append(
                f"{prefix} derivation_chain 步数 {len(dc) if isinstance(dc, list) else 0} "
                f"< {MIN_DERIVATION_CHAIN_STEPS}（§3 v2.1）"
            )

    return warnings


def check_applicability(d):
    """v2 适用性提示 — 仅 warn 不 fail（§4 / §2.1 §2.2 §2.4）。"""
    notes = []
    label = "[v2 适用性]"

    soi = d.get("schools_of_interpretation")
    if soi is not None and isinstance(soi, list) and 0 < len(soi) < MIN_SCHOOLS:
        notes.append(f"{label} schools_of_interpretation 已填但只有 {len(soi)} 派 < {MIN_SCHOOLS}（§2.1）")

    vv = d.get("version_variants")
    if vv is not None and isinstance(vv, list) and 0 < len(vv) < MIN_VERSION_VARIANTS:
        notes.append(f"{label} version_variants 已填但只有 {len(vv)} 处 < {MIN_VERSION_VARIANTS}（§2.2）")

    cln = d.get("chapter_level_notes")
    if cln is not None and isinstance(cln, list) and 0 < len(cln) < MIN_CHAPTER_NOTES:
        notes.append(f"{label} chapter_level_notes 已填但只有 {len(cln)} 个 < {MIN_CHAPTER_NOTES}（§2.4 v2.1）")

    return notes


def check_v21_applicability(d):
    """v2.1 适用性提示 — §2.6 / §2.7 / §2.8 三个新字段。

    应用规则（§4.4-§4.6）：
      - 字段不存在或空数组：发"适用书必填"提示（不 fail，不适用书可空）
      - 存在且非空：按数量+单条字数校验，未达发"v2.1 加深版警告"

    返回 (applicability_hints, v21_warnings) — 区分两类。
    """
    hints = []  # [v2.1 适用性] 缺失但不强制
    warns = []  # [v2.1 加深版] 已填但不达标
    h_label = "[v2.1 适用性]"
    w_label = "[v2.1 加深版]"

    # §2.6 scene_dissections
    sd = d.get("scene_dissections")
    if not sd:
        hints.append(
            f"{h_label} 缺少 scene_dissections（§2.6）—— "
            f"小说/史书/戏剧等适用书必填 ≥{MIN_SCENE_DISSECTIONS} 个（降级 ≥{MIN_SCENE_DISSECTIONS_DOWNGRADE}），详见 §4.4"
        )
    else:
        if isinstance(sd, list):
            n = len(sd)
            # 用宽松的"降级阈值"做 warn（取较低门槛；具体应用类强制由 caller 判定）
            if n < MIN_SCENE_DISSECTIONS_DOWNGRADE:
                warns.append(
                    f"{w_label} scene_dissections 仅 {n} 个 < 降级最低 {MIN_SCENE_DISSECTIONS_DOWNGRADE}（§2.6/§4.4）"
                )
            elif n < MIN_SCENE_DISSECTIONS:
                warns.append(
                    f"{w_label} scene_dissections 仅 {n} 个 < 强制档 {MIN_SCENE_DISSECTIONS}（§2.6 小说类应满足）"
                )
            for j, entry in enumerate(sd):
                if not isinstance(entry, dict):
                    continue
                cc = count_dossier_chars(entry, SCENE_DISSECTION_FIELDS)
                if cc < MIN_SCENE_DISSECTION_CHARS:
                    title = entry.get("scene_title", f"#{j+1}")
                    warns.append(
                        f"{w_label} scene_dissections[{title}] 字数 {cc} "
                        f"< {MIN_SCENE_DISSECTION_CHARS}（§2.6 单条体量）"
                    )

    # §2.7 character_dossiers
    cd = d.get("character_dossiers")
    if not cd:
        hints.append(
            f"{h_label} 缺少 character_dossiers（§2.7）—— "
            f"小说/传记/史书等适用书必填 ≥{MIN_CHARACTER_DOSSIERS} 人（巨著 ≥{MIN_CHARACTER_DOSSIERS_GIANT}），详见 §4.5"
        )
    else:
        if isinstance(cd, list):
            n = len(cd)
            if n < MIN_CHARACTER_DOSSIERS:
                warns.append(
                    f"{w_label} character_dossiers 仅 {n} 人 < {MIN_CHARACTER_DOSSIERS}（§2.7 人物书应满足；巨著 ≥{MIN_CHARACTER_DOSSIERS_GIANT}）"
                )
            for j, entry in enumerate(cd):
                if not isinstance(entry, dict):
                    continue
                cc = count_dossier_chars(entry, CHARACTER_DOSSIER_FIELDS)
                if cc < MIN_CHARACTER_DOSSIER_CHARS:
                    name = entry.get("name", f"#{j+1}")
                    warns.append(
                        f"{w_label} character_dossiers[{name}] 字数 {cc} "
                        f"< {MIN_CHARACTER_DOSSIER_CHARS}（§2.7 单条体量）"
                    )

    # §2.8 poetics_dossiers
    pd = d.get("poetics_dossiers")
    if not pd:
        hints.append(
            f"{h_label} 缺少 poetics_dossiers（§2.8）—— "
            f"含诗词曲赋的书必填 ≥{MIN_POETICS_DOSSIERS} 篇，详见 §4.6"
        )
    else:
        if isinstance(pd, list):
            n = len(pd)
            if n < MIN_POETICS_DOSSIERS:
                warns.append(
                    f"{w_label} poetics_dossiers 仅 {n} 篇 < {MIN_POETICS_DOSSIERS}（§2.8 含诗词书应满足）"
                )
            for j, entry in enumerate(pd):
                if not isinstance(entry, dict):
                    continue
                cc = count_dossier_chars(entry, POETICS_DOSSIER_FIELDS)
                if cc < MIN_POETICS_DOSSIER_CHARS:
                    title = entry.get("title", f"#{j+1}")
                    warns.append(
                        f"{w_label} poetics_dossiers[{title}] 字数 {cc} "
                        f"< {MIN_POETICS_DOSSIER_CHARS}（§2.8 单条体量）"
                    )

    return hints, warns


# ─── v2.2 排版警告（§10）──────────────────────────────────
def _collect_long_text(field):
    """提取长字段的纯文本内容（不含 HTML/标记），用于段落计数。
    支持三种格式：
    - str → 直接返回
    - {paragraphs: [str, ...]} → join
    - {subhead, body} → join body
    - list of dict → join 各子块
    """
    if not field:
        return ""
    if isinstance(field, str):
        return field
    if isinstance(field, dict):
        if "paragraphs" in field:
            return "\n\n".join(str(p) for p in field.get("paragraphs", []))
        if "body" in field:
            body = field["body"]
            if isinstance(body, list):
                return "\n\n".join(str(p) for p in body)
            return str(body)
        return ""
    if isinstance(field, list):
        return "\n\n".join(_collect_long_text(item) for item in field)
    return str(field)


def _count_paragraphs(field):
    """估算长字段的段落数。
    - 显式 paragraphs/list/dict-of-subhead 直接数
    - 字符串则按 \\n\\n 或「第N组事实/第N层/其N」启发式
    """
    if not field:
        return 0
    if isinstance(field, dict):
        if "paragraphs" in field:
            return len([p for p in field.get("paragraphs", []) if str(p).strip()])
        if "body" in field:
            body = field["body"]
            if isinstance(body, list):
                return len([p for p in body if str(p).strip()])
            return _count_paragraphs(body)
    if isinstance(field, list):
        return sum(_count_paragraphs(item) for item in field)
    if not isinstance(field, str):
        return 0
    text = field.strip()
    if not text:
        return 0
    if "\n\n" in text:
        return len([p for p in text.split("\n\n") if p.strip()])
    n_subhead = len(re.findall(r'第[一二三四五六七八九十]+(?:组事实|层|组|个层次|阶段|个模式|种模式)[，、]', text))
    n_qiyi = len(re.findall(r'其[一二三四五六七八九十]+[，、：]', text))
    if n_subhead >= 2:
        return n_subhead
    if n_qiyi >= 2:
        return n_qiyi
    return 1


def _count_kw_marks(text):
    """统计文本中 v2.2 关键短语标记数（「...」内 2-12 字 + 元论述词）。"""
    if not text:
        return 0
    n_quoted = len(re.findall(r'[「『][^「」『』\n]{2,12}[」』]', text))
    n_meta = len(re.findall(
        r'(总钥匙|总宣告|总命题|临界点|拐点|分水岭|转折点|反证|反讽|核心命题|内在悖论|结构性宿命|精准命名|精确预告)',
        text
    ))
    return n_quoted + n_meta


# v2.2 排版段落硬下限（§10.4）
V22_PARA_THRESHOLDS = [
    (3000, 5),  # ≥3000 字 → ≥5 段
    (1500, 4),  # ≥1500 字 → ≥4 段
    (600,  3),  # ≥600 字  → ≥3 段
]
V22_MIN_KW_PER_MODULE = 5         # §10.4.5 单模块至少 5 个关键短语
V22_MIN_KW_PER_HEAVY_MODULE = 10  # 场景/人物模块至少 10 个


def check_v22_typography(d):
    """v2.2 §10 排版警告：长字段段落数 + 关键短语密度。"""
    warns = []
    label = "[v2.2 排版]"

    # 检查每个 module 的长字段段落数
    for i, m in enumerate(d.get("modules", []), 1):
        title = m.get("title", f"#{i}")[:25]
        prefix = f"{label} 模块[{title}]"

        # 各长字段段落检查
        long_fields = {
            "facts_layer.systematized_facts": m.get("facts_layer", {}).get("systematized_facts") if isinstance(m.get("facts_layer"), dict) else None,
            "mechanism_layer.cross_dim_weaving": m.get("mechanism_layer", {}).get("cross_dim_weaving") if isinstance(m.get("mechanism_layer"), dict) else None,
            "viewpoint_layer.modern_transfer": m.get("viewpoint_layer", {}).get("modern_transfer") if isinstance(m.get("viewpoint_layer"), dict) else None,
            "viewpoint_layer.caveats": m.get("viewpoint_layer", {}).get("caveats") if isinstance(m.get("viewpoint_layer"), dict) else None,
        }
        for fname, field in long_fields.items():
            if not field:
                continue
            text = _collect_long_text(field)
            char_count = count_chars_text(text) if text else 0
            if char_count == 0:
                continue
            n_para = _count_paragraphs(field)
            for thresh_chars, thresh_para in V22_PARA_THRESHOLDS:
                if char_count >= thresh_chars and n_para < thresh_para:
                    warns.append(
                        f"{prefix} {fname} 字数 {char_count} 但段落仅 {n_para} 段 "
                        f"< {thresh_para} 段（§10.4：≥{thresh_chars} 字应 ≥{thresh_para} 段）"
                    )
                    break

        # 关键短语密度
        full_module_text = _collect_long_text(long_fields["facts_layer.systematized_facts"])
        kw_n = _count_kw_marks(full_module_text)
        gene = m.get("gene", "")
        threshold = V22_MIN_KW_PER_HEAVY_MODULE if gene in ("character", "narrative") else V22_MIN_KW_PER_MODULE
        if kw_n < threshold:
            warns.append(
                f"{prefix} 关键短语标记 {kw_n} < {threshold}（§10.4.5 用「」标记关键短语让 .kw 高亮）"
            )

    # 检查 scene_dissections 各场景长字段段落
    for i, s in enumerate(d.get("scene_dissections", []) or [], 1):
        if not isinstance(s, dict):
            continue
        title = s.get("scene_title", f"#{i}")[:20]
        layers = s.get("dissection_layers", {})
        if isinstance(layers, dict):
            for lname, lcontent in layers.items():
                text = _collect_long_text(lcontent) if lcontent else ""
                if not text:
                    continue
                cc = count_chars_text(text)
                np = _count_paragraphs(lcontent)
                if cc >= 600 and np < 2:
                    warns.append(
                        f"{label} 场景[{title}].{lname} 字数 {cc} 但段落仅 {np} 段（§10.4 长字段应分段）"
                    )

    return warns


def main():
    args = sys.argv[1:]
    legacy = False
    if args and args[0] == "--legacy":
        legacy = True
        args = args[1:]

    if not args:
        print("Usage: quality_check.py [--legacy] <distill.json> [rendered.html]", file=sys.stderr)
        print("\nv1 硬红线（始终强制 · 违反算不合格）：", file=sys.stderr)
        print("  - 结构完整性 / 禁词 / 框架名 / 三层结构", file=sys.stderr)
        print("  - misreadings ≥ 2 / blindspots ≥ 2 / golden_quotes ≥ 5", file=sys.stderr)
        print("\nv2.1 加深版警告（默认开启 · 见 deepening-protocol §1-§3 v2.1）：", file=sys.stderr)
        print(f"  - 模块数 ≥ {MIN_MODULES} / 单模块字数 ≥ {MIN_MODULE_CHARS} / quote_pairs ≥ {MIN_QUOTE_PAIRS}", file=sys.stderr)
        print(f"  - 单条 quote.original ≥ {MIN_QUOTE_ORIGINAL_CHARS} 字（§1.4b）/ 推导链 ≥ {MIN_DERIVATION_CHAIN_STEPS} 步", file=sys.stderr)
        print(f"  - 误读 ≥ {MIN_MISREADINGS} / 盲点 ≥ {MIN_BLINDSPOTS} / 金句 ≥ {MIN_GOLDEN_QUOTES}", file=sys.stderr)
        print(f"  - 思想坐标四维各 ≥ {MIN_THOUGHT_COORD_PER_DIM} / 外部反例 ≥ {MIN_EXTERNAL_COUNTERPOINTS} /", file=sys.stderr)
        print(f"    事实矩阵 cells ≥ {MIN_FACT_MATRIX_CELLS} / 章节级 ≥ {MIN_CHAPTER_NOTES}（§2.4 单条 ≥ {MIN_CHAPTER_INTERPRETATION_CHARS} 字）", file=sys.stderr)
        print(f"\nv2.1 适用性提示（§4.4-§4.6 新字段）：", file=sys.stderr)
        print(f"  - scene_dissections ≥ {MIN_SCENE_DISSECTIONS}（小说类，单条 ≥ {MIN_SCENE_DISSECTION_CHARS} 字 / 降级 ≥ {MIN_SCENE_DISSECTIONS_DOWNGRADE}）", file=sys.stderr)
        print(f"  - character_dossiers ≥ {MIN_CHARACTER_DOSSIERS}（人物书，巨著 ≥ {MIN_CHARACTER_DOSSIERS_GIANT}，单条 ≥ {MIN_CHARACTER_DOSSIER_CHARS} 字）", file=sys.stderr)
        print(f"  - poetics_dossiers ≥ {MIN_POETICS_DOSSIERS}（含诗词书，单条 ≥ {MIN_POETICS_DOSSIER_CHARS} 字）", file=sys.stderr)
        print("\n--legacy 仅运行 v1 硬红线（向后兼容旧 distill.json）", file=sys.stderr)
        sys.exit(1)

    in_path = Path(args[0])
    try:
        with in_path.open(encoding="utf-8") as f:
            d = json.load(f)
    except json.JSONDecodeError as e:
        print(f"━ JSON 解析失败 ━", file=sys.stderr)
        print(f"文件: {in_path}", file=sys.stderr)
        print(f"错误位置: 行 {e.lineno} 列 {e.colno} (字符 {e.pos})", file=sys.stderr)
        print(f"错误原因: {e.msg}", file=sys.stderr)
        print(f"\n常见原因：", file=sys.stderr)
        print(f"  · 字符串内有未转义的双引号（中文「」或 smart quotes 会被当作正文）", file=sys.stderr)
        print(f"  · 最后一个条目后有多余逗号", file=sys.stderr)
        print(f"  · 字符串未闭合或括号不匹配", file=sys.stderr)
        # 显示错误附近的上下文
        try:
            raw = in_path.read_text(encoding="utf-8")
            lines = raw.split("\n")
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            print(f"\n上下文（行 {start+1}-{end}）：", file=sys.stderr)
            for i in range(start, end):
                marker = " >> " if i + 1 == e.lineno else "    "
                print(f"{marker}{i+1}: {lines[i][:120]}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(2)

    print("━" * 60)
    title = d.get('meta', {}).get('title', '未命名')
    mode = "v1 legacy 模式" if legacy else "v2.1 加深版模式"
    print(f"质量检查 · {title} · {mode}")
    print("━" * 60)

    # 1. Schema (v1 硬红线)
    errors = check_distill_schema(d, legacy=legacy)
    print("\n【结构完整性 · v1 硬红线】")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("  ✓ 所有必需字段齐全")

    # 2. 正文文本
    body_text = extract_all_text(d)
    char_count = count_chars_text(body_text)
    print(f"\n【字数估算】")
    print(f"  中文字符数（粗估）: {char_count}")

    # 3. 事实密度
    facts_count = count_facts_anchors(d)
    qp_total = count_quote_pairs_total(d)
    print(f"\n【事实锚点】")
    print(f"  quote_pairs 总数（纯）: {qp_total}")
    print(f"  事实锚点估算（含软锚点）: {facts_count}")
    if char_count > 0:
        density = facts_count * 1000 / char_count
        print(f"  密度估算: {density:.2f} / 千字（目标 ≥ 2）")
        if density < 2:
            print(f"  ⚠ 事实密度偏低")

    # 4. 禁词扫描（v1 硬红线）
    print("\n【禁词扫描 · v1 硬红线】")
    all_banned = {
        "网感词": BANNED_NET_SLANG,
        "营销体": BANNED_MARKETING,
        "作者腔": BANNED_AUTHOR_TONE,
        "总结废话": BANNED_SUMMARY_WASTE,
        "学术造作": BANNED_ACADEMIC_POSE,
        "办公室黑话": BANNED_CORPORATE,
    }
    total_hits = 0
    for cat, words in all_banned.items():
        hits = count_char_in(body_text, words)
        if hits:
            total_hits += sum(c for _, c in hits)
            print(f"  ✗ {cat}:")
            for w, c in hits:
                print(f"      「{w}」× {c}")
    if total_hits == 0:
        print("  ✓ 禁词 0 命中")
    else:
        print(f"  ⚠ 总禁词命中: {total_hits}")

    # 5. 框架名扫描（v1 硬红线）
    print("\n【框架名扫描（正文） · v1 硬红线】")
    framework_hits = count_char_in(body_text, FRAMEWORK_NAMES)
    if framework_hits:
        print("  ✗ 正文出现框架名（应在工具箱才出现）:")
        for w, c in framework_hits:
            print(f"      「{w}」× {c}")
    else:
        print("  ✓ 正文未出现框架名")

    # 6. 模块三重结构检查（v1 硬红线）
    print("\n【三重结构完整性 · v1 硬红线】")
    missing = []
    for i, m in enumerate(d.get("modules", [])):
        has_facts = bool(m.get("facts_layer"))
        has_mech = bool(m.get("mechanism_layer"))
        has_view = bool(m.get("viewpoint_layer"))
        if not (has_facts and has_mech and has_view):
            missing.append(
                f"模块 {i+1} 「{m.get('title', '?')}」: "
                f"{'✓' if has_facts else '✗'}事实 "
                f"{'✓' if has_mech else '✗'}机制 "
                f"{'✓' if has_view else '✗'}观点"
            )
    if missing:
        for mm in missing:
            print(f"  ✗ {mm}")
    else:
        print(f"  ✓ 所有 {len(d.get('modules', []))} 个模块三层齐全")

    # 7. 信源透明度
    print("\n【信源透明度】")
    sm = d.get("meta", {}).get("source_mix", {})
    if sm:
        total = sum(sm.values())
        if abs(total - 1.0) > 0.05:
            print(f"  ⚠ 信源比例总和 = {total:.2f}，应约等于 1.0")
        else:
            print(f"  ✓ 信源比例合理（总和 {total:.2f}）")
        a_pct = sm.get("A", 0)
        if a_pct < 0.2:
            print(f"  ⚠ A 级原文占比 {a_pct:.0%} 偏低")
    else:
        print("  ✗ 未标注信源构成")

    # 8. v2 / v2.1 加深版深度检查（默认启用，--legacy 跳过）
    v2_warnings = []
    v21_warnings = []
    applicability_notes = []
    v21_app_hints = []
    if not legacy:
        print("\n【v2 加深版深度检查 · 见 deepening-protocol §1-§3 v2 列】")
        v2_warnings = check_v2_deepening(d)
        if v2_warnings:
            print("  · 以下条目按 v2.0 阈值仍未达标（v2.0 → v2.1 升级所需 + v2.0 基线未过）：")
            for w in v2_warnings:
                print(f"  ⚠ {w}")
        else:
            print("  ✓ v2.0 加深版基线全部达标")

        print("\n【v2.1 加深版深度检查 · 见 deepening-protocol §1-§3 v2.1 列】")
        v21_warnings = check_v21_deepening(d)
        if v21_warnings:
            print("  · 以下条目按 v2.1 阈值未达标（v2.0 产物会在此提示 v2.0 → v2.1 升级所需）：")
            for w in v21_warnings:
                print(f"  ⚠ {w}")
        else:
            print("  ✓ v2.1 加深版所有指标达标")

        applicability_notes = check_applicability(d)
        if applicability_notes:
            print("\n【v2 适用性提示 · 仅 warn 不 fail】")
            for n in applicability_notes:
                print(f"  · {n}")

        v21_app_hints, v21_app_warns = check_v21_applicability(d)
        if v21_app_warns:
            print("\n【v2.1 加深版警告 · §2.6/§2.7/§2.8 已填但未达标】")
            for w in v21_app_warns:
                print(f"  ⚠ {w}")
            v21_warnings.extend(v21_app_warns)
        if v21_app_hints:
            print("\n【v2.1 适用性提示 · §4.4-§4.6 新字段（缺失不 fail）】")
            for n in v21_app_hints:
                print(f"  · {n}")

    # 9. v2.2 排版警告（§10）
    v22_warnings = []
    if not legacy:
        print("\n【v2.2 排版警告 · 见 deepening-protocol §10 重点突出与排版规范】")
        v22_warnings = check_v22_typography(d)
        if v22_warnings:
            print("  · 长字段段落数 / 关键短语标记 未达 §10 排版下限：")
            for w in v22_warnings[:20]:
                print(f"  ⚠ {w}")
            if len(v22_warnings) > 20:
                print(f"  ⋯ （余 {len(v22_warnings) - 20} 条同类排版警告）")
        else:
            print("  ✓ v2.2 排版规范全部达标")

    # ─── 汇总 ───────────────────────────────────────
    print("\n" + "━" * 60)
    print("【v1 硬红线】 — 违反 = 不合格")
    hard_issues = len(errors) + total_hits + len(framework_hits) + len(missing)
    print(f"  结构错误: {len(errors)} | 禁词命中: {total_hits} | 框架名命中: {len(framework_hits)} | 三层缺失: {len(missing)}")
    print(f"  硬红线合计: {hard_issues}")

    print("\n【软警告】 — 参考指标")
    soft_count = 0
    if char_count > 0:
        density = facts_count * 1000 / char_count
        if density < 2:
            print(f"  · 事实密度 {density:.2f}/千字 < 目标 2.0")
            soft_count += 1
        if char_count < 6000:
            print(f"  · 字数 {char_count} < 基本充实线 6000")
            soft_count += 1
    if soft_count == 0:
        print(f"  · 无软警告")

    if not legacy:
        print(f"\n【v2 加深版警告】 — 不阻断硬红线，但应推动改进")
        print(f"  v2.0 深度警告: {len(v2_warnings)} 条")
        print(f"  v2 适用性提示: {len(applicability_notes)} 条")

        print(f"\n【v2.1 加深版警告】 — 当前协议主线（v2.0 产物会在此看到升级所需项）")
        print(f"  v2.1 深度警告: {len(v21_warnings)} 条")

        print(f"\n【v2.1 适用性提示】 — §2.6/§2.7/§2.8 新字段（不适用书可空）")
        print(f"  v2.1 适用性提示: {len(v21_app_hints)} 条")

        print(f"\n【v2.2 排版警告】 — §10 重点突出与排版规范")
        print(f"  v2.2 排版警告: {len(v22_warnings)} 条")

    print("━" * 60)
    if hard_issues == 0:
        suffix_parts = []
        if soft_count:
            suffix_parts.append(f"{soft_count} 条软警告")
        if not legacy and v2_warnings:
            suffix_parts.append(f"{len(v2_warnings)} 条 v2.0 警告")
        if not legacy and v21_warnings:
            suffix_parts.append(f"{len(v21_warnings)} 条 v2.1 加深版警告（建议回流加深）")
        if not legacy and applicability_notes:
            suffix_parts.append(f"{len(applicability_notes)} 条 v2 适用性提示")
        if not legacy and v21_app_hints:
            suffix_parts.append(f"{len(v21_app_hints)} 条 v2.1 适用性提示")
        if suffix_parts:
            print(f"✓ v1 硬红线全部通过（{'；'.join(suffix_parts)}）")
        else:
            print("✓ v1 硬红线全部通过")
    else:
        print(f"✗ v1 硬红线 {hard_issues} 处违反，需修正")
    print("━" * 60)

    # 退出码：仅 v1 硬红线决定 pass/fail（v2/v2.1 警告不阻断 → 向后兼容）
    sys.exit(0 if hard_issues == 0 else 1)


if __name__ == "__main__":
    main()
