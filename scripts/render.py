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


def escape_html(s):
    """alias of esc()，对外暴露的 HTML 转义助手。"""
    return esc(s)


def load_svg_template(viz_type):
    """从 assets/svg-templates/<viz_type>.svg 读取 SVG 模板。
    返回原始 SVG 文本；若文件不存在返回空串。
    支持类型：timeline / network / evolution / spectrum。"""
    if not viz_type:
        return ""
    tpl_dir = Path(__file__).parent.parent / "assets" / "svg-templates"
    tpl_path = tpl_dir / f"{viz_type}.svg"
    if not tpl_path.exists():
        return ""
    return tpl_path.read_text(encoding="utf-8")


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


def paragraphize(text):
    """v2.2 · 把长段中文文本切成 <p> 段。

    启发式分段规则（按强度从高到低）：
    1. 显式 \\n\\n 段间距 → 直接切
    2. 「第一组事实，」「第一层，」「第二组事实，」等组别小标题 → subhead + body
    3. 「其一，」「其二，」「其三，」「其一：」 → 切段
    4. 长句以「。」结束且后有「{典型起句}」 → 切段
    """
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()

    # Step 1: 显式 \n\n 段
    if "\n\n" in text:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return "\n".join(_render_paragraph(p) for p in paragraphs)

    # Step 2: 识别组别小标题（第N组事实/第N层/第N组）
    pattern_groups = re.compile(
        r'(?=第[一二三四五六七八九十]+(?:组事实|层|组|个层次|阶段|个模式|种模式)[，、,])'
    )
    if len(pattern_groups.findall(text)) >= 2:
        parts = pattern_groups.split(text)
        return "\n".join(_render_paragraph(p.strip()) for p in parts if p.strip())

    # Step 3: 识别 其一/其二 等
    pattern_qiyi = re.compile(r'(?=其[一二三四五六七八九十]+[，、：])')
    if len(pattern_qiyi.findall(text)) >= 2:
        parts = pattern_qiyi.split(text)
        return "\n".join(_render_paragraph(p.strip()) for p in parts if p.strip())

    # Step 4: 长文本按句号 + 起句切（避免单段超过 ~500 字）
    if len(text) > 600:
        # 切句然后按累计长度成段
        sentences = re.split(r'(?<=[。！？])', text)
        paragraphs = []
        cur = ""
        for s in sentences:
            cur += s
            if len(cur) >= 350:
                paragraphs.append(cur.strip())
                cur = ""
        if cur.strip():
            paragraphs.append(cur.strip())
        if len(paragraphs) >= 2:
            return "\n".join(_render_paragraph(p) for p in paragraphs)

    # 短或单段：直接 <p> 包一下
    return _render_paragraph(text)


_SUBHEAD_PATTERN = re.compile(
    r'^(第[一二三四五六七八九十]+(?:组事实|层|组|个层次|阶段|个模式|种模式|回|条|步)[，、])'
)
_QIYI_PATTERN = re.compile(r'^(其[一二三四五六七八九十]+[，、：])')


def _render_paragraph(p):
    """单段 <p> 渲染。识别开头的小标题加 <strong class="para-subhead">。"""
    if not p:
        return ""
    m = _SUBHEAD_PATTERN.match(p)
    if m:
        head = m.group(1)
        body = p[m.end():].lstrip()
        return f'<p><strong class="para-subhead">{esc(head)}</strong>{_highlight_keywords(body)}</p>'
    m = _QIYI_PATTERN.match(p)
    if m:
        head = m.group(1)
        body = p[m.end():].lstrip()
        return f'<p><strong class="para-qiyi">{esc(head)}</strong>{_highlight_keywords(body)}</p>'
    return f'<p>{_highlight_keywords(p)}</p>'


# v2.2 · 关键词自动加重（限于元论述层标记词，不滥用）
_KEYWORD_PATTERNS = [
    # 命题/结论标记词
    re.compile(r'(总钥匙|总宣告|总命题|总曲|总图)'),
    re.compile(r'(临界点|拐点|分水岭|转折点)'),
    re.compile(r'(反证|反讽|反向献祭|镜像|对位)'),
    re.compile(r'(精准命名|精确预告|核心命题|内在悖论|结构性宿命)'),
    # 命运 / 关键事件名
    re.compile(r'([「『][^「」『』\n]{2,12}[」』])'),  # 引号内的关键短语 2-12 字
]


def _highlight_keywords(text):
    """把元论述标记词与关键短语加 <strong>，但避免重复包装。"""
    safe = esc(text)
    # 已经被 esc 后的 &lt;...&gt; 不会与下面的 <strong> 冲突
    for pat in _KEYWORD_PATTERNS:
        safe = pat.sub(lambda m: f'<strong class="kw">{m.group(1)}</strong>', safe)
    return safe


def render_derivation_chain(chain):
    """v2.2 · 渲染推导链为有视觉层级的步骤列表。"""
    if not chain or not isinstance(chain, list):
        return ""
    items = []
    for i, step in enumerate(chain, 1):
        if not isinstance(step, dict):
            continue
        step_n = step.get("step", i)
        type_ = step.get("type", "")
        content = step.get("content", "")
        type_label_map = {
            "fact": "事实", "mechanism": "机制", "analogy": "类比",
            "counterfact": "反证", "synthesis": "综合", "claim": "结论",
            "refutation": "反驳"
        }
        type_label = type_label_map.get(type_, type_)
        items.append(
            f'<li class="chain-step">'
            f'<span class="chain-num">{step_n}</span>'
            f'<span class="chain-type">{esc(type_label)}</span>'
            f'<span class="chain-body">{_highlight_keywords(content)}</span>'
            f'</li>'
        )
    if not items:
        return ""
    return f'<ol class="derivation-chain">{"".join(items)}</ol>'


def _render_long_field(field):
    """渲染 v2.2 长字段：支持三种格式。
    - str → paragraphize
    - {paragraphs: [str, ...]} → 直接段渲染
    - {subhead: str, body: str|list} → 小标题+正文段
    - list[dict] → 多个 subhead-body 块
    """
    if not field:
        return ""
    if isinstance(field, str):
        return paragraphize(field)
    if isinstance(field, list):
        return "\n".join(_render_long_field(item) for item in field)
    if isinstance(field, dict):
        if "paragraphs" in field:
            return "\n".join(_render_paragraph(p) for p in field["paragraphs"])
        if "subhead" in field:
            head = field.get("subhead", "")
            body = field.get("body", "")
            head_html = f'<h6 class="layer-subhead">{esc(head)}</h6>' if head else ""
            body_html = _render_long_field(body)
            return f'{head_html}{body_html}'
        # 兜底：当作普通 dict 序列化
        return paragraphize(json.dumps(field, ensure_ascii=False))
    return ""


def render_module(m, idx):
    """渲染单个内容模块（三重结构 + 对照 + 他山之石） v2.2 加重点+分段排版。"""
    title = esc(m.get("title", "未命名模块"))

    # 三重结构
    facts = m.get("facts_layer", {})
    mech = m.get("mechanism_layer", {})
    view = m.get("viewpoint_layer", {})

    facts_html = ""
    if isinstance(facts, dict):
        systematized = facts.get("systematized_facts", "")
        facts_html = _render_long_field(systematized)
    elif isinstance(facts, str):
        facts_html = paragraphize(facts)

    mech_html = ""
    if isinstance(mech, dict):
        patterns = mech.get("single_dim_patterns", [])
        weaving = mech.get("cross_dim_weaving", "")
        if patterns:
            patterns_list = "".join(
                f'<li>{_highlight_keywords(p) if isinstance(p, str) else esc(json.dumps(p, ensure_ascii=False))}</li>'
                for p in patterns
            )
            mech_html += (
                f'<div class="mech-block">'
                f'<h6 class="layer-subhead">单维度规律</h6>'
                f'<ul class="patterns-list">{patterns_list}</ul>'
                f'</div>'
            )
        if weaving:
            mech_html += (
                f'<div class="mech-block">'
                f'<h6 class="layer-subhead">跨维度交织</h6>'
                f'{_render_long_field(weaving)}'
                f'</div>'
            )
    elif isinstance(mech, str):
        mech_html = paragraphize(mech)

    view_html = ""
    if isinstance(view, dict):
        claim = view.get("core_claim", "")
        chain = view.get("derivation_chain", [])
        transfer = view.get("modern_transfer", "")
        caveats = view.get("caveats", "")
        if claim:
            view_html += (
                f'<div class="view-block view-claim">'
                f'<h6 class="layer-subhead">核心判断</h6>'
                f'<p class="claim-line">{_highlight_keywords(claim)}</p>'
                f'</div>'
            )
        if chain:
            chain_html = render_derivation_chain(chain)
            if chain_html:
                view_html += (
                    f'<div class="view-block view-chain">'
                    f'<h6 class="layer-subhead">推导链</h6>'
                    f'{chain_html}'
                    f'</div>'
                )
        if transfer:
            view_html += (
                f'<div class="view-block view-transfer">'
                f'<h6 class="layer-subhead">现代迁移</h6>'
                f'{_render_long_field(transfer)}'
                f'</div>'
            )
        if caveats:
            view_html += (
                f'<div class="view-block view-caveat">'
                f'<h6 class="layer-subhead">边界</h6>'
                f'{_render_long_field(caveats)}'
                f'</div>'
            )
    elif isinstance(view, str):
        view_html = paragraphize(view)

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
    """把 fact_matrix.cells 渲染成表格（如果没有 SVG 就用表格）。

    支持两种 cells 结构：
    - dict 形式: {"行×列": "内容", ...}  (v1 风格)
    - list of dicts 形式: [{"row":..., "col":..., "content":..., "anchor":...}, ...]  (v2 风格)
    """
    if not fm:
        return ""
    cells = fm.get("cells", {})
    if not cells:
        return ""

    rows = {}
    cols = set()

    if isinstance(cells, list):
        # v2 list-of-dicts 形式
        for cell in cells:
            if not isinstance(cell, dict):
                continue
            row_k = str(cell.get("row", "")).strip()
            col_k = str(cell.get("col", "")).strip()
            if not row_k or not col_k:
                continue
            content = cell.get("content", "")
            anchor = cell.get("anchor", "")
            val = f"{content}（{anchor}）" if anchor else content
            cols.add(col_k)
            rows.setdefault(row_k, {})[col_k] = val
    elif isinstance(cells, dict):
        # v1 dict 形式
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
    """金句渲染。兼容三种字段格式：
    - 字符串：直接当 text
    - {text, source}：旧 v1 格式
    - {quote, chapter, context_brief}：v2.1 标准格式
    """
    if isinstance(q, dict):
        # v2.1 字段优先，回落到 v1
        text = q.get("quote") or q.get("text") or ""
        chapter = q.get("chapter") or ""
        context = q.get("context_brief") or ""
        source = q.get("source") or ""
        # 显示：正文 + 出处（chapter）+ 上下文小字（context_brief）
        out = f'<p class="golden-quote-text">{esc(text)}</p>'
        meta_parts = []
        if chapter:
            meta_parts.append(f'<span class="gq-chapter">{esc(chapter)}</span>')
        if source:
            meta_parts.append(f'<span class="gq-source">{esc(source)}</span>')
        if meta_parts:
            out += f'<p class="gq-meta">{" · ".join(meta_parts)}</p>'
        if context:
            out += f'<p class="gq-context">{esc(context)}</p>'
        return f'<figure class="golden-quote">{out}</figure>'
    return f'<figure class="golden-quote"><p class="golden-quote-text">{esc(q)}</p></figure>'


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


# ==========================================================================
# v2 · §2 · 5 个新模块的渲染函数
# 每个函数对应 template.html 的一个占位符；空数据 → 返回空串（让 :empty CSS 隐藏）
# ==========================================================================


_APD_FACET_META = {
    "class":       {"label": "阶级立场", "key": "class_position"},
    "knowledge":   {"label": "知识边界", "key": "knowledge_boundary"},
    "motive":      {"label": "动机暗影", "key": "writing_motive_shadow"},
}
_APD_FACET_ORDER = ["class", "knowledge", "motive"]


def render_author_position(apd):
    """v2.2 填充 {{AUTHOR_POSITION_HTML}} · §2.3 作者立场解构。

    新版结构：三个 facet 各自一张「立场卡」，含
      - 顶部 facet 名（阶级立场 / 知识边界 / 动机暗影）
      - 中部一句话浓缩（class_position / knowledge_boundary / writing_motive_shadow）
      - 底部该 facet 下的 evidence 列表（按 facet 字段自动归组）
    三卡水平排列（响应式收单列）。
    """
    if not apd or not isinstance(apd, dict):
        return ""

    summaries = {f: esc(apd.get(_APD_FACET_META[f]["key"], "") or "") for f in _APD_FACET_ORDER}
    evidence = apd.get("evidence", []) or []

    # 按 facet 归组 evidence
    grouped = {f: [] for f in _APD_FACET_ORDER}
    orphan = []  # facet 字段缺失或不识别的兜底
    for ev in evidence:
        if not isinstance(ev, dict):
            continue
        f = (ev.get("facet") or "").strip().lower()
        if f in grouped:
            grouped[f].append(ev)
        else:
            orphan.append(ev)

    if not (any(summaries.values()) or any(grouped.values()) or orphan):
        return ""

    cards = []
    for f in _APD_FACET_ORDER:
        label = _APD_FACET_META[f]["label"]
        summary = summaries[f]
        items = grouped[f]
        if not (summary or items):
            continue
        ev_html = ""
        if items:
            ev_lis = []
            for ev in items:
                anchor = esc(ev.get("anchor", "") or "")
                elab = esc(ev.get("elaboration", "") or "")
                ev_lis.append(
                    f'<li class="apd-ev-item">'
                    f'<div class="apd-ev-anchor">{anchor}</div>'
                    f'<div class="apd-ev-elab">{elab}</div>'
                    f'</li>'
                )
            ev_html = (
                f'<ul class="apd-ev-list">{"".join(ev_lis)}</ul>'
            )
        cards.append(
            f'<article class="apd-card apd-{f}">'
            f'<header class="apd-card-head">'
            f'<span class="apd-facet-tag">{esc(label)}</span>'
            f'</header>'
            + (f'<p class="apd-summary">{summary}</p>' if summary else '')
            + (f'<div class="apd-evidence-block">'
               f'<h6 class="apd-ev-title">证据 · {len(items)} 条</h6>'
               f'{ev_html}</div>' if ev_html else '')
            + '</article>'
        )

    out = '<div class="apd-grid">' + "".join(cards) + '</div>' if cards else ''

    # 处理孤立 evidence（facet 字段未识别）
    if orphan:
        orphan_lis = []
        for ev in orphan:
            facet = esc(ev.get("facet", "—") or "—")
            anchor = esc(ev.get("anchor", "") or "")
            elab = esc(ev.get("elaboration", "") or "")
            orphan_lis.append(
                f'<li class="apd-ev-item">'
                f'<span class="apd-facet-tag inline">{facet}</span>'
                f'<div class="apd-ev-anchor">{anchor}</div>'
                f'<div class="apd-ev-elab">{elab}</div>'
                f'</li>'
            )
        out += (
            f'<div class="apd-orphan">'
            f'<h6 class="apd-ev-title">未归类证据</h6>'
            f'<ul class="apd-ev-list">{"".join(orphan_lis)}</ul>'
            f'</div>'
        )

    return out


def render_schools_of_interpretation(schools):
    """填充 {{SCHOOLS_OF_INTERPRETATION_HTML}} · §2.1 学派论争。

    渲染学派卡片数组：每张含派名、核心立场、代表人物、关键证据、我们的判断。
    空数组 → 返回空串。"""
    if not schools or not isinstance(schools, list):
        return ""
    cards = []
    for s in schools:
        if not isinstance(s, dict):
            continue
        name = esc(s.get("school", ""))
        core = esc(s.get("core_position", ""))
        figures = s.get("key_figures", []) or []
        figs_html = "、".join(esc(f) for f in figures) if figures else ""
        anchors = s.get("evidence_anchors", []) or []
        anc_items = "".join(
            f'<li><strong>{esc(a.get("source",""))}</strong>：{esc(a.get("summary",""))}</li>'
            for a in anchors if isinstance(a, dict)
        )
        anc_html = f'<ul class="school-anchors">{anc_items}</ul>' if anc_items else ""
        judg = esc(s.get("our_judgment", ""))
        cards.append(
            f'<div class="school-card">'
            f'<h6>{name}</h6>'
            f'<p class="school-core">{core}</p>'
            + (f'<p class="school-figures"><em>代表人物：</em>{figs_html}</p>' if figs_html else "")
            + anc_html
            + (f'<p class="school-judgment"><em>我们的判断：</em>{judg}</p>' if judg else "")
            + '</div>'
        )
    return "\n".join(cards)


def render_version_variants(variants):
    """填充 {{VERSION_VARIANTS_HTML}} · §2.2 版本/译本差异。

    渲染对照行：版本 A vs 版本 B / 差异位置 / 内容 / 解读意义。
    空数组 → 返回空串。"""
    if not variants or not isinstance(variants, list):
        return ""
    rows = []
    for v in variants:
        if not isinstance(v, dict):
            continue
        a = esc(v.get("version_a", ""))
        b = esc(v.get("version_b", ""))
        locus = esc(v.get("diff_locus", ""))
        content = esc(v.get("diff_content", ""))
        sig = esc(v.get("interpretive_significance", ""))
        rows.append(
            f'<div class="variant-row">'
            f'<div class="variant-head"><span class="ver-a">{a}</span>'
            f'<span class="ver-vs">vs</span><span class="ver-b">{b}</span></div>'
            f'<p><em>差异位置：</em>{locus}</p>'
            f'<p><em>差异内容：</em>{content}</p>'
            f'<p><em>解读意义：</em>{sig}</p>'
            f'</div>'
        )
    return "\n".join(rows)


def render_chapter_level_notes(notes):
    """填充 {{CHAPTER_LEVEL_NOTES_HTML}} · §2.4 章节级覆盖。

    渲染编号列表：章/回名 + 关键事件 + 解读 + 跨章呼应。
    空数组 → 返回空串。"""
    if not notes or not isinstance(notes, list):
        return ""
    items = []
    for i, n in enumerate(notes, 1):
        if not isinstance(n, dict):
            continue
        ch = esc(n.get("chapter", ""))
        anc = esc(n.get("anchor_event", ""))
        interp = esc(n.get("interpretation", ""))
        cross = esc(n.get("cross_link", ""))
        cross_html = f'<p class="chapter-cross"><em>呼应：</em>{cross}</p>' if cross else ""
        items.append(
            f'<li class="chapter-note">'
            f'<h6><span class="chapter-idx">{i:02d}</span>{ch}</h6>'
            f'<p class="chapter-anchor"><em>关键事件：</em>{anc}</p>'
            f'<p class="chapter-interp">{interp}</p>'
            f'{cross_html}'
            f'</li>'
        )
    return f'<ol class="chapter-notes-list">{"".join(items)}</ol>' if items else ""


def render_thought_coordinates_extended(tc):
    """填充 {{THOUGHT_COORDINATES_EXTENDED_HTML}} · §2.5 强化版四列。

    四列：同题延伸 / 对立视角 / 承继关系 / 现代回响；
    每条结构化（referenced_work / referenced_author / position / relation_to_book）。
    若所有列都是字符串列表（v1 兼容） → 返回空串，由旧 coord-grid 走原渲染。

    精读模式（mode-focus）只展示每维第一条作为索引；深读模式（mode-deep）展开全部。"""
    if not tc or not isinstance(tc, dict):
        return ""
    dims = ["同题延伸", "对立视角", "承继关系", "现代回响"]
    has_structured = any(
        isinstance(it, dict)
        for d in dims
        for it in (tc.get(d, []) or [])
    )
    if not has_structured:
        return ""

    def render_li(it):
        if isinstance(it, dict):
            w = esc(it.get("referenced_work", ""))
            au = esc(it.get("referenced_author", ""))
            pos = esc(it.get("position", ""))
            rel = esc(it.get("relation_to_book", ""))
            head = f"《{w}》" + (f" · {au}" if au else "")
            return (
                f'<li><strong>{head}</strong>'
                + (f'<br/><span class="tc-pos">{pos}</span>' if pos else "")
                + (f'<br/><span class="tc-rel"><em>与本书：</em>{rel}</span>' if rel else "")
                + '</li>'
            )
        return f"<li>{esc(it)}</li>"

    cols_focus = []  # 精读简版：每维第 1 条
    cols_deep = []   # 深读完整：每维剩余条目
    for d in dims:
        items = tc.get(d, []) or []
        if not items:
            continue
        first_li = render_li(items[0])
        cols_focus.append(
            f'<div class="tc-col"><h6>{d}</h6>'
            f'<ul>{first_li}</ul></div>'
        )
        rest = items[1:]
        if rest:
            rest_lis = "".join(render_li(it) for it in rest)
            cols_deep.append(
                f'<div class="tc-col"><h6>{d} · 深读续</h6>'
                f'<ul>{rest_lis}</ul></div>'
            )
    parts = []
    if cols_focus:
        parts.append(
            f'<div class="tc-grid-4col tc-focus level-精读 mode-focus">{"".join(cols_focus)}</div>'
        )
    if cols_deep:
        parts.append(
            f'<div class="tc-grid-4col tc-deep level-深读 mode-deep">{"".join(cols_deep)}</div>'
        )
    return "".join(parts)


# ==========================================================================
# v2.1 · §2.6 / §2.7 / §2.8 · 三个新模块（场景细读 / 人物小传 / 诗词专题）
# 每个函数对应 template.html 的占位符；空数据 → 返回空串（让 :empty CSS 隐藏）
# ==========================================================================


def render_scene_dissections(scenes):
    """填充 {{SCENE_DISSECTIONS_HTML}} · §2.6 场景细读。

    每个场景：标题 + 定位 + 原文摘录 + 五层拆解（blocking/language/sensorium/
    subtext/structural_function）+ 关键短语近读 + 全书呼应。
    空列表/None → 返回空串（graceful degradation）。"""
    if not scenes or not isinstance(scenes, list):
        return ""
    cards = []
    layer_labels = [
        ("blocking", "调度"),
        ("language", "语言层"),
        ("sensorium", "感官层"),
        ("subtext", "潜文本"),
        ("structural_function", "结构功能"),
    ]
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        title = esc(sc.get("scene_title", ""))
        locus = esc(sc.get("scene_locus", ""))
        excerpt = esc(sc.get("original_text_excerpt", ""))

        layers = sc.get("dissection_layers", {}) or {}
        layer_items = []
        for key, cn in layer_labels:
            val = layers.get(key, "") if isinstance(layers, dict) else ""
            if not val:
                continue
            layer_items.append(
                f'<li class="scene-layer">'
                f'<span class="layer-name">{cn}</span>{esc(val)}'
                f'</li>'
            )
        layers_html = (
            f'<ol class="scene-layers">{"".join(layer_items)}</ol>'
            if layer_items else ""
        )

        cr_items = []
        for cr in sc.get("key_close_reads", []) or []:
            if not isinstance(cr, dict):
                continue
            phrase = esc(cr.get("phrase", ""))
            reading = esc(cr.get("reading", ""))
            cr_items.append(
                f'<li><span class="cr-phrase">「{phrase}」</span>{reading}</li>'
            )
        cr_html = (
            f'<ol class="scene-closereads">{"".join(cr_items)}</ol>'
            if cr_items else ""
        )

        echoes = esc(sc.get("echoes", ""))
        echoes_html = f'<p class="scene-echoes">{echoes}</p>' if echoes else ""

        excerpt_html = f'<div class="scene-original">{excerpt}</div>' if excerpt else ""
        locus_html = f'<p class="scene-locus">{locus}</p>' if locus else ""

        cards.append(
            f'<div class="scene-card">'
            f'<h4 class="scene-title">{title}</h4>'
            f'{locus_html}'
            f'{excerpt_html}'
            f'{layers_html}'
            f'{cr_html}'
            f'{echoes_html}'
            f'</div>'
        )
    return "\n".join(cards)


def render_character_dossiers(characters):
    """填充 {{CHARACTER_DOSSIERS_HTML}} · §2.7 人物小传。

    每条小传：人名 + tier 徽章 + 出场轨迹 + 核心矛盾 + 关键场景列表 +
    语言印记 + 命运模式 + 母题视角解读（共 8 个字段）。
    空列表/None → 返回空串。"""
    if not characters or not isinstance(characters, list):
        return ""
    tier_map = {
        "primary": ("主要", "tier-primary"),
        "secondary": ("次要", "tier-secondary"),
        "minor_but_pivotal": ("枢纽配角", "tier-minor"),
    }
    blocks_def = [
        ("appearance_arc", "出场轨迹"),
        ("language_signature", "语言印记"),
        ("fate_pattern", "命运模式"),
        ("reading_through_lens", "母题视角"),
    ]
    cards = []
    for ch in characters:
        if not isinstance(ch, dict):
            continue
        name = esc(ch.get("name", ""))
        tier_raw = ch.get("tier", "")
        tier_cn, tier_cls = tier_map.get(
            tier_raw, (esc(tier_raw) if tier_raw else "", "")
        )
        tier_html = (
            f'<span class="tier-badge {tier_cls}">{tier_cn}</span>'
            if tier_cn else ""
        )

        paradox = esc(ch.get("core_paradox", ""))
        paradox_html = f'<p class="char-paradox">{paradox}</p>' if paradox else ""

        # 4 个长文本字段
        block_html_parts = []
        for key, cn in blocks_def:
            val = ch.get(key, "")
            if not val:
                continue
            block_html_parts.append(
                f'<div class="char-block">'
                f'<h6>{cn}</h6><p>{esc(val)}</p>'
                f'</div>'
            )

        # key_scenes 有序列表
        ks_items = []
        for ks in ch.get("key_scenes", []) or []:
            if not isinstance(ks, dict):
                continue
            scene = esc(ks.get("scene", ""))
            reveals = esc(ks.get("what_it_reveals", ""))
            ks_items.append(
                f'<li><span class="ks-scene">{scene}</span>{reveals}</li>'
            )
        ks_html = (
            f'<div class="char-block"><h6>关键场景</h6>'
            f'<ol class="char-keyscenes">{"".join(ks_items)}</ol></div>'
            if ks_items else ""
        )

        cards.append(
            f'<div class="character-card">'
            f'<div class="char-head">'
            f'<h3 class="char-name">{name}</h3>'
            f'{tier_html}'
            f'</div>'
            f'{paradox_html}'
            + (block_html_parts[0] if len(block_html_parts) > 0 else "")
            + ks_html
            + "".join(block_html_parts[1:])
            + '</div>'
        )
    return "\n".join(cards)


def render_poetics_dossiers(poems):
    """填充 {{POETICS_DOSSIERS_HTML}} · §2.8 诗词曲赋专题。

    每篇专题：篇名 + 出处 + 作者/声音 + 全文或节选（楷体竖式风格） +
    形式分析 + 内容分析 + 互文锚点列表 + 命运预告（如有）。
    空列表/None → 返回空串。"""
    if not poems or not isinstance(poems, list):
        return ""
    cards = []
    for p in poems:
        if not isinstance(p, dict):
            continue
        title = esc(p.get("title", ""))
        locus = esc(p.get("locus", ""))
        speaker = esc(p.get("speaker_or_voice", ""))
        text = esc(p.get("full_or_excerpt", ""))
        form = esc(p.get("form_analysis", ""))
        content_an = esc(p.get("content_analysis", ""))
        fate = esc(p.get("fate_foreshadowing", ""))

        head_parts = [f'<h4 class="poem-title">{title}</h4>']
        if locus:
            head_parts.append(f'<span class="poem-locus">{locus}</span>')
        if speaker:
            head_parts.append(f'<span class="poem-speaker">{speaker}</span>')
        head_html = f'<div class="poem-head">{"".join(head_parts)}</div>'

        text_html = f'<div class="poem-text">{text}</div>' if text else ""
        form_html = (
            f'<div class="poem-block"><h6>形式分析</h6><p>{form}</p></div>'
            if form else ""
        )
        content_html = (
            f'<div class="poem-block"><h6>内容分析</h6><p>{content_an}</p></div>'
            if content_an else ""
        )

        ix_items = []
        for ix in p.get("intertextual_anchors", []) or []:
            if not isinstance(ix, dict):
                continue
            refers = esc(ix.get("refers_to", ""))
            sig = esc(ix.get("significance", ""))
            ix_items.append(
                f'<li><span class="it-refers">{refers}</span>{sig}</li>'
            )
        ix_html = (
            f'<div class="poem-block"><h6>互文锚点</h6>'
            f'<ul class="poem-intertext">{"".join(ix_items)}</ul></div>'
            if ix_items else ""
        )

        fate_html = f'<p class="poem-fate">{fate}</p>' if fate else ""

        cards.append(
            f'<div class="poetics-card">'
            f'{head_html}'
            f'{text_html}'
            f'{form_html}'
            f'{content_html}'
            f'{ix_html}'
            f'{fate_html}'
            f'</div>'
        )
    return "\n".join(cards)


# ==========================================================================
# v2 · §1.17 · 第二可视化渲染（4 种类型）
# ==========================================================================


def _render_timeline_viz(data):
    """timeline · 节点 + 标签沿水平轴排列。
    data: {nodes: [{x_pct, label, year/chapter, key?}], labels?: [...]}"""
    nodes = data.get("nodes", []) or []
    if not nodes:
        return load_svg_template("timeline").replace("{{NODES}}", "").replace("{{LABELS}}", "")
    node_parts = []
    label_parts = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        x_pct = float(n.get("x_pct", 50))
        x = 60 + (x_pct / 100.0) * (740 - 60)
        is_key = bool(n.get("key", False))
        cls_node = "tl-node-key" if is_key else "tl-node"
        cls_label = "tl-label-key" if is_key else "tl-label"
        r = 7 if is_key else 5
        label = esc(n.get("label", ""))
        sub = esc(str(n.get("year", n.get("chapter", ""))))
        node_parts.append(f'<circle class="{cls_node}" cx="{x:.1f}" cy="100" r="{r}"/>')
        label_parts.append(
            f'<text class="{cls_label}" x="{x:.1f}" y="80">{label}</text>'
        )
        if sub:
            label_parts.append(
                f'<text class="tl-label" x="{x:.1f}" y="130">{sub}</text>'
            )
    svg = load_svg_template("timeline")
    svg = svg.replace("{{NODES}}", "\n  ".join(node_parts))
    svg = svg.replace("{{LABELS}}", "\n  ".join(label_parts))
    return svg


def _render_network_viz(data):
    """network · 圆 + 连线。
    data: {nodes: [{id, label, x_pct, y_pct, key?}], edges: [{from, to, key?}]}"""
    nodes = data.get("nodes", []) or []
    edges = data.get("edges", []) or []
    id_to_xy = {}
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid = n.get("id", "")
        x = (float(n.get("x_pct", 50)) / 100.0) * 600
        y = (float(n.get("y_pct", 50)) / 100.0) * 600
        id_to_xy[nid] = (x, y)

    edge_parts = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        a = id_to_xy.get(e.get("from"))
        b = id_to_xy.get(e.get("to"))
        if not a or not b:
            continue
        cls = "net-edge-key" if e.get("key") else "net-edge"
        edge_parts.append(
            f'<line class="{cls}" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>'
        )

    node_parts = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        nid = n.get("id", "")
        if nid not in id_to_xy:
            continue
        x, y = id_to_xy[nid]
        is_key = bool(n.get("key", False))
        cls_node = "net-node-key" if is_key else "net-node"
        cls_label = "net-label-key" if is_key else "net-label"
        r = 26 if is_key else 22
        label = esc(n.get("label", ""))
        node_parts.append(
            f'<g><circle class="{cls_node}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
            f'<text class="{cls_label}" x="{x:.1f}" y="{y:.1f}">{label}</text></g>'
        )

    svg = load_svg_template("network")
    svg = svg.replace("{{EDGES}}", "\n  ".join(edge_parts))
    svg = svg.replace("{{NODES}}", "\n  ".join(node_parts))
    return svg


def _render_evolution_viz(data):
    """evolution · 顶部根 + 向下分支。
    data: {root: {label}, branches: [{label, sub_branches: [str]}]}"""
    root = data.get("root", {}) or {}
    branches = data.get("branches", []) or []
    root_label = esc(root.get("label", ""))
    root_x, root_y = 400, 60
    root_html = (
        f'<circle class="ev-root-node" cx="{root_x}" cy="{root_y}" r="28"/>'
        f'<text class="ev-root-label" x="{root_x}" y="{root_y}">{root_label}</text>'
    )

    branch_parts = []
    n = max(len(branches), 1)
    span_left, span_right = 100, 700
    for i, br in enumerate(branches):
        if not isinstance(br, dict):
            continue
        bx = span_left + (span_right - span_left) * (i + 0.5) / n
        by = 230
        is_key = bool(br.get("key", False))
        line_cls = "ev-branch-key" if is_key else "ev-branch"
        # 主干曲线 (root → branch node)
        branch_parts.append(
            f'<path class="{line_cls}" d="M{root_x},{root_y+28} '
            f'C{root_x},{(root_y+by)/2} {bx},{(root_y+by)/2} {bx},{by-22}"/>'
        )
        branch_parts.append(
            f'<circle class="ev-leaf-node" cx="{bx:.1f}" cy="{by}" r="22"/>'
        )
        branch_parts.append(
            f'<text class="ev-leaf-label" x="{bx:.1f}" y="{by}">{esc(br.get("label",""))}</text>'
        )
        subs = br.get("sub_branches", []) or []
        m = max(len(subs), 1)
        for j, sub in enumerate(subs):
            sx = bx - 60 + 120 * (j + 0.5) / m
            sy = 380
            branch_parts.append(
                f'<path class="ev-branch" d="M{bx:.1f},{by+22} '
                f'C{bx:.1f},{(by+sy)/2} {sx:.1f},{(by+sy)/2} {sx:.1f},{sy-18}"/>'
            )
            branch_parts.append(
                f'<circle class="ev-leaf-node" cx="{sx:.1f}" cy="{sy}" r="18"/>'
            )
            branch_parts.append(
                f'<text class="ev-leaf-label" x="{sx:.1f}" y="{sy}">{esc(sub)}</text>'
            )

    svg = load_svg_template("evolution")
    svg = svg.replace("{{ROOT}}", root_html)
    svg = svg.replace("{{BRANCHES}}", "\n  ".join(branch_parts))
    return svg


def _render_spectrum_viz(data):
    """spectrum · 两端标签 + 立场点。
    data: {left_label, right_label, positions: [{label, x_pct, key?}]}"""
    left = esc(data.get("left_label", ""))
    right = esc(data.get("right_label", ""))
    positions = data.get("positions", []) or []
    parts = []
    # 错落 y 防止标签重叠
    y_choices = [150, 175, 90, 65]
    for i, p in enumerate(positions):
        if not isinstance(p, dict):
            continue
        x_pct = float(p.get("x_pct", 50))
        x = 80 + (x_pct / 100.0) * (720 - 80)
        is_key = bool(p.get("key", False))
        cls_node = "sp-pos-node-key" if is_key else "sp-pos-node"
        r = 7 if is_key else 5
        label_y = y_choices[i % len(y_choices)]
        # 连线从轴到标签上方
        parts.append(
            f'<line class="sp-tick" x1="{x:.1f}" y1="110" x2="{x:.1f}" y2="{label_y + (8 if label_y < 110 else -8)}" opacity="0.3"/>'
        )
        parts.append(f'<circle class="{cls_node}" cx="{x:.1f}" cy="110" r="{r}"/>')
        parts.append(
            f'<text class="sp-pos-label" x="{x:.1f}" y="{label_y}">{esc(p.get("label",""))}</text>'
        )
    svg = load_svg_template("spectrum")
    svg = svg.replace("{{LEFT_LABEL}}", left)
    svg = svg.replace("{{RIGHT_LABEL}}", right)
    svg = svg.replace("{{POSITIONS}}", "\n  ".join(parts))
    return svg


_SECONDARY_VIZ_DISPATCH = {
    "timeline": _render_timeline_viz,
    "network": _render_network_viz,
    "evolution": _render_evolution_viz,
    "spectrum": _render_spectrum_viz,
}


def render_secondary_viz(spec):
    """填充 {{SECONDARY_VIZ_SVG}} · §1.17 第二可视化。

    spec 可以是：
    - dict {viz_type, data} — 单个可视化（v2 兼容）
    - list of dicts — 多个可视化串联（v2.1 加深，达 §1.17 ≥3 种）
    返回 (svg_html_str, viz_type_summary_str)。"""
    if not spec:
        return "", ""

    # v2.1 多 viz: list of dicts
    if isinstance(spec, list):
        parts = []
        types = []
        for item in spec:
            if not isinstance(item, dict):
                continue
            vt = item.get("viz_type", "")
            data = item.get("data", {}) or {}
            fn = _SECONDARY_VIZ_DISPATCH.get(vt)
            if not fn:
                continue
            try:
                svg = normalize_svg(fn(data))
            except Exception:
                continue
            if not svg:
                continue
            # 包成带 data-viz-type 的 div，让 visual_check 能识别每个 SVG 的类型
            parts.append(
                f'<div class="viz-secondary-item" data-viz-type="{esc(vt)}" '
                f'style="margin: 1.6em 0;">{svg}</div>'
            )
            types.append(vt)
        if not parts:
            return "", ""
        return "\n".join(parts), " + ".join(types)

    # v2 兼容: 单 dict
    if not isinstance(spec, dict):
        return "", ""
    vt = spec.get("viz_type", "")
    data = spec.get("data", {}) or {}
    fn = _SECONDARY_VIZ_DISPATCH.get(vt)
    if not fn:
        return "", ""
    try:
        svg = fn(data)
    except Exception:
        return "", ""
    return normalize_svg(svg), vt


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

    thought_coordinates_raw = distill.get("thought_coordinates", {}) or {}
    thought_coordinates_html = render_thought_coordinates(thought_coordinates_raw)
    thought_coordinates_extended_html = render_thought_coordinates_extended(thought_coordinates_raw)
    # 若结构化扩展版渲染出来，则旧网格不再重复展示
    if thought_coordinates_extended_html:
        thought_coordinates_html = ""

    toolbox_html = render_toolbox(distill.get("toolbox", []))

    source_meta_html = render_source_meta(source_mix)

    # v2 · 5 个新模块
    author_position_html = render_author_position(distill.get("author_position_deconstruction", {}))
    schools_html = render_schools_of_interpretation(distill.get("schools_of_interpretation", []))
    version_variants_html = render_version_variants(distill.get("version_variants", []))
    chapter_level_notes_html = render_chapter_level_notes(distill.get("chapter_level_notes", []))

    # v2.1 · 3 个新模块（§2.6 / §2.7 / §2.8）
    scene_dissections_html = render_scene_dissections(distill.get("scene_dissections", []))
    character_dossiers_html = render_character_dossiers(distill.get("character_dossiers", []))
    poetics_dossiers_html = render_poetics_dossiers(distill.get("poetics_dossiers", []))

    # v2 · §1.17 第二可视化（兼容两种位置：顶层 secondary_viz 或 fact_matrix.secondary_viz）
    secondary_viz_spec = distill.get("secondary_viz") or (
        fact_matrix.get("secondary_viz") if isinstance(fact_matrix, dict) else None
    )
    secondary_viz_svg, secondary_viz_type = render_secondary_viz(secondary_viz_spec)

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
        "SECONDARY_VIZ_SVG": secondary_viz_svg,
        "SECONDARY_VIZ_TYPE": secondary_viz_type,
        "MODULES_HTML": modules_html,
        "AUTHOR_POSITION_HTML": author_position_html,
        "GOLDEN_QUOTES_HTML": golden_quotes_html,
        "MISREADINGS_HTML": misreadings_html,
        "BLINDSPOTS_HTML": blindspots_html,
        "SCHOOLS_OF_INTERPRETATION_HTML": schools_html,
        "VERSION_VARIANTS_HTML": version_variants_html,
        "CHAPTER_LEVEL_NOTES_HTML": chapter_level_notes_html,
        "SCENE_DISSECTIONS_HTML": scene_dissections_html,
        "CHARACTER_DOSSIERS_HTML": character_dossiers_html,
        "POETICS_DOSSIERS_HTML": poetics_dossiers_html,
        "THOUGHT_COORDINATES_EXTENDED_HTML": thought_coordinates_extended_html,
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
