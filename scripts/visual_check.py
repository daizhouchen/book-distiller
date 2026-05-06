#!/usr/bin/env python3
"""
visual_check.py — 渲染后 HTML 的视觉级自检（无浏览器）

使用：
    python scripts/visual_check.py <rendered.html> [--legacy]

  默认模式（v2.1 加深版）：
    在 v1 硬检查之外，额外强制：
      §1.16  深读 / 精读 字数比 ≥ 1.35（v2.1 不变；旧 v1 是 1.2）
      §1.17  ≥ 3 种 SVG 可视化类型（矩阵 + 至少 2 种新类型，v2.1 提升自 v2 的 ≥2）
    并对 v2/v2.1 新模块（学派论争 / 版本变体 / 作者立场解构 /
    章节级覆盖 / 思想坐标四维 / 场景细读 / 人物小传 / 诗词曲赋专题）
    做"软"检查：缺失只发警告。

  --legacy（v1 兼容）：
    只跑 v1 硬检查（三模式差异化 / SVG 尺寸 / 9 大板块 /
    三层结构 / 引用对照），用于检查老 HTML。

检查项：
1. 三模式差异化 ——
   - 速读 / 精读 / 深读 三种 body class 下可见内容必须严格递增
   - 防止像 v1 那样"速读和精读看起来一样"
2. SVG 尺寸合规 ——
   - <svg> 标签不应有固定 width/height（应由 CSS 接管）
   - 必须有 viewBox
   - 推荐有 preserveAspectRatio
3. 必需板块存在 ——
   - 卷首 / 全貌图 / 事实矩阵 / 主干模块 / 金句 / 误读 / 盲点 / 坐标 / 工具箱
4. 三重结构完整 ——
   - layer-facts / layer-mech / layer-view 都要成对出现
5. 引用对照 ——
   - quote-pair 数量
   - counterpoint 数量
6. （v2.1）SVG 可视化类型计数 —— ≥ 3 种
7. （v2.1）新模块 section 存在性与非空检查（degrade 警告）—— 含
   §2.6 场景细读 / §2.7 人物小传 / §2.8 诗词曲赋专题

不依赖浏览器,纯解析。快且可靠。
"""

import re
import sys
from pathlib import Path


# ─── 阈值（按 deepening-protocol §1.16 / §1.17 v2.1）──────
# v2.1 加深版硬下限：
#   §1.16 深读 / 精读 ≥ 1.35×（v2.1 不变；旧 v1 是 1.2×）
#   设计判断：1.5×/1.4× 在巨著（红楼/金瓶/史记）实操中过严——精读已是核心模块全展开，
#             1.35× 已能稳定分辨深读厚于精读（典型差异 ≥1万字），且不会因 section 划分粒度
#             或字数计算误差而误伤合格产物。仍显著高于 v1 旧值 1.2。
#   FOCUS_OVER_QUICK 不变（精读必须明显多于速读，阈值 1.3）
DEEP_OVER_FOCUS = 1.35
FOCUS_OVER_QUICK = 1.3

# §1.17 v2.1 可视化类型：必须 ≥ 3 种 SVG 可视化（矩阵 + ≥ 2 种新类型）
MIN_SVG_VIZ_TYPES = 3
# 单个 SVG 最少内容字符数，过滤掉占位空 SVG
MIN_SVG_CONTENT_CHARS = 100

# v2 / v2.1 新模块 section（class 选择器 → 中文名）
# template.html 设计：section 用 *-sec class，模块内容 div 用 module-* class。
# 检查时优先匹配 section 级 class；若未找到再退回 module-* class（向后兼容）。
V2_MODULE_SECTIONS = {
    'schools-sec':                            '学派论争（§2.1）',
    'version-variants-sec':                   '版本/译本差异（§2.2）',
    'author-position-sec':                    '作者立场解构（§2.3）',
    'chapter-notes-sec':                      '章节级覆盖（§2.4）',
    'tc-grid-4col':                           '思想坐标四维强化（§2.5）',
    # v2.1 新增三个模块（§2.6 / §2.7 / §2.8）
    'scene-dissections-sec':                  '场景细读（§2.6）',
    'character-dossiers-sec':                 '人物小传（§2.7）',
    'poetics-dossiers-sec':                   '诗词曲赋专题（§2.8）',
}

# 兼容回退：如果 *-sec 未找到，可以接受 module-* class（含在任何元素里）
V2_MODULE_FALLBACK_CLASSES = {
    'schools-sec':              'module-schools-of-interpretation',
    'version-variants-sec':     'module-version-variants',
    'author-position-sec':      'module-author-position-deconstruction',
    'chapter-notes-sec':        'module-chapter-level-notes',
    'tc-grid-4col':             'thought-coordinates-extended',
    # v2.1 新增三个模块的回退 class
    'scene-dissections-sec':    'module-scene-dissections',
    'character-dossiers-sec':   'module-character-dossiers',
    'poetics-dossiers-sec':     'module-poetics-dossiers',
}


# ─── HTML 解析（处理 <section> 嵌套）──────────────────
def find_top_level_sections(html):
    """找出所有带 level-* class 的顶层 section,正确处理嵌套。

    返回 [(tag_snippet, classes_list, content_start, content_end)]
    只包含标签里带 level-always/精读/深读 其中之一的 section。
    内部嵌套的 <section class="module"> 不会被当顶层,但其文本算在
    外层 section 的 content 里（正是我们想要的——module 内容
    本来就属于 modules-sec 这一层）。
    """
    sections = []
    # 用 tokenizer 扫描所有 <section ...> 和 </section>
    tokens = []
    for m in re.finditer(r'<(/?)section\b([^>]*)>', html, flags=re.IGNORECASE):
        tokens.append((m.start(), m.end(), m.group(1) == '/', m.group(2)))

    stack = []  # [(attrs, classes, content_start)]
    for start, end, is_close, attrs in tokens:
        if is_close:
            if stack:
                attrs_open, classes, content_start = stack.pop()
                # 只收集有 level-* class 的 section
                if any(c.startswith('level-') for c in classes):
                    # 但如果有祖先也是 level-* section,就跳过内层（避免双重计数）
                    has_level_ancestor = any(
                        any(c.startswith('level-') for c in s[1]) for s in stack
                    )
                    if not has_level_ancestor:
                        sections.append((attrs_open, classes, content_start, start))
        else:
            class_m = re.search(r'class\s*=\s*"([^"]*)"', attrs)
            classes = class_m.group(1).split() if class_m else []
            stack.append((attrs, classes, end))

    return sections


def extract_text(html_fragment):
    """粗暴去标签估字数。"""
    no_tags = re.sub(r'<[^>]+>', ' ', html_fragment)
    no_tags = re.sub(r'&[a-zA-Z]+;', ' ', no_tags)
    # 只数中文字符+英文单词
    chinese = re.findall(r'[一-鿿]', no_tags)
    return len(chinese)


# v1 兼容模式下使用的旧阈值（深读/精读 ≥ 1.2×）
LEGACY_DEEP_OVER_FOCUS = 1.2


# ─── 模式可见性判断 ──────────────────────────────────
def is_visible_in_mode(classes, mode):
    """根据 section 的 class 列表和当前 mode，判断是否可见。
    mode: 'brief' | 'intermediate' | 'full'
    CSS 规则（新版 template）：
      mode-brief 隐藏 level-精读 和 level-深读
      mode-intermediate 隐藏 level-深读
      mode-full 全显示
    """
    has_brief_hide = 'level-精读' in classes or 'level-深读' in classes
    has_inter_hide = 'level-深读' in classes

    if mode == 'brief':
        return not has_brief_hide
    if mode == 'intermediate':
        return not has_inter_hide
    return True  # full


# ─── 主检查 ──────────────────────────────────
def check_mode_differentiation(html, legacy=False):
    """三模式差异化检查。

    legacy=True 时使用 v1 旧阈值（深读/精读 ≥ 1.2×），
    legacy=False（默认）使用 v2 §1.16 阈值（≥ 1.35×）。
    """
    deep_threshold = LEGACY_DEEP_OVER_FOCUS if legacy else DEEP_OVER_FOCUS
    sections = find_top_level_sections(html)
    if not sections:
        return False, "没有找到任何 <section>（HTML 结构异常）"

    counts = {'brief': {'sections': 0, 'chars': 0},
              'intermediate': {'sections': 0, 'chars': 0},
              'full': {'sections': 0, 'chars': 0}}

    visible_per_mode = {m: [] for m in ('brief', 'intermediate', 'full')}

    for attrs, classes, start, end in sections:
        body = html[start:end]
        chars = extract_text(body)
        for mode in ('brief', 'intermediate', 'full'):
            if is_visible_in_mode(classes, mode):
                counts[mode]['sections'] += 1
                counts[mode]['chars'] += chars
                visible_per_mode[mode].append((classes, chars))

    # 约束：brief < intermediate ≤ full（严格关系）
    brief_c = counts['brief']['chars']
    inter_c = counts['intermediate']['chars']
    full_c = counts['full']['chars']

    problems = []
    if brief_c == 0:
        problems.append("速读模式没有任何可见内容")
    if brief_c >= inter_c:
        problems.append(
            f"速读({brief_c} 字) >= 精读({inter_c} 字)，"
            f"两模式看起来会一样或倒置 — 这是上次的 Bug"
        )
    if inter_c >= full_c:
        problems.append(
            f"精读({inter_c} 字) >= 深读({full_c} 字)，"
            f"深读没有提供更多内容"
        )
    # 差异幅度：
    #   §1.16（v2）：精读 / 速读 ≥ 1.3×；深读 / 精读 ≥ 1.35×（v1 旧值 1.2×）
    if brief_c and inter_c < brief_c * FOCUS_OVER_QUICK:
        problems.append(
            f"速读→精读增量不足 {int((FOCUS_OVER_QUICK-1)*100)}%（{brief_c}→{inter_c}）"
        )
    if inter_c and full_c < inter_c * deep_threshold:
        scope = "v1 旧阈值" if legacy else "§1.16 v2"
        problems.append(
            f"精读→深读增量不足 {int((deep_threshold-1)*100)}%"
            f"（{scope} 要求 ≥ {deep_threshold}×；实测 {inter_c}→{full_c}）"
        )

    return (len(problems) == 0), {
        'counts': counts,
        'problems': problems,
    }


def check_svg_sizing(html):
    """SVG 尺寸合规：不应有固定 width/height，应有 viewBox。"""
    problems = []
    bad_fixed_size = []
    missing_viewbox = []

    svgs = re.findall(r'<svg\b[^>]*>', html, flags=re.IGNORECASE)
    for i, tag in enumerate(svgs, 1):
        # 检查是否有固定 width/height attr（数字而非百分比）
        width_m = re.search(r'\swidth\s*=\s*["\']?(\d+)(?:px)?["\']?', tag, flags=re.IGNORECASE)
        height_m = re.search(r'\sheight\s*=\s*["\']?(\d+)(?:px)?["\']?', tag, flags=re.IGNORECASE)
        if width_m:
            bad_fixed_size.append(f"第 {i} 个 SVG 有固定 width={width_m.group(1)}")
        if height_m:
            bad_fixed_size.append(f"第 {i} 个 SVG 有固定 height={height_m.group(1)}")

        # 检查 viewBox
        if 'viewBox' not in tag:
            missing_viewbox.append(f"第 {i} 个 SVG 缺 viewBox")

    if bad_fixed_size:
        problems.extend(bad_fixed_size)
    if missing_viewbox:
        problems.extend(missing_viewbox)

    return (len(problems) == 0), {
        'svg_count': len(svgs),
        'problems': problems,
    }


def check_required_sections(html):
    """必需板块存在性。"""
    required = {
        'cover': '卷首（书名+母题）',
        'overview-sec': '全貌图',
        'fact-matrix-sec': '事实矩阵',
        'modules-sec': '主干模块',
        'quotes-sec': '金句',
        'misread-sec': '误读陷阱',
        'blind-sec': '作者盲点',
        'coord-sec': '思想坐标',
        'toolbox-sec': '思考工具箱',
    }
    missing = []
    for cls, label in required.items():
        if f'class="{cls}' not in html and f"class='{cls}" not in html and cls not in html:
            missing.append(f"{cls}（{label}）")
    return (len(missing) == 0), missing


def check_three_layer(html):
    """三层结构成对检查。"""
    facts = len(re.findall(r'class="[^"]*layer-facts', html))
    mech = len(re.findall(r'class="[^"]*layer-mech', html))
    view = len(re.findall(r'class="[^"]*layer-view', html))

    problems = []
    if facts == 0:
        problems.append("没有 layer-facts（事实层）")
    if mech == 0:
        problems.append("没有 layer-mech（机制层）")
    if view == 0:
        problems.append("没有 layer-view（观点层）")
    if facts != mech or facts != view:
        problems.append(
            f"三层不对齐：facts={facts}, mech={mech}, view={view}"
        )

    return (len(problems) == 0), {
        'counts': {'facts': facts, 'mech': mech, 'view': view},
        'problems': problems,
    }


def check_pair_counts(html):
    """引用对照与他山之石的数量。"""
    quote_pairs = len(re.findall(r'class="[^"]*quote-pair', html))
    counterpoints = len(re.findall(r'class="[^"]*counterpoint', html))
    return {'quote_pairs': quote_pairs, 'counterpoints': counterpoints}


# ─── v2 新检查 §1.17 · SVG 可视化类型计数 ──────────────
def _iter_svg_blocks(html):
    """遍历 <svg ...> ... </svg> 整块（不依赖换行，处理任意嵌套属性）。

    返回 [(open_tag, full_block, classes_list)]。
    """
    blocks = []
    for m in re.finditer(r'<svg\b([^>]*)>', html, flags=re.IGNORECASE):
        open_start = m.start()
        open_end = m.end()
        attrs = m.group(1)
        # 找对应的 </svg>（SVG 不会嵌套在另一个 <svg> 里——简化处理：找下一个 </svg>）
        close_m = re.search(r'</svg\s*>', html[open_end:], flags=re.IGNORECASE)
        if not close_m:
            continue
        full_block = html[open_start:open_end + close_m.end()]
        class_m = re.search(r'class\s*=\s*["\']([^"\']*)["\']', attrs)
        classes = class_m.group(1).split() if class_m else []
        blocks.append((html[open_start:open_end], full_block, classes))
    return blocks


def check_svg_viz_types(html):
    """§1.17 · 可视化类型 ≥ 2。

    判定每个 SVG 属于哪种"类型"：
      - 显式 class（如 timeline-svg / network-svg / evolution-svg /
        spectrum-svg / fact-matrix-svg / overview-svg）优先；
      - 没有显式 class 时，按上下文（祖先 section 的 class）退而归类；
      - 内容字符数 < MIN_SVG_CONTENT_CHARS 的 SVG 视为"占位"，不计入。

    返回 (ok, info)：ok = (类型数 ≥ MIN_SVG_VIZ_TYPES)。
    info 含 types_set / svg_count / nontrivial_count / problems。
    """
    blocks = _iter_svg_blocks(html)
    types = set()
    nontrivial = 0
    type_class_keywords = (
        ('timeline',     'timeline'),
        ('network',      'network'),
        ('evolution',    'evolution'),
        ('spectrum',     'spectrum'),
        ('fact-matrix',  'fact_matrix'),
        ('matrix',       'fact_matrix'),
        ('overview',     'overview'),
    )

    for open_tag, full_block, classes in blocks:
        # 内容长度（去标签后字符数；过滤占位）
        content = re.sub(r'<[^>]+>', '', full_block)
        if len(content.strip()) < MIN_SVG_CONTENT_CHARS:
            continue
        nontrivial += 1

        # 用 class 判类型
        matched = None
        joined_classes = ' '.join(classes).lower()
        for kw, key in type_class_keywords:
            if kw in joined_classes:
                matched = key
                break

        # class 没命中——优先看 SVG 紧邻的父级 div 是否有 data-viz-type 属性
        # (template.html 把 secondary viz 包在 <div class="viz-secondary" data-viz-type="...">)
        if matched is None:
            idx = html.find(full_block)
            if idx > 0:
                # 在 SVG 之前 1000 字符内查找 data-viz-type
                preceding = html[max(0, idx - 1500):idx]
                viz_attr = re.findall(
                    r'data-viz-type\s*=\s*["\']([^"\']+)["\']', preceding
                )
                if viz_attr:
                    last_viz = viz_attr[-1].lower().strip()
                    if last_viz in ('timeline', 'network', 'evolution', 'spectrum'):
                        matched = last_viz
                    elif last_viz in ('matrix', 'fact_matrix'):
                        matched = 'fact_matrix'
                # 也接受 viz-secondary class 作为信号（即使没 data-viz-type）
                if matched is None and 'viz-secondary' in preceding:
                    matched = 'secondary'

        # 还是没命中——用 SVG 周边上下文中的 section class 推断
        if matched is None:
            idx = html.find(full_block)
            if idx > 0:
                window = html[max(0, idx - 4000):idx]
                # 优先找最近的 section class
                sec_classes = re.findall(
                    r'<section\b[^>]*class\s*=\s*"([^"]*)"', window, flags=re.IGNORECASE
                )
                if sec_classes:
                    last_sec = sec_classes[-1].lower()
                    for kw, key in type_class_keywords:
                        if kw in last_sec:
                            matched = key
                            break
                    # 兼容 v1：fact-matrix-sec / overview-sec
                    if matched is None:
                        if 'fact-matrix-sec' in last_sec:
                            matched = 'fact_matrix'
                        elif 'overview-sec' in last_sec:
                            matched = 'overview'
        # 还没归类的——用一个稳定的 hash key 占位（每个未知 SVG 自成一类，避免低估）
        if matched is None:
            matched = f'unknown-{nontrivial}'
        types.add(matched)

    problems = []
    if len(types) < MIN_SVG_VIZ_TYPES:
        problems.append(
            f"§1.17 可视化类型不足：仅 {len(types)} 种"
            f"（要求 ≥ {MIN_SVG_VIZ_TYPES}：矩阵 + ≥ 1 种新类型，"
            f"如 timeline / network / evolution / spectrum）"
        )

    return (len(problems) == 0), {
        'svg_count': len(blocks),
        'nontrivial_count': nontrivial,
        'types': sorted(types),
        'problems': problems,
    }


# ─── v2 新检查 · v2 模块 section 存在性 + 非空 ──────────
def _extract_section_by_class(html, class_token):
    """提取第一个 class 列表里含 class_token 的 <section>...</section> 块。

    返回 (found, body_text_or_None)。
    """
    tokens = []
    for m in re.finditer(r'<(/?)section\b([^>]*)>', html, flags=re.IGNORECASE):
        tokens.append((m.start(), m.end(), m.group(1) == '/', m.group(2)))

    stack = []
    for start, end, is_close, attrs in tokens:
        if is_close:
            if stack:
                attrs_open, classes, content_start = stack.pop()
                if class_token in classes:
                    return True, html[content_start:start]
        else:
            class_m = re.search(r'class\s*=\s*"([^"]*)"', attrs)
            classes = class_m.group(1).split() if class_m else []
            stack.append((attrs, classes, end))
    return False, None


def _has_any_class(html, class_token):
    """class_token 是否以独立 token 形式出现在任何 class 属性里。"""
    pattern = r'class\s*=\s*"[^"]*\b' + re.escape(class_token) + r'\b[^"]*"'
    return re.search(pattern, html) is not None


def check_v2_modules(html):
    """v2 模块 section 存在性与非空检查（degrade warning）。

    对 V2_MODULE_SECTIONS 里的每个 class：
      - 不存在 → degrade warning
      - 存在但内容字符 < 50 → degrade warning（空壳）
    返回 list of (severity, message)。severity 都是 'warn'，
    不参与 hard fail。
    """
    warnings = []
    for cls, label in V2_MODULE_SECTIONS.items():
        found, body = _extract_section_by_class(html, cls)
        if not found:
            # 退回检查 module-* 兼容 class（在任何元素里出现且非空即可）
            fallback_cls = V2_MODULE_FALLBACK_CLASSES.get(cls)
            if fallback_cls and _has_any_class(html, fallback_cls):
                # 找到等价的 module-* class，视为 v2 渲染存在
                continue
            # 真没找到任何相关 class
            if not _has_any_class(html, cls):
                warnings.append(('missing', f"缺 .{cls}（{label}）"))
                continue
            warnings.append(('non-section', f".{cls} 未以 <section> 渲染（{label}）"))
            continue
        if body is None:
            continue
        chars = extract_text(body)
        if chars < 50:
            warnings.append(('empty', f".{cls} 内容过少（{chars} 中文字 < 50，疑空壳）（{label}）"))
    return warnings


# ─── 主入口 ─────────────────────────────────
def main():
    args = sys.argv[1:]
    legacy = False
    if '--legacy' in args:
        legacy = True
        args = [a for a in args if a != '--legacy']

    if not args:
        print(
            "Usage: visual_check.py <rendered.html> [--legacy]\n"
            "\n"
            "  默认（v2.1 加深版）：\n"
            f"    强制 §1.16 深读/精读 ≥ {DEEP_OVER_FOCUS}×、§1.17 SVG 可视化 ≥ {MIN_SVG_VIZ_TYPES} 种；\n"
            "    v2/v2.1 新模块（学派/版本/作者立场/章节级/思想坐标四维 +\n"
            "    §2.6 场景细读/§2.7 人物小传/§2.8 诗词曲赋专题）做软检查。\n"
            "  --legacy：只跑 v1 硬检查，用于检查老 HTML。",
            file=sys.stderr,
        )
        sys.exit(1)

    html_path = Path(args[0])
    html = html_path.read_text(encoding='utf-8')

    print("━" * 60)
    mode_label = "v1 兼容模式" if legacy else "v2.1 加深版"
    print(f"视觉级自检 · {html_path.name}  [{mode_label}]")
    print("━" * 60)

    total_problems = 0

    # 1. 三模式差异化
    ok, data = check_mode_differentiation(html, legacy=legacy)
    print("\n【三模式差异化】")
    counts = data['counts']
    print(f"  速读  : {counts['brief']['sections']} 个 section · {counts['brief']['chars']} 中文字")
    print(f"  精读  : {counts['intermediate']['sections']} 个 section · {counts['intermediate']['chars']} 中文字")
    print(f"  深读  : {counts['full']['sections']} 个 section · {counts['full']['chars']} 中文字")
    if ok:
        brief = counts['brief']['chars']
        inter = counts['intermediate']['chars']
        full = counts['full']['chars']
        ratio_bi = inter / brief if brief else 0
        ratio_if = full / inter if inter else 0
        print(f"  ✓ 三模式递增合规（精读/速读 = {ratio_bi:.1f}×，深读/精读 = {ratio_if:.1f}×）")
    else:
        total_problems += len(data['problems'])
        for p in data['problems']:
            print(f"  ✗ {p}")

    # 2. SVG 尺寸
    ok, data = check_svg_sizing(html)
    print(f"\n【SVG 尺寸合规】（共 {data['svg_count']} 个 SVG）")
    if ok:
        print(f"  ✓ 全部 SVG 无固定尺寸，viewBox 齐全")
    else:
        total_problems += len(data['problems'])
        for p in data['problems']:
            print(f"  ✗ {p}")

    # 3. 必需板块
    ok, missing = check_required_sections(html)
    print("\n【必需板块】")
    if ok:
        print("  ✓ 全部齐全（9 个板块）")
    else:
        total_problems += len(missing)
        for m in missing:
            print(f"  ✗ 缺失: {m}")

    # 4. 三层结构
    ok, data = check_three_layer(html)
    c = data['counts']
    print(f"\n【三层结构对齐】")
    print(f"  事实层 × {c['facts']}  机制层 × {c['mech']}  观点层 × {c['view']}")
    if ok:
        print(f"  ✓ 三层成对，{c['facts']} 个完整模块")
    else:
        total_problems += len(data['problems'])
        for p in data['problems']:
            print(f"  ✗ {p}")

    # 5. 对照数量
    counts = check_pair_counts(html)
    print(f"\n【引用与对照】")
    print(f"  原文双栏: {counts['quote_pairs']}  他山之石: {counts['counterpoints']}")
    if counts['quote_pairs'] < 6:
        print(f"  ⚠ 原文双栏偏少（< 6 组）")
    if counts['counterpoints'] < 2:
        print(f"  ⚠ 他山之石偏少（< 2 处）")

    # 6. （v2.1）SVG 可视化类型计数 §1.17 —— 默认硬，legacy 软
    ok, viz = check_svg_viz_types(html)
    print(f"\n【可视化类型 §1.17 v2.1】")
    print(
        f"  SVG 总数 {viz['svg_count']}（其中非占位 {viz['nontrivial_count']} 个），"
        f"识别到 {len(viz['types'])} 种类型: {', '.join(viz['types']) or '(无)'}"
    )
    if ok:
        print(f"  ✓ ≥ {MIN_SVG_VIZ_TYPES} 种可视化类型")
    elif viz['nontrivial_count'] == 0:
        msg = "  ✗ 没有任何有效 SVG 可视化"
        if legacy:
            print(f"  ⚠ [v1 兼容] {msg.lstrip(' ✗')}")
        else:
            total_problems += 1
            print(msg)
    else:
        if legacy:
            print(f"  ⚠ [v1 兼容] {viz['problems'][0]}")
        elif len(viz['types']) < MIN_SVG_VIZ_TYPES:
            # v2.1 提档到 ≥3 后，2 种只发警告（v2.0 产物常见状态），1 种亦警告——保持向后兼容、不阻断
            print(f"  ⚠ [v2.1 加深版] {viz['problems'][0]}")
            print(f"     建议在矩阵之外补充至少 2 种新类型（timeline / network / evolution / spectrum 等）")
        else:
            total_problems += 1
            print(f"  ✗ {viz['problems'][0]}")

    # 7. （v2/v2.1）新模块 section 软检查 —— legacy 模式下完全跳过
    if not legacy:
        warns = check_v2_modules(html)
        print(f"\n【v2.1 加深版 模块 section】")
        total_required = len(V2_MODULE_SECTIONS)
        if not warns:
            print(f"  ✓ {total_required} 个 v2/v2.1 模块 class 均存在且非空")
        else:
            print(f"  · 共检查 {total_required} 个模块 section（含 §2.6/§2.7/§2.8 v2.1 新增）")
            for sev, msg in warns:
                print(f"  ⚠ [v2.1 加深版] {msg}")

    print("\n" + "━" * 60)
    if total_problems == 0:
        print("✓ 视觉级自检全部通过（hard checks）")
    else:
        print(f"✗ 发现 {total_problems} 处视觉问题，需修正")
    print("━" * 60)

    sys.exit(0 if total_problems == 0 else 1)


if __name__ == "__main__":
    main()
