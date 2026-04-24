#!/usr/bin/env python3
"""
fetch_sources.py — 多源抓取 + 信源分级

使用：
    python scripts/fetch_sources.py "书名" [作者]

功能：
1. 尝试从公版渠道获取原文（ctext / Wikisource / archive.org / Project Gutenberg）
2. 失败则标记 "need_user_upload"
3. 同时抓权威解读（豆瓣书页、学术摘要）
4. 输出 JSON 格式的 sources 清单

注意：
- 本脚本只做 URL 拼接和标记，实际 HTTP 抓取由 Claude 的 WebFetch 完成
- 脚本帮忙生成要抓的 URL 列表 + 分级标签
- 不碰 paywall / 不绕 DRM
"""

import json
import sys
import urllib.parse


PUBLIC_DOMAIN_CLASSIC_CN = {
    # 中文公版书的首选站点
    "ctext": "https://ctext.org/zhs?searchu={q}",
    "gushiwen": "https://so.gushiwen.cn/search.aspx?value={q}",
    "wikisource_zh": "https://zh.wikisource.org/wiki/{q}",
}

PUBLIC_DOMAIN_EN = {
    "gutenberg": "https://www.gutenberg.org/ebooks/search/?query={q}",
    "archive": "https://archive.org/search.php?query={q}",
    "wikisource_en": "https://en.wikisource.org/wiki/{q}",
}

COMMENTARY_SOURCES = {
    "douban_book": "https://book.douban.com/subject_search?search_text={q}",
    "douban_reviews": "https://book.douban.com/subject_search?search_text={q}&cat=1002",
    "zhihu": "https://www.zhihu.com/search?q={q}&type=content",
    "wikipedia_zh": "https://zh.wikipedia.org/wiki/Special:Search?search={q}",
    "wikipedia_en": "https://en.wikipedia.org/wiki/Special:Search?search={q}",
    "google_scholar": "https://scholar.google.com/scholar?q={q}",
}


def is_likely_chinese(s):
    for ch in s:
        if "一" <= ch <= "鿿":
            return True
    return False


def build_fetch_plan(title, author=""):
    """给定书名和作者，返回一个抓取计划。"""
    q = urllib.parse.quote(title)
    q_plus = urllib.parse.quote(f"{title} {author}".strip())

    plan = {
        "title": title,
        "author": author,
        "attempts": []
    }

    # 优先级 1：原书（A 级候选）
    if is_likely_chinese(title):
        for name, url in PUBLIC_DOMAIN_CLASSIC_CN.items():
            plan["attempts"].append({
                "level": "A_candidate",
                "source": name,
                "url": url.format(q=q),
                "note": "公版中文古籍尝试点",
            })
    for name, url in PUBLIC_DOMAIN_EN.items():
        plan["attempts"].append({
            "level": "A_candidate",
            "source": name,
            "url": url.format(q=q),
            "note": "英文公版尝试点",
        })

    # 优先级 2：用户上传的占位提示
    plan["attempts"].append({
        "level": "A_fallback",
        "source": "user_upload",
        "url": None,
        "note": "以上都失败则请用户上传原文",
    })

    # 副线：解读/评论（B/C 级）
    for name, url in COMMENTARY_SOURCES.items():
        level = "B_candidate" if "scholar" in name or "wikipedia" in name else "C_candidate"
        plan["attempts"].append({
            "level": level,
            "source": name,
            "url": url.format(q=q_plus),
            "note": "权威解读/评论",
        })

    return plan


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_sources.py \"书名\" [作者]", file=sys.stderr)
        sys.exit(1)

    title = sys.argv[1]
    author = sys.argv[2] if len(sys.argv) > 2 else ""

    plan = build_fetch_plan(title, author)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print("\n# 使用说明:", file=sys.stderr)
    print("# 1. 用 WebFetch 工具按优先级顺序尝试 A_candidate 的 url", file=sys.stderr)
    print("# 2. 如果都失败, 请用户上传原文或使用 C_candidate 做二手资料", file=sys.stderr)
    print("# 3. 同时抓 B_candidate/C_candidate 作为他山之石素材", file=sys.stderr)


if __name__ == "__main__":
    main()
