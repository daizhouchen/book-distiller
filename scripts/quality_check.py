#!/usr/bin/env python3
"""
quality_check.py — 对 distill.json / 生成的 HTML 做质量检查

使用：
    python scripts/quality_check.py <distill.json>
    python scripts/quality_check.py <distill.json> <rendered.html>

检查项（见 SKILL.md 步骤 8）：
- 结构完整性
- 密度指标（事实/推导/千字）
- 禁词扫描（网感词/营销体/作者腔/总结废话）
- 正文出现框架名次数（应为 0，工具箱除外）
- 必需模块存在性
"""

import json
import re
import sys
from pathlib import Path


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


def check_distill_schema(d):
    """检查 distill.json 结构完整性。"""
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

    if "misreadings" not in d or len(d.get("misreadings", [])) < 2:
        errors.append("误读陷阱不足 2 条")

    if "blindspots" not in d or len(d.get("blindspots", [])) < 2:
        errors.append("作者盲点不足 2 条")

    if "golden_quotes" not in d or len(d.get("golden_quotes", [])) < 5:
        errors.append("金句不足 5 条")

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


def count_chars_text(text):
    """估算中文字数（非空白非标点字符）。"""
    cleaned = re.sub(r"[\s\W\d]+", "", text, flags=re.UNICODE)
    # 保留中文和字母
    return len(cleaned)


def main():
    if len(sys.argv) < 2:
        print("Usage: quality_check.py <distill.json> [rendered.html]", file=sys.stderr)
        print("\n硬红线（违反算不合格）：结构完整性 / 禁词 / 框架名 / 三重结构", file=sys.stderr)
        print("软警告（参考指标）：事实密度 / 字数 / 信源占比合理性", file=sys.stderr)
        sys.exit(1)

    in_path = Path(sys.argv[1])
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
    print(f"质量检查 · {d.get('meta', {}).get('title', '未命名')}")
    print("━" * 60)

    # 1. Schema
    errors = check_distill_schema(d)
    print("\n【结构完整性】")
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
    print(f"\n【事实锚点】")
    print(f"  quote_pairs 双栏数: {facts_count}")
    if char_count > 0:
        density = facts_count * 1000 / char_count
        print(f"  密度估算: {density:.2f} / 千字（目标 ≥ 2）")
        if density < 2:
            print(f"  ⚠ 事实密度偏低")

    # 4. 禁词扫描
    print("\n【禁词扫描】")
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

    # 5. 框架名扫描（正文禁用，除非在 toolbox）
    print("\n【框架名扫描（正文）】")
    framework_hits = count_char_in(body_text, FRAMEWORK_NAMES)
    if framework_hits:
        print("  ✗ 正文出现框架名（应在工具箱才出现）:")
        for w, c in framework_hits:
            print(f"      「{w}」× {c}")
    else:
        print("  ✓ 正文未出现框架名")

    # 6. 模块三重结构检查
    print("\n【三重结构完整性】")
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

    # 汇总
    print("\n" + "━" * 60)
    print("【硬红线】 — 违反 = 不合格")
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

    print("━" * 60)
    if hard_issues == 0:
        print("✓ 硬红线全部通过" + (f"（有 {soft_count} 条软警告建议优化）" if soft_count else ""))
    else:
        print(f"✗ 硬红线 {hard_issues} 处违反，需修正")
    print("━" * 60)

    sys.exit(0 if hard_issues == 0 else 1)


if __name__ == "__main__":
    main()
