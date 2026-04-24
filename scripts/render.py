#!/usr/bin/env python3
"""
render.py — 把 distill.json 渲染为典雅风 HTML

使用：
    python scripts/render.py <distill.json> <output.html>

distill.json schema 见 SKILL.md 步骤 6。
"""

import json
import sys
import html
import re
from pathlib import Path


def esc(s):
    """HTML-escape 文本内容。"""
    if s is None:
        return ""
    return html.escape(str(s))


def normalize_svg(svg_str):
    """归一化 SVG：去掉内联 width/height/style，让 CSS 接管尺寸。
    保留 viewBox（否则无法缩放）。"""
    if not svg_str or "<svg" not in svg_str:
        return svg_str
    # 定位 <svg ... > 开头标签
    m = re.search(r'<svg\b([^>]*)>', svg_str, flags=re.IGNORECASE)
    if not m:
        return svg_str
    attrs = m.group(1)
    # 去掉固定的 width/height 属性
    attrs = re.sub(r'\s(width|height)\s*=\s*["\']?[^"\'\s>]+["\']?', '', attrs, flags=re.IGNORECASE)
    # 去掉 style 里与尺寸相关的条目，保留其他样式
    def strip_size_style(m2):
        style = m2.group(1)
        parts = [p.strip() for p in style.split(';') if p.strip()]
        kept = []
        for p in parts:
            k = p.split(':')[0].strip().lower()
            if k in ('width', 'max-width', 'min-width', 'height', 'max-height', 'min-height'):
                continue
            kept.append(p)
        if not kept:
            return ''
        return f' style="{"; ".join(kept)}"'
    attrs = re.sub(r'\s*style\s*=\s*"([^"]*)"', strip_size_style, attrs, flags=re.IGNORECASE)
    attrs = re.sub(r"\s*style\s*=\s*'([^']*)'", strip_size_style, attrs, flags=re.IGNORECASE)
    # 确保有 preserveAspectRatio（居中、不裁剪）
    if 'preserveAspectRatio' not in attrs:
        attrs += ' preserveAspectRatio="xMidYMid meet"'
    return svg_str[:m.start()] + f'<svg{attrs}>' + svg_str[m.end():]


def render_source_meta(source_mix):
    """渲染信源构成条形图。"""
    if not source_mix:
        return "<p>信源构成未标注</p>"

    labels = {
        "A": "A 级 · 原书原文",
        "B": "B 级 · 权威学术/研究型长评",
        "C": "C 级 · 普通书评/网络",
        "D": "D 级 · 模型补全（未核证）",
    }

    a = source_mix.get("A", 0)
    b = source_mix.get("B", 0)
    ab = a + b

    if a >= 0.6 and b >= 0.2:
        conf = "高 ⭐⭐⭐⭐⭐"
    elif a >= 0.4 and ab >= 0.65:
        conf = "中高 ⭐⭐⭐⭐"
    elif a >= 0.2 and ab >= 0.5:
        conf = "中 ⭐⭐⭐"
    elif a >= 0.2:
        conf = "低 ⭐⭐（基于二手资料为主）"
    else:
        conf = "不宜产出 ⭐（建议用户上传原文）"

    rows = []
    for level in ["A", "B", "C", "D"]:
        pct = source_mix.get(level, 0)
        bar_width = f"{int(pct * 100)}%"
        rows.append(
            f'<div class="source-row">'
            f'<span style="width:12em;">{labels[level]}</span>'
            f'<div class="source-bar {level.lower()}" style="position:relative;">'
            f'<span style="position:absolute;top:0;left:0;bottom:0;width:{bar_width};background:inherit;"></span>'
            f'</div>'
            f'<span style="width:4em;text-align:right;">{int(pct*100)}%</span>'
            f'</div>'
        )
    rows_html = "\n".join(rows)

    # Use a simpler bar rendering since we can't nest ::before dynamically
    simple_rows = []
    for level in ["A", "B", "C", "D"]:
        pct = source_mix.get(level, 0)
        pct_str = f"{int(pct * 100)}%"
        color_map = {"A": "#8b3a3a", "B": "#b89b66", "C": "#5b7a6a", "D": "#8a8a8a"}
        simple_rows.append(
            f'<div class="source-row">'
            f'<span style="flex:0 0 11em;">{labels[level]}</span>'
            f'<div style="flex:1;height:12px;background:#f9f5ec;border:1px solid rgba(139,58,58,0.1);position:relative;">'
            f'<div style="position:absolute;top:0;left:0;bottom:0;width:{pct_str};background:{color_map[level]};"></div>'
            f'</div>'
            f'<span style="flex:0 0 3em;text-align:right;">{pct_str}</span>'
            f'</div>'
        )

    return "\n".join(simple_rows) + f'<p style="margin-top:1em;"><strong>置信度自评：</strong>{conf}</p>'


def render_quote_pair(pair):
    """渲染原文-解读双栏。"""
    original = esc(pair.get("original", ""))
    analysis = esc(pair.get("analysis", ""))
    return f"""
<div class="quote-pair">
  <div class="quote-original">{original}</div>
  <div class="quote-analysis">{analysis}</div>
</div>
"""


def render_counterpoint(cp):
    """渲染他山之石对照块。"""
    source = esc(cp.get("source", ""))
    view = esc(cp.get("view", ""))
    judgment = esc(cp.get("our_judgment", ""))
    return f"""
<div class="counterpoint">
  <p><strong>{source}</strong>：{view}</p>
  <p style="margin-top:0.4em;"><em>我们的判断：</em>{judgment}</p>
</div>
"""


def render_module(m, idx):
    """渲染单个内容模块（三重结构 + 对照 + 他山之石）。"""
    title = esc(m.get("title", "未命名模块"))

    # 三重结构
    facts = m.get("facts_layer", {})
    mech = m.get("mechanism_layer", {})
    view = m.get("viewpoint_layer", {})

    facts_html = ""
    if isinstance(facts, dict):
        systematized = facts.get("systematized_facts", "")
        facts_html = esc(systematized) if isinstance(systematized, str) else json.dumps(systematized, ensure_ascii=False)
    elif isinstance(facts, str):
        facts_html = esc(facts)

    mech_html = ""
    if isinstance(mech, dict):
        patterns = mech.get("single_dim_patterns", [])
        weaving = mech.get("cross_dim_weaving", "")
        patterns_list = "".join(f"<li>{esc(p)}</li>" for p in patterns) if patterns else ""
        mech_html = ""
        if patterns_list:
            mech_html += f"<p><strong>单维度规律：</strong></p><ul>{patterns_list}</ul>"
        if weaving:
            mech_html += f"<p><strong>跨维度交织：</strong>{esc(weaving)}</p>"
    elif isinstance(mech, str):
        mech_html = esc(mech)

    view_html = ""
    if isinstance(view, dict):
        claim = view.get("core_claim", "")
        transfer = view.get("modern_transfer", "")
        caveats = view.get("caveats", "")
        if claim:
            view_html += f"<p><strong>核心判断：</strong>{esc(claim)}</p>"
        if transfer:
            view_html += f"<p><strong>现代迁移：</strong>{esc(transfer)}</p>"
        if caveats:
            view_html += f"<p><strong>边界：</strong>{esc(caveats)}</p>"
    elif isinstance(view, str):
        view_html = esc(view)

    # 原文对照
    pairs_html = "\n".join(render_quote_pair(p) for p in m.get("quote_pairs", []))

    # 他山之石
    counters_html = "\n".join(render_counterpoint(c) for c in m.get("external_counterpoints", []))

    return f"""
<section class="module">
  <h3 class="section">{title}</h3>

  <div class="three-layer">
    <div class="layer layer-facts">
      <span class="layer-label"></span>
      {facts_html}
    </div>
    <div class="layer layer-mech">
      <span class="layer-label"></span>
      {mech_html}
    </div>
    <div class="layer layer-view">
      <span class="layer-label"></span>
      {view_html}
    </div>
  </div>

  {pairs_html}
  {counters_html}
</section>
"""


def render_fact_matrix_table(fm):
    """把 fact_matrix.cells 渲染成表格（如果没有 SVG 就用表格）。"""
    if not fm:
        return ""
    cells = fm.get("cells", {})
    if not cells:
        return ""

    # 解析 cells 格式：key 形如 "维度A值×维度B值"
    rows = {}
    cols = set()
    for key, val in cells.items():
        parts = key.split("×") if "×" in key else key.split("x")
        if len(parts) != 2:
            continue
        row_k, col_k = parts[0].strip(), parts[1].strip()
        cols.add(col_k)
        rows.setdefault(row_k, {})[col_k] = val

    if not rows:
        return ""
    cols_list = sorted(cols)
    rows_list = list(rows.keys())

    thead = "<thead><tr><th></th>" + "".join(f"<th>{esc(c)}</th>" for c in cols_list) + "</tr></thead>"
    tbody_parts = []
    for r in rows_list:
        cells_parts = [f"<th>{esc(r)}</th>"]
        for c in cols_list:
            v = rows[r].get(c, "")
            if isinstance(v, list):
                v_str = "；".join(str(x) for x in v)
            else:
                v_str = str(v)
            cells_parts.append(f"<td>{esc(v_str)}</td>")
        tbody_parts.append("<tr>" + "".join(cells_parts) + "</tr>")
    tbody = "<tbody>" + "".join(tbody_parts) + "</tbody>"

    return f'<table class="fact-matrix">{thead}{tbody}</table>'


def render_misreading(mr):
    return f"""
<dl class="misreading">
  <dt>常见误读</dt>
  <dd>{esc(mr.get('common_misread', ''))}</dd>
  <dt>为什么会被误读</dt>
  <dd>{esc(mr.get('why_misread', ''))}</dd>
  <dt>原书实际</dt>
  <dd>{esc(mr.get('actual', ''))}</dd>
</dl>
"""


def render_blindspot(bs):
    return f"""
<dl class="blindspot">
  <dt>局限</dt>
  <dd>{esc(bs.get('limitation', ''))}</dd>
  <dt>证据</dt>
  <dd>{esc(bs.get('evidence', ''))}</dd>
  <dt>边界提示</dt>
  <dd>{esc(bs.get('boundary', ''))}</dd>
</dl>
"""


def render_golden_quote(q):
    if isinstance(q, dict):
        text = esc(q.get("text", ""))
        source = esc(q.get("source", ""))
        source_html = f'<span class="golden-quote-source">{source}</span>' if source else ''
        return f'<p class="golden-quote">{text}{source_html}</p>'
    return f'<p class="golden-quote">{esc(q)}</p>'


def render_thought_coordinates(tc):
    mapping = {
        "同题延伸": "同题延伸",
        "对立视角": "对立视角",
        "承继关系": "承继关系",
        "现代回响": "现代回响",
    }
    parts = []
    for k_cn in mapping:
        items = tc.get(k_cn, [])
        if not items:
            continue
        li = "".join(f"<li>{esc(i)}</li>" for i in items)
        parts.append(f'<div class="coord-card"><h6>{k_cn}</h6><ul>{li}</ul></div>')
    return "\n".join(parts)


def render_toolbox(toolbox):
    return "\n".join(f"<li>{esc(t)}</li>" for t in toolbox)


def simple_substitute(template, mapping):
    """非常简单的占位符替换。handles {{KEY}} and {{#COND}}...{{/COND}}."""
    # 先处理条件块
    def cond_sub(m):
        key = m.group(1)
        content = m.group(2)
        value = mapping.get(key, "")
        return content if value else ""

    template = re.sub(r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}', cond_sub, template, flags=re.DOTALL)

    # 再处理普通占位符
    for k, v in mapping.items():
        template = template.replace("{{" + k + "}}", str(v) if v is not None else "")

    return template


def render(distill):
    """主渲染入口。"""
    meta = distill.get("meta", {})
    title = meta.get("title", "未命名")
    author = meta.get("author", "")
    motif = meta.get("motif", "")
    source_mix = meta.get("source_mix", {})
    lens = meta.get("lens", "balanced")
    lens_reason = meta.get("lens_reason", "")

    lens_note = ""
    if lens != "balanced" and lens_reason:
        lens_note = f"本次产出视角：<strong>{esc(lens)}</strong>。{esc(lens_reason)}"

    memory_hook = distill.get("memory_hook", "")
    overview_svg = normalize_svg(distill.get("overview_svg", ""))
    fact_matrix = distill.get("fact_matrix", {})
    fact_matrix_svg = normalize_svg(fact_matrix.get("viz_svg", "") if isinstance(fact_matrix, dict) else "")
    fact_matrix_table = render_fact_matrix_table(fact_matrix) if isinstance(fact_matrix, dict) else ""

    modules_html = "\n".join(render_module(m, i) for i, m in enumerate(distill.get("modules", [])))
    misreadings_html = "\n".join(render_misreading(mr) for mr in distill.get("misreadings", []))
    blindspots_html = "\n".join(render_blindspot(bs) for bs in distill.get("blindspots", []))

    golden_quotes = distill.get("golden_quotes", [])
    golden_quotes_html = "\n".join(render_golden_quote(q) for q in golden_quotes)

    thought_coordinates_html = render_thought_coordinates(distill.get("thought_coordinates", {}))
    toolbox_html = render_toolbox(distill.get("toolbox", []))

    source_meta_html = render_source_meta(source_mix)

    template_path = Path(__file__).parent.parent / "assets" / "template.html"
    template = template_path.read_text(encoding="utf-8")

    mapping = {
        "TITLE": esc(title),
        "AUTHOR": esc(author),
        "MOTIF": esc(motif),
        "MEMORY_HOOK": esc(memory_hook),
        "SOURCE_META_HTML": source_meta_html,
        "LENS_NOTE": lens_note,
        "OVERVIEW_SVG": overview_svg,
        "FACT_MATRIX_SVG": fact_matrix_svg,
        "FACT_MATRIX_TABLE": fact_matrix_table,
        "MODULES_HTML": modules_html,
        "GOLDEN_QUOTES_HTML": golden_quotes_html,
        "MISREADINGS_HTML": misreadings_html,
        "BLINDSPOTS_HTML": blindspots_html,
        "THOUGHT_COORDINATES_HTML": thought_coordinates_html,
        "TOOLBOX_HTML": toolbox_html,
    }

    return simple_substitute(template, mapping)


def main():
    if len(sys.argv) < 3:
        print("Usage: render.py <distill.json> <output.html>", file=sys.stderr)
        sys.exit(1)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    with in_path.open(encoding="utf-8") as f:
        distill = json.load(f)

    html_content = render(distill)
    out_path.write_text(html_content, encoding="utf-8")
    print(f"✓ 已生成: {out_path}")


if __name__ == "__main__":
    main()
