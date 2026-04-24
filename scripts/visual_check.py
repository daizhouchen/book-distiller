#!/usr/bin/env python3
"""
visual_check.py — 渲染后 HTML 的视觉级自检（无浏览器）

使用：
    python scripts/visual_check.py <rendered.html>

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

不依赖浏览器,纯解析。快且可靠。
"""

import re
import sys
from pathlib import Path


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
def check_mode_differentiation(html):
    """三模式差异化检查。"""
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
    # 差异幅度：intermediate 应该比 brief 大至少 30%，full 比 intermediate 大至少 20%
    if brief_c and inter_c < brief_c * 1.3:
        problems.append(
            f"速读→精读增量不足 30%（{brief_c}→{inter_c}）"
        )
    if inter_c and full_c < inter_c * 1.2:
        problems.append(
            f"精读→深读增量不足 20%（{inter_c}→{full_c}）"
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


# ─── 主入口 ─────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("Usage: visual_check.py <rendered.html>", file=sys.stderr)
        sys.exit(1)

    html_path = Path(sys.argv[1])
    html = html_path.read_text(encoding='utf-8')

    print("━" * 60)
    print(f"视觉级自检 · {html_path.name}")
    print("━" * 60)

    total_problems = 0

    # 1. 三模式差异化
    ok, data = check_mode_differentiation(html)
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

    print("\n" + "━" * 60)
    if total_problems == 0:
        print("✓ 视觉级自检全部通过")
    else:
        print(f"✗ 发现 {total_problems} 处视觉问题，需修正")
    print("━" * 60)

    sys.exit(0 if total_problems == 0 else 1)


if __name__ == "__main__":
    main()
